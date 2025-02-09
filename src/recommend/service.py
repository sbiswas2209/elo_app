import pymongo
import redis
from typing import List, Optional, Tuple, Dict
from bson import ObjectId
from utils.database import db, get_collection
from utils.constants import redis_uri, redis_password

db = get_collection("actresses")

# Redis client
redis_client = redis.Redis(host=redis_uri, port=12318, db=0, decode_responses=True, password=redis_password)

def serialize_document(doc: Dict) -> Dict:
    """Convert MongoDB document to a serializable format"""
    if doc is None:
        return None
    doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
    return doc

async def recommend_pairs(user_id: str, actress_one_id: Optional[str], actress_two_id: Optional[str]) -> Tuple[Optional[Dict], Optional[Dict]]:
    """Fetch two unique actresses, ensuring lost ones do not reappear"""

    seen_key = f"seen_actresses:{user_id}"  # Redis key to track seen actresses
    seen_actresses = redis_client.smembers(seen_key)  # Retrieve seen IDs

    # **Fix:** Ensure IDs are properly converted
    seen_actresses = {ObjectId(str(actress_id)) for actress_id in seen_actresses if actress_id}  # Convert only non-empty values

    # Fetch actress_one (not seen before)
    if actress_one_id:
        actress_one = db.find_one({"_id": ObjectId(actress_one_id)})
    else:
        actress_one = db.find_one({"_id": {"$nin": list(seen_actresses)}}, sort=[("recentActivity", pymongo.DESCENDING)])

    if not actress_one:
        return None, None  # No available actress

    # Mark actress_one as seen
    redis_client.sadd(seen_key, str(actress_one["_id"]))

    # Fetch actress_two (also not seen before)
    query = {"_id": {"$ne": actress_one["_id"], "$nin": list(seen_actresses)}}
    if actress_two_id:
        query["_id"]["$nin"].append(ObjectId(actress_two_id))  # Ensure actress_two is also unique

    actress_two = db.find_one(query)

    if not actress_two:
        return None, None  # No unique actress available

    # Mark actress_two as seen
    redis_client.sadd(seen_key, str(actress_two["_id"]))

    return serialize_document(actress_one), serialize_document(actress_two)

def get_rank(actress_id: str) -> int:
    """Retrieve the rank of an actress based on Elo rating."""
    rank = redis_client.zrevrank("actress_rankings", actress_id)
    return rank + 1 if rank is not None else None


def update_elo_rating(winner_id: str, loser_id: str, k_factor: int = 32) -> Dict[str, any]:
    def expected_score(rating_a: float, rating_b: float) -> float:
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    # Fetch winner and loser from MongoDB
    winner = db.find_one({"_id": ObjectId(winner_id)})
    loser = db.find_one({"_id": ObjectId(loser_id)})

    if not winner or not loser:
        return {"error": "One or both actresses not found"}

    winner_rating = float(winner.get("rating", 1000))
    loser_rating = float(loser.get("rating", 1000))

    # Store previous ranks
    prev_winner_rank = get_rank(winner_id)
    prev_loser_rank = get_rank(loser_id)

    expected_winner = expected_score(winner_rating, loser_rating)
    expected_loser = expected_score(loser_rating, winner_rating)

    new_winner_rating = winner_rating + k_factor * (1 - expected_winner)
    new_loser_rating = loser_rating + k_factor * (0 - expected_loser)

    # Update MongoDB
    db.update_one(
        {"_id": ObjectId(winner_id)},
        {"$set": {"rating": round(new_winner_rating), "recentActivity": True}},
    )

    db.update_one(
        {"_id": ObjectId(loser_id)},
        {"$set": {"rating": round(new_loser_rating), "recentActivity": True}},
    )

    # Update Redis leaderboard (sorted set)
    redis_client.zadd("actress_rankings", {winner_id: new_winner_rating, loser_id: new_loser_rating})

    # Get new ranks
    new_winner_rank = get_rank(winner_id)
    new_loser_rank = get_rank(loser_id)

    return {
        "winner_id": winner_id,
        "prev_winner_rank": prev_winner_rank,
        "new_winner_rank": new_winner_rank,
        "new_winner_rating": round(new_winner_rating),
        "loser_id": loser_id,
        "prev_loser_rank": prev_loser_rank,
        "new_loser_rank": new_loser_rank,
        "new_loser_rating": round(new_loser_rating),
    }

def get_leaderboard(limit: int = 10) -> List[Dict]:
    """Fetch the top actresses based on Elo rating and track their rank changes."""

    leaderboard_key = "leaderboard_ranks"  # Redis key to store previous rankings

    # Retrieve leaderboard sorted by Elo rating (descending)
    actresses = list(db.find({}, {"_id": 1, "name": 1, "rating": 1}).sort("rating", pymongo.DESCENDING).limit(limit))

    leaderboard = []
    
    for rank, actress in enumerate(actresses, start=1):
        actress_id = str(actress["_id"])  # Convert ObjectId to string

        # Fetch previous rank from Redis (if exists)
        previous_rank = redis_client.hget(leaderboard_key, actress_id)
        previous_rank = int(previous_rank) if previous_rank else None  # Convert to int if exists
        
        # Store the new rank in Redis
        redis_client.hset(leaderboard_key, actress_id, rank)

        # Append actress details with rank info
        leaderboard.append({
            "rank": rank,
            "previous_rank": previous_rank,
            "name": actress["name"],
            "rating": actress["rating"]
        })

    return leaderboard
