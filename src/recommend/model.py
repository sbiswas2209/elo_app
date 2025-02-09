from typing import Optional
from pydantic import BaseModel

class Actress(BaseModel):
    _id: Optional[str] = None
    url: Optional[str] = None
    name: Optional[str] = None
    rating: Optional[int] = None

class FetchActressesRequestBody(BaseModel):
    actress_one_id: Optional[str]
    actress_two_id: Optional[str]

class ChoiceBody(BaseModel):
    winner_id: str
    loser_id: str
