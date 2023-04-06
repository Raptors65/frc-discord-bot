from aiohttp_client_cache import CachedSession, SQLiteBackend
from dotenv import load_dotenv
import os
from base64 import b64encode
from typing import Literal, NotRequired, Optional, TypedDict

from tba_types import Event, EventPredictions, MatchSimple, ModelType

load_dotenv()

TBA_API_KEY = os.getenv("TBA_API_KEY")

HEADERS = {
    "X-TBA-AUTH-KEY": TBA_API_KEY
}

BASE_URL = "https://www.thebluealliance.com/api/v3"

etags = {}

session: CachedSession = None


async def get_json(path: str):
    global session

    if session is None:
        session = CachedSession(cache=SQLiteBackend(cache_name='api_cache',
                                                    cache_control=True))

    full_url = BASE_URL + path
    if full_url in etags:
        headers = {**HEADERS, "If-None-Match": etags[full_url]}
    else:
        headers = HEADERS

    async with session.get(full_url, headers=headers) as response:
        if response.status < 400:
            etags[full_url] = response.headers["ETag"]
            return await response.json()
        else:
            raise ConnectionError(
                f"Error accessing the TBA API; status code {response.status}.")


async def team_events_statuses(team_key: str, year: int) -> dict:
    return await get_json(f"/team/{team_key}/events/{year}/statuses")


async def team_events_year(team_key: str, year: int) -> list[Event]:
    return await get_json(f"/team/{team_key}/events/{year}")


async def event_predictions(event_key: str) -> EventPredictions:
    return await get_json(f"/event/{event_key}/predictions")


async def team_matches_year_simple(team_key: int, year: int) -> list[MatchSimple]:
    return await get_json(f"/team/{team_key}/matches/{year}/simple")


async def team_event_matches(team_key: str, event_key: str, model_type: Optional[ModelType] = None):
    if model_type is None:
        return await get_json(f"/team/{team_key}/event/{event_key}/matches")
    elif model_type in ["simple", "keys"]:
        return await get_json(f"/team/{team_key}/event/{event_key}/matches/{model_type}")
    else:
        raise ValueError("Invalid model_type; must be 'simple' or 'keys'.")
