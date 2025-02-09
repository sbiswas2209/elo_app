from fastapi import APIRouter, Header
from typing import Optional
from pydantic import BaseModel
from src.recommend.model import Actress, ChoiceBody, FetchActressesRequestBody
from src.recommend.service import recommend_pairs, update_elo_rating, get_leaderboard
from typing import Annotated

router = APIRouter()

@router.post("/fetch")
async def recommend(user_id: Annotated[str, Header()] ,data: Optional[FetchActressesRequestBody]):
    actress_1, actress_2 = await recommend_pairs(user_id=user_id, actress_one_id=data.actress_one_id, actress_two_id=data.actress_two_id)
    return {
        "message": "Response sent",
        "actress_1": actress_1,
        "actress_2": actress_2
    }

@router.post("/score")
async def score(data: ChoiceBody):
    result = update_elo_rating(winner_id=data.winner_id, loser_id=data.loser_id)
    return {
        "message": "Updated",
        "result": result
    }

@router.get("/leaderboard")
async def fetch_leaderboard():
    result = get_leaderboard()
    return result