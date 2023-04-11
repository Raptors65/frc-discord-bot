from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from dotenv import load_dotenv
import os
from typing import Any, Optional

from tba_types import Event, EventPredictions, MatchSimple, ModelType

load_dotenv()

TBA_API_KEY = os.getenv("TBA_API_KEY")

HEADERS = {
    "X-TBA-AUTH-KEY": TBA_API_KEY
}

BASE_URL = "https://www.thebluealliance.com/api/v3"

etags = {}

session: Optional[CachedSession] = None


async def get_json(path: str, model_type: Optional[ModelType] = None) -> Any:
    global session

    # Create session if not already created
    if session is None:
        session = CachedSession(cache=SQLiteBackend(cache_name='api_cache',
                                                    cache_control=True))

    # Get full URL and headers
    full_url = BASE_URL + path

    if full_url in etags:
        headers = {**HEADERS, "If-None-Match": etags[full_url]}
    else:
        headers = HEADERS

    # Necessary to manually get cached response because if it expired,
    # then it will be deleted during the request.
    cache_key = session.cache.create_key("GET", full_url)
    cached_response = await session.cache.responses.read(cache_key)

    # Send request
    async with session.get(full_url, headers=headers) as response:
        if response.status == 200:
            # This means either the response was cached or there was
            # new data.
            etags[full_url] = response.headers["ETag"]
            return await response.json()
        elif response.status == 304:
            # This means the cache expired but the server said the data
            # was not changed.
            if cached_response is not None:
                # Re-cache original cached data
                await session.cache.responses.write(cache_key, cached_response)
                # Return cached data
                cached_data = await cached_response.json()  # type: ignore
                return cached_data

            if cached_response is None:
                # this shouldn't happen but just in case...
                etags.pop(full_url)
        elif response.status == 404:
            raise FileNotFoundError("404 Not Found; check your parameters?")
        else:
            raise ConnectionError(
                f"Error accessing the TBA API; status code {response.status}.")


async def event_matches_simple(event_key: str) -> list[MatchSimple]:
    return await get_json(f"/event/{event_key}/matches/simple")


async def team_events_statuses(team_key: str, year: int) -> dict:
    return await get_json(f"/team/{team_key}/events/{year}/statuses")


async def team_events_year(team_key: str, year: int) -> list[Event]:
    return await get_json(f"/team/{team_key}/events/{year}")


async def event_predictions(event_key: str) -> EventPredictions:
    return await get_json(f"/event/{event_key}/predictions")


async def team_matches_year_simple(team_key: str, year: int) -> list[MatchSimple]:
    return await get_json(f"/team/{team_key}/matches/{year}/simple")


async def team_event_matches(team_key: str, event_key: str):
    return await get_json(f"/team/{team_key}/event/{event_key}/matches")
