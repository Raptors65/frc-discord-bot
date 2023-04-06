from typing import Literal, Optional, TypedDict


class DistrictList(TypedDict):
    abbreviation: str
    display_name: str
    key: str
    year: int


class Webcast(TypedDict):
    type: str
    channel: str
    date: Optional[str]
    file: Optional[str]


class Event(TypedDict):
    key: str
    name: str
    event_code: str
    event_type: int
    district: Optional[DistrictList]
    city: Optional[str]
    state_prov: Optional[str]
    country: Optional[str]
    start_date: str
    end_date: str
    year: int
    short_name: Optional[str]
    event_type_string: str
    week: Optional[int]
    address: Optional[str]
    postal_code: Optional[str]
    gmaps_place_id: Optional[str]
    gmaps_url: Optional[str]
    lat: Optional[int]
    lng: Optional[int]
    location_name: Optional[str]
    timezone: Optional[str]
    website: Optional[str]
    first_event_id: Optional[str]
    first_event_code: Optional[str]
    webcasts: Optional[list[Webcast]]
    division_keys: Optional[list[str]]
    parent_event_key: Optional[str]
    playoff_type: Optional[int]
    playoff_type_string: Optional[str]

# Prediction Types: may change at any time


class BrierScores(TypedDict):
    win_loss: float


class MatchTypePredictionStats(TypedDict):
    brier_scores: BrierScores
    err_mean: float
    err_var: float
    wl_accuracy: float
    wl_accuracy_75: float


class MatchPredictionStats(TypedDict):
    playoff: MatchTypePredictionStats
    qual: MatchTypePredictionStats


class SingleMatchTeamPrediction(TypedDict):
    charge_station_points: float
    charge_station_points_var: float
    links: float
    links_var: float
    prob_activation_bonus: float
    prob_sustainability_bonus: float
    score: float
    score_var: float


class SingleMatchPrediction(TypedDict):
    blue: SingleMatchTeamPrediction
    prob: float
    red: SingleMatchTeamPrediction
    winning_alliance: Literal["red", "blue"]


MatchTypePredictions = dict[str, SingleMatchPrediction]


class MatchPredictions(TypedDict):
    playoff: MatchTypePredictions
    qual: MatchTypePredictions


class RankingPredictionStats(TypedDict):
    last_played_match: str


RankingPredictions = list[tuple[str, list[int]]]

TeamTaskPointsStats = dict[str, float]


class TaskPointsMeanVars(TypedDict):
    mean: TeamTaskPointsStats
    var: TeamTaskPointsStats


class MatchTypeStatMeanVars(TypedDict):
    charge_station_points: TaskPointsMeanVars
    links: TaskPointsMeanVars
    score: TaskPointsMeanVars


class StatMeanVars(TypedDict):
    playoff: MatchTypeStatMeanVars
    qual: MatchTypeStatMeanVars


class EventPredictions(TypedDict):
    match_prediction_stats: Optional[MatchPredictionStats]
    match_predictions: Optional[MatchPredictions]
    ranking_prediction_stats: Optional[RankingPredictionStats]
    ranking_predictions: Optional[RankingPredictions]
    stat_mean_vars: Optional[StatMeanVars]


class MatchAlliance(TypedDict):
    score: Optional[int]
    team_keys: list[str]
    surrogate_team_keys: Optional[list[str]]
    dq_team_keys: Optional[list[str]]


class AllianceList(TypedDict):
    red: MatchAlliance
    blue: MatchAlliance


class MatchSimple(TypedDict):
    key: str
    comp_level: Literal["qm", "ef", "qf", "sf", "f"]
    set_number: int
    match_number: int
    alliances: Optional[AllianceList]
    winning_alliance: Optional[Literal["red", "blue", ""]]
    event_key: str
    time: Optional[int]
    predicted_time: Optional[int]
    actual_time: Optional[int]


class APIStatusAppVersion(TypedDict):
    min_app_version: int
    latest_app_version: int


class APIStatus(TypedDict):
    current_season: int
    max_season: int
    is_datafeed_down: bool
    down_events: list[str]
    ios: APIStatusAppVersion
    android: APIStatusAppVersion


class TeamSimple(TypedDict):
    key: str
    team_number: int
    nickname: Optional[str]
    name: str
    city: Optional[str]
    state_prov: Optional[str]
    country: Optional[str]


class Team(TypedDict):
    key: str
    team_number: int
    nickname: Optional[str]
    name: str
    school_name: Optional[str]
    city: Optional[str]
    state_prov: Optional[str]
    country: Optional[str]
    address: Optional[str]
    postal_code: Optional[str]
    gmaps_place_id: Optional[str]
    gmaps_url: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    location_name: Optional[str]
    website: Optional[str]
    rookie_year: Optional[int]
    motto: Optional[str]
    home_championship: Optional[dict[str, str]]


class TeamRobot(TypedDict):
    year: int
    robot_name: str
    key: str
    team_key: str


class EventSimple(TypedDict):
    key: str
    name: str
    event_code: str
    event_type: int
    district: Optional[DistrictList]
    city: Optional[str]
    state_prov: Optional[str]
    country: Optional[str]
    start_date: str
    end_date: str
    year: int


ModelType = Literal["simple", "keys"]
