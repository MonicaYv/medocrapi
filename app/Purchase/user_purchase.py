from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_mongo_db
from datetime import datetime
from app.database import get_db
from app.profile.user_auth import get_current_user_object
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/purchase",
    tags=["purchase"]
)


# Search Medicines (also logs search history)
@router.get("/search", response_model=List[dict])
async def search_medicine(
    name: str = Query(..., description="Search medicine by name"),
    limit: int = Query(50, ge=1, le=200, description="Max number of results to return"),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    db: AsyncSession = Depends(get_db),
    current_user_data: tuple = Depends(get_current_user_object),
):
    user, profile = current_user_data
    user_id = str(user.id)  # or profile.id depending on your schema

    collection = mongo_db["master_medicine"]

    cursor = collection.find(
        {"product_name": {"$regex": name, "$options": "i"}},
        {"_id": 0}
    ).limit(limit)
    results = await cursor.to_list(length=limit)

    # Save search in search_history collection
    history_collection = mongo_db["search_history"]
    await history_collection.update_one(
        {"user_id": user_id},
        {
            "$push": {
                "history": {
                    "$each": [{"name": name, "searched_at": datetime.utcnow()}],
                    "$slice": -20  # keep only last 20 searches
                }
            }
        },
        upsert=True
    )

    return results

# Get Search History
@router.get("/search_history")
async def get_search_history(
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    db: AsyncSession = Depends(get_db),
    current_user_data: tuple = Depends(get_current_user_object),
):
    user, profile = current_user_data
    user_id = str(user.id)

    collection = mongo_db["search_history"]
    doc = await collection.find_one({"user_id": user_id}, {"_id": 0})
    return doc.get("history", []) if doc else []


# Product Details
@router.get("/product_details")
async def product_details(
    product_id: str = Query(..., description="Product ID"),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    collection = mongo_db["master_medicine"]
    product = await collection.find_one({"product_id": product_id}, {"_id": 0})
    if not product:
        return {"error": "Product not found"}
    return product

# Medicine List (filterable)
@router.get("/medicine_list")
async def medicine_list(
    brand: Optional[str] = None,
    category: Optional[str] = None,
    salt: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    collection = mongo_db["master_medicine"]

    filters = {}

    if brand:
        filters["product_manufactured"] = {"$regex": brand, "$options": "i"}
    if category:
        filters["category"] = {"$regex": category, "$options": "i"}

    if salt:
        filters["$or"] = [
            {f"compound_{i}": {"$regex": salt, "$options": "i"}} for i in range(1, 25)
        ]

    cursor = collection.find(filters, {"_id": 0}).limit(limit)
    results = await cursor.to_list(length=limit)
    return results

# Similar Products (by salt)
@router.get("/similar_product")
async def similar_product(
    product_name: str = Query(..., description="Product name to find similar"),
    limit: int = Query(10, ge=1, le=50),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    collection = mongo_db["master_medicine"]

    product = await collection.find_one({"product_name": product_name}, {"_id": 0})
    if not product:
        return {"error": "Product not found"}
    
    compounds = []
    for i in range(1, 25):
        comp = product.get(f"compound_{i}")
        if comp:
            compounds.append(comp)

    if not compounds:
        return {"error": "No salt composition available"}

    # build OR filter for similar compounds
    compound_filters = [
        {f"compound_{i}": {"$in": compounds}} for i in range(1, 9)
    ]

    cursor = collection.find(
        {
            "product_name": {"$ne": product_name},
            "$or": compound_filters
        },
        {"_id": 0}
    ).limit(limit)

    results = await cursor.to_list(length=limit)
    return results

