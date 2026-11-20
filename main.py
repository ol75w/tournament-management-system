from fastapi import FastAPI, HTTPException, Depends
from schemas import (
    TeamCreate, TeamUpdate, TeamResponse,
    TournamentCreate, TournamentUpdate, TournamentResponse,
    GroupCreate, MatchCreate, MatchUpdate, MatchResponse
)
from database import engine, Base, get_db 
from sqlalchemy.orm import Session
from models import (
    Team, Tournament, Registration,
    TournamentGroup, GroupAssignment, Match
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tournament Management Api",
    description="An Api For Managing Esports Teams",
    version="1.0.0"
)



@app.get("/")
def home():
    return {
        "message": "Tournament ap running"
    }


@app.post("/teams", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):

    new_team = Team(
        name=team.name,
        game=team.game,
        captain=team.captain,
        players=team.players
    )

    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    return new_team


@app.get("/teams", response_model=list[TeamResponse])
def get_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()

    return teams


@app.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):

    team = db.query(Team).filter(Team.id == team_id).first()

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    return team

    

@app.put("/teams/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    update_data: TeamUpdate,
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(Team.id == team_id).first()

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    team.name = update_data.name
    team.game = update_data.game
    team.captain = update_data.captain
    team.players = update_data.players

    db.commit()
    db.refresh(team)

    return team



@app.delete("/teams/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db)):

    team = db.query(Team).filter(Team.id == team_id).first()

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    db.delete(team)
    db.commit()

    return {
        "message": "Team deleted successfully"
    }

@app.post("/tournaments", response_model=TournamentResponse)
def create_tournament(
    tournament : TournamentCreate,
    db: Session = Depends(get_db)
):
    new_tournament = Tournament(
        name=tournament.name,
        game=tournament.game,
        max_teams=tournament.max_teams
    )

    db.add(new_tournament)
    db.commit()
    db.refresh(new_tournament)

    return new_tournament

@app.get("/tournaments", response_model=list[TournamentResponse])
def get_tournaments(db: Session = Depends(get_db)):
    tournaments = db.query(Tournament).all()

    return tournaments

@app.get("/tournaments/{tournament_id}", response_model=TournamentResponse)
def get_tournament(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if tournament is None:
        raise HTTPException(
            status_code=404,
            detail="No tournament found"
        )
    return tournament

@app.put("/tournaments/{tournament_id}", response_model=TournamentResponse)
def update_tournament(
    tournament_id: int,
    update_data: TournamentUpdate,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if tournament is None:
        raise HTTPException(
            status_code=404,
            detail="No tournament not found"
        )

    tournament.name = update_data.name
    tournament.game = update_data.game
    tournament.max_teams = update_data.max_teams
    tournament.status = update_data.status

    db.commit()
    db.refresh(tournament)

    return tournament

@app.delete("/tournaments/{tournament_id}")
def delete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(
        Tournament.id == tournament_id
    ).first()

    if tournament is None:
        raise HTTPException(
            status_code=404,
            detail="Tournament not found"
        )

    db.delete(tournament)
    db.commit()

    return {
        "message": "Tournament deleted successfully"
    }


@app.post("/tournaments/{tournament_id}/register/{team_id}")
def register_team(
    tournament_id: int,
    team_id: int,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(
        Tournament.id == tournament_id
    ).first()

    if not tournament:
        raise HTTPException(
            status_code=404,
            detail="Tournament not found"
        )

    team = db.query(Team).filter(
        Team.id == team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    if team.game.lower() != tournament.game.lower():
        raise HTTPException(
            status_code=400,
            detail="Games do not match"
        )

    existing_registration = db.query(Registration).filter(
        Registration.tournament_id == tournament_id,
        Registration.team_id == team_id
    ).first()

    if existing_registration:
        raise HTTPException(
            status_code=409,
            detail="Team already registered"
        )

    registered_count = db.query(Registration).filter(
        Registration.tournament_id == tournament_id
    ).count()

    if registered_count >= tournament.max_teams:
        raise HTTPException(
            status_code=409,
            detail="Tournament is full"
        )

    new_registration = Registration(
        tournament_id=tournament_id,
        team_id=team_id
    )

    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return {
        "message": "Team registered successfully",
        "registration_id": new_registration.id,
        "tournament_id": tournament_id,
        "team_id": team_id
    }

@app.get(
    "/tournaments/{tournament_id}/teams",
    response_model=list[TeamResponse]
)
def get_registered_teams(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(
        Tournament.id == tournament_id
    ).first()

    if not tournament:
        raise HTTPException(
            status_code=404,
            detail="Tournament not found"
        )

    teams = db.query(Team).join(
        Registration,
        Team.id == Registration.team_id
    ).filter(
        Registration.tournament_id == tournament_id
    ).all()

    return teams

@app.delete("/tournaments/{tournament_id}/unregister/{team_id}")
def unregister_team(
    tournament_id: int,
    team_id: int,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(
        Tournament.id == tournament_id
    ).first()

    if not tournament:
        raise HTTPException(
            status_code=404,
            detail="Tournament not found"
        )

    registration = db.query(Registration).filter(
        Registration.tournament_id == tournament_id,
        Registration.team_id == team_id
    ).first()

    if not registration:
        raise HTTPException(
            status_code=404,
            detail="Registration not found"
        )

    db.delete(registration)
    db.commit()

    return {
        "message": "Team unregistered successfully"
    }

@app.post("/tournaments/{tournament_id}/groups")
def groupcreate(
    tournament_id: int,
    group: GroupCreate,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(
            status_code=404,
            detail= "No tournament found"
        )

    existing_group = db.query(TournamentGroup).filter(
        TournamentGroup.tournament_id == tournament_id,
        TournamentGroup.name == group.name 
        ).first()

    if existing_group:
        raise HTTPException(
            status_code=409,
            detail="Group already exists"
        )

    new_group = TournamentGroup(
        name = group.name,
        tournament_id = tournament_id
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return {
        "message": "Group created successfully",
        "group_id": new_group.id,
        "group_name": new_group.name,
        "tournament_id": new_group.tournament_id
    }

@app.post("/groups/{group_id}/assign/{team_id}")
def assign_team(
    group_id: int,
    team_id: int,
    db: Session = Depends(get_db)
):
    group = db.query(TournamentGroup).filter(TournamentGroup.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=404,
            detail= "No group found"
        )

    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail= "No team found"
        )

    registration = db.query(Registration).filter(
        Registration.tournament_id == group.tournament_id,
        Registration.team_id == team_id
    ).first()

    if not registration:
        raise HTTPException(
            status_code=404,
            detail= "Team not registered"
        )

    existing_assignment = db.query(GroupAssignment).filter(GroupAssignment.registration_id == registration.id).first()

    if existing_assignment:
        raise HTTPException(
            status_code=409,
            detail= "Team already assigned to a group"
        )

    new_assignment = GroupAssignment(
        group_id=group_id,
        registration_id=registration.id
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return {
        "message": "Team assigned successfully",
        "group_id": group_id,
        "team_id": team_id,
        "registration_id": registration.id
    }

@app.get("/tournaments/{tournament_id}/groups")
def get_tournament_group(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(
            status_code=404,
            detail= "No tournament found"
        )

    groups = db.query(TournamentGroup).filter(TournamentGroup.tournament_id == tournament_id).all()

    result = []

    for group in groups:
        teams = db.query(Team).join(
            Registration,
            Team.id == Registration.team_id 
        ).join(
            GroupAssignment,
            Registration.id == GroupAssignment.registration_id
        ).filter(
            GroupAssignment.group_id == group.id
        ).all()

        result.append({
            "group_id": group.id,
            "group_name": group.name,
            "teams": [
                {
                    "id": team.id,
                    "name": team.name,
                    "game": team.game,
                    "captain": team.captain,
                    "players": team.players
                }
                for team in teams
            ]
        })

    return result

@app.delete("/groups/{group_id}/remove/{team_id}")
def remove_team_from_group(
    group_id: int,
    team_id: int,
    db: Session = Depends(get_db)
):
    group = db.query(TournamentGroup).filter(TournamentGroup.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=404,
            detail= "No group found"
        )

    registration = db.query(Registration).filter(
        Registration.tournament_id == group.tournament_id,
        Registration.team_id == team_id
    ).first()

    if not registration:
        raise HTTPException(
            status_code=404,
            detail= "Team is not registered in this tournament"
        )

    assignment = db.query(GroupAssignment).filter(
        GroupAssignment.group_id == group_id,
        GroupAssignment.registration_id == registration.id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail= "Team is not assigned to this group"
        )

    db.delete(assignment)
    db.commit()

    return {
        "message": "Team removed from group successfully",
        "group_id": group_id,
        "team_id": team_id
    
    }

@app.post("/tournaments/{tournament_id}/matches", response_model=MatchResponse)
def create_match(
    tournament_id: int,
    match: MatchCreate,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(
            status_code=404,
            detail="No tournament found"
        )

    if match.team1_id == match.team2_id:
        raise HTTPException(
            status_code=404,
            detail="A team cannot play against itself"
        )

    team1 = db.query(Team).filter(Team.id == match.team1_id).first()
    team2 = db.query(Team).filter(Team.id == match.team2_id).first()

    if not team1 or not team2:
        raise HTTPException(
            status_code=404,
            detail="One or both team not found"
        )

    for team_id in [match.team1_id, match.team2_id]:
        registration = db.query(Registration).filter(
            Registration.tournament_id == tournament_id,
            Registration.team_id == team_id
        ).first()

        if not registration:
            raise HTTPException(
                status_code=400,
                detail=f"Team {team_id} is not registered in this tournament"
            )
    if match.group_id is not None:
        group = db.query(TournamentGroup).filter(
            TournamentGroup.id == match.group_id,
            TournamentGroup.tournament_id == tournament_id
        ).first()

        if not group:
            raise HTTPException(
                status_code=404,
                detail="Group not found in this tournament"
            )

        for team_id in [match.team1_id, match.team2_id]:
            registration = db.query(Registration).filter(
                Registration.tournament_id == tournament_id,
                Registration.team_id == team_id
            ).first()

            assignment = db.query(GroupAssignment).filter(
                GroupAssignment.registration_id == registration.id,
                GroupAssignment.group_id == match.group_id
            ).first()

            if not assignment:
                raise HTTPException(
                    status_code=400,
                    detail=f"Team {team_id} is not assigned to this group"
                )

    new_match = Match(
        tournament_id=tournament_id,
        group_id=match.group_id,
        team1_id=match.team1_id,
        team2_id=match.team2_id
    )

    db.add(new_match)
    db.commit()
    db.refresh(new_match)

    return new_match


@app.get(
    "/tournaments/{tournament_id}/matches",
    response_model=list[MatchResponse]
)
def get_tournament_matches(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    tournament = db.query(Tournament).filter(
        Tournament.id == tournament_id
    ).first()

    if not tournament:
        raise HTTPException(
            status_code=404,
            detail="Tournament not found"
        )

    matches = db.query(Match).filter(
        Match.tournament_id == tournament_id
    ).all()

    return matches


@app.put(
    "/matches/{match_id}/result",
    response_model=MatchResponse
)
def update_match_result(
    match_id: int,
    result: MatchUpdate,
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(
        Match.id == match_id
    ).first()

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )

    match.team1_score = result.team1_score
    match.team2_score = result.team2_score

    if result.team1_score > result.team2_score:
        match.winner_id = match.team1_id
        match.status = "completed"

    elif result.team2_score > result.team1_score:
        match.winner_id = match.team2_id
        match.status = "completed"

    else:
        match.winner_id = None
        match.status = "draw"

    db.commit()
    db.refresh(match)

    return match


@app.get(
    "/matches/{match_id}",
    response_model=MatchResponse
)
def get_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(
        Match.id == match_id
    ).first()

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )

    return match


@app.delete("/matches/{match_id}")
def delete_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(
        Match.id == match_id
    ).first()

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )

    db.delete(match)
    db.commit()

    return {
        "message": "Match deleted successfully"
    }
