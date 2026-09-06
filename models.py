from pydantic import BaseModel
from typing import List, Optional


class ClubEvent(BaseModel):
    id : int
    title: str
    url: str = "https://www.activateuts.com.au/"
    start_date: str = "N/A"
    end_date: str = "N/A"
    desc: Optional[str] = "No description"

class Club(BaseModel):
    club_id: str
    name: str
    url: str
    events: Optional[List[ClubEvent]]

class ClubList(BaseModel):
    clubs: List[Club]

