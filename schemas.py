
from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    game: str
    captain: str
    players: int = Field(ge=1, le=4)


class TeamUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    game: str
    captain: str
    players: int = Field(ge=1, le=4)


class TeamResponse(BaseModel):
    id: int
    name: str
    game: str
    captain: str
    players: int

    class Config:
        from_attributes = True

class TournamentCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    game: str
    max_teams: int = Field(ge=2, le=1000)


class TournamentUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    game: str
    max_teams: int = Field(ge=2, le=1000)
    status: str


class TournamentResponse(BaseModel):
    id: int
    name: str
    game: str
    max_teams: int
    status: str

    class Config:
        from_attributes = True

class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)

class MatchCreate(BaseModel):
    team1_id: int
    team2_id: int
    group_id: int | None = None

class MatchUpdate(BaseModel):
    team1_score: int = Field(ge=0)
    team2_score: int = Field(ge=0)

class MatchResponse(BaseModel):
    id: int
    tournament_id: int
    group_id: int | None
    team1_id: int
    team2_id: int
    team1_score: int
    team2_score: int
    status: str
    winning_id: int | None

    class Config:
        from_attributes = True