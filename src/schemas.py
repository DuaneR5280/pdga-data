from typing import List, Union, Optional, Dict, Any
from datetime import datetime, date
from pydantic import (
    BaseModel,
    HttpUrl,
    Field,
    field_validator,
    ValidationError,
    model_validator,
    RootModel,
)
from rich import print

class DiscBase(BaseModel):
    manufacturer: str
    name: str
    weight_max: float = 180.0
    diameter: float = None
    height: float = None
    rim_depth: float = None
    rim_diameter_inside: float = None
    rim_thickness: float = None
    rim_ratio: float = None
    rim_config: float = None
    flex: float = None
    cert: str = None
    approved: date = None
    speed: Union[float, int] = None
    glide: Union[float, int] = None
    turn: Union[float, int] = None
    fade: Union[float, int] = None
    stability: Union[float, int] = None
    description: str = None
    url: HttpUrl = None  # Optional[HttpUrl] = None
    oop: bool = None

    @field_validator("approved", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        return value


class CompanyBase(BaseModel):
    """Company Name,Status,Approved Equipment,Contact,Phone,Address,City,State,Country,ZIP,Website"""
    company_name: str
    equipment: str = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = None
    phone: Optional[str] = None
    website: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    facebook: Optional[HttpUrl] = None
    instagram: Optional[HttpUrl] = None
    youtube: Optional[HttpUrl] = None
    contact_name: str = None
    contact_email: str = None
    contact_phone: str = None
    is_active: bool = True

    @field_validator("is_active", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, str):
            if value.lower() == "active":
                return True
            elif value.lower() == "inactive":
                return False
        return value

# Tournaments
class HoleDetail(BaseModel):
    """Represents the hole details for a tournament
    {
        "Hole": "H1",
        "HoleOrdinal": 1,
        "Label": "1",
        "Par": 3,
        "Length": 382,
        "Units": None,
        "Accuracy": None,
        "Ordinal": 1,
    }
    """

    hole: str
    hole_ordinal: Optional[int] = Field(default=None, alias="HoleOrdinal")
    label: str
    par: int
    length: Optional[Union[int, None]] = None
    ordinal: Optional[int] = None

    class Config:
        alias_generator = lambda x: x.capitalize()


class HoleScores(BaseModel):
    """Represents the hole scores for a tournament
    [
            {
                'ResultID': 210830836,
                'Name': 'Josh Hill',
                'PDGANum': 98981,
                'Rating': 867,
                'Division': 'MA40',
                'Round': 1,
                'Holes': 21,
                'LayoutID': 659400,
                'GrandTotal': 121,
                'Played': 21,
                'RoundScore': 60,
                'RoundtoPar': -3,
                'ToPar': -9,
                'Rounds': '60,61,,,,,,,,,,,',
                'RoundRating': None,
                'ProfileURL': 'https://www.pdga.com/player/98981',
                'HoleScores': ['2', '3', '3', '3', '3', '3', '2', '3', '3', '3', '3', '2', '4', '3', '2', '3', '4', '3', '2', '3', '3']
            }
    ]
    """

    result_id: int = Field(..., alias="ResultID")
    round_id: int = Field(..., alias="RoundID")
    score_id: int = Field(None, alias="ScoreID")
    name: str
    pdga_num: Optional[int] = Field(..., alias="PDGANum")
    rating: Optional[int] = (
        None  # rating is current rating instead of rating at time of event
    )
    profile_url: Optional[HttpUrl] = Field(..., alias="ProfileURL")
    layout_id: int = Field(..., alias="LayoutID")
    division: str
    holes: int
    round: int
    round_score: Optional[int] = Field(..., alias="RoundScore")
    round_to_par: Optional[int] = Field(..., alias="RoundtoPar")
    round_rating: Optional[int] = Field(..., alias="RoundRating")
    scores: Optional[List[Union[int, None]]] = Field(..., alias="HoleScores")

    class Config:
        alias_generator = lambda x: x.capitalize()

    @field_validator("profile_url", mode="before")
    @classmethod
    def validate_profile_url(cls, value):
        if value == "" or value is None:
            return "https://www.pdga.com/no_profile"
        return value

    @field_validator("scores", mode="before")
    @classmethod
    def validate_scores(cls, value):
        # Replace empty strings with None
        hole_scores = [int(value) if value else None for value in value]
        return hole_scores


class Layout(BaseModel):
    """Represents the layout for a tournament
    {
        'LayoutID': 659400,
        'CourseID': 24799,
        'CourseName': 'Badlands',
        'TournID': 78184,
        'Name': '303 Doubles Alternate Shot Long 17',
        'Holes': 21,
        'Par': 63,
        'Length': 6124,
        'Units': 'Feet',
        'Accuracy': 'M',
        'Notes': None,
    }
    """

    api_url: Optional[HttpUrl]
    live_url: Optional[HttpUrl]
    tourn_id: int = Field(..., alias="TournID")
    layout_id: int = Field(..., alias="LayoutID")
    course_id: Optional[int] = Field(..., alias="CourseID")
    course_name: Optional[str] = Field(..., alias="CourseName")
    name: str = Field(..., alias="Name")
    division: str
    round_num: int | str
    holes: int = Field(..., alias="Holes")
    par: int = Field(..., alias="Par")
    length: Optional[Union[int, None]] = Field(..., alias="Length")
    ssa: Optional[float]
    notes: Optional[str] = Field(..., alias="Notes")
    hole_detail: Optional[List[HoleDetail]] = Field(..., alias="Detail")
    scores: Optional[List[HoleScores]] = None


class Divisions(BaseModel):
    division_name: str
    place: int
    points: int
    player_name: str
    player_page: HttpUrl
    player_num: int
    player_rating: int
    player_par: int
    player_round_scores: List[int]
    player_round_ratings: List[int]
    player_score_total: int


class Event(BaseModel):
    event_id: int
    event_name: str
    event_url: HttpUrl
    start_date: date
    end_date: Optional[date] = None  # Optional date
    location: str
    tier: str
    tournament_director: Optional[str]
    asst_td: Optional[str | List]  # edge case
    website: Optional[HttpUrl] = None
    scores: Optional[List[Dict]] = None

    @field_validator("website", mode="before")
    def validate_website_url(cls, value: str | None):  # Allow str or None
        if value is None:
            return None  # If None, keep it as None
        try:
            url = HttpUrl(value, scheme="https")
            return url
        except ValidationError as e:
            print(e)
            return None


class PlayerEvent(Event):
    # place: int
    # points: int
    # rating_day_of: int = Field(..., alias="rating")
    # division: str
    score: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    def remove_scores(cls, values):
        """Remove scores from player event
        Temp until scores are formatted correctly
        to be able to use BaseModel
        """
        values.pop("scores", None)
        return values


class TournamentResult(BaseModel):
    year: int
    dates: str | date
    division: str
    place: int
    points: float
    tournament: str
    tournament_url: str  # AnyHttpUrl = None
    tier: str
    prize: Optional[str] = None
    event_info: Optional[Event] = None


# Players
class PlayerStatsUrls(RootModel):
    root: Dict[str, str] = Field(
        ..., description="Dictionary of year to stats URL mappings"
    )


class SeasonTotal(BaseModel):
    year: int
    classification: str  # Amateur, Professional
    division: str
    num_tournaments: int
    points: float


class Season(BaseModel):
    totals: Optional[List[SeasonTotal]] = Field(default_factory=list)
    tournament_results: Optional[List[TournamentResult]] = Field(default_factory=list)


class RatingsDetail(BaseModel):
    pass


class RatingsHistory(BaseModel):
    date: date
    rating: int
    rounds_used: int


class UpcomingEvent(BaseModel):
    date: date
    name: str
    location: str
    url: str
    event_id: int


class Rating(BaseModel):
    current: int
    last_updated: date
    change: int = 0


class PlayerBase(BaseModel):
    player_name: str
    pdga_num: int
    profile_url: HttpUrl
    location: Optional[str]
    classification: str
    join_date: int
    membership_status: str
    current_rating: Optional[Rating]
    career_events: Optional[int]
    career_wins: Optional[int]
    world_rank: Optional[str]
    upcoming_events: Optional[List[UpcomingEvent]]
    stats_years_urls: Optional[PlayerStatsUrls]
    event_results: Optional[List[PlayerEvent]]

    def profile(self):
        """
        Returns a dictionary representation of the PlayerBase object, excluding the 'stats_years_urls' and 'event_results' fields.

        Returns:
            dict: A dictionary representation of the PlayerBase object.
        """
        return self.model_dump(exclude={"stats_years_urls", "event_results"})
