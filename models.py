from sqlalchemy import Integer, String, Column, ForeignKey, UniqueConstraint
from database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    game = Column(String, nullable=False)
    captain = Column(String, nullable=False)
    players = Column(Integer, nullable=False)

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    game = Column(String, nullable=False)
    max_teams = Column(Integer, nullable=False)
    status = Column(String, default="upcoming")

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)

    tournament_id = Column(
        Integer,
        ForeignKey("tournaments.id"),
        nullable=False
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "tournament_id",
            "team_id",
            name="unique_team_registration"
        ),
    )

class TournamentGroup(Base):
    __tablename__ = "tournament_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)

    __table_args__ = (UniqueConstraint("tournament_id", "name", name= "unique_group_per_tournament" ),)

class GroupAssignment(Base):
    __tablename__ = "group_assignments"

    id = Column(Integer, primary_key=True, index=True)

    group_id = Column(
        Integer,
        ForeignKey("tournament_groups.id"),
        nullable=False
    )

    registration_id = Column(
        Integer,
        ForeignKey("registrations.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "registration_id",
            name="unique_group_assignment"
        ),
    )


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("tournament_groups.id"), nullable=True)

    team1_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team2_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    team1_score = Column(Integer, default=0)
    team2_score = Column(Integer, default=0)

    status = Column(String, default="scheduled")
    winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
