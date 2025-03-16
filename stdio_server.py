from datetime import datetime
from mcp.server.fastmcp import FastMCP
from f1_types import Session, Driver, Lap, MiniSectorValue, TrackConditions
from typing import List, Optional, Literal
from loguru import logger
from openf1_utils import get_response

BASE_URL = "https://api.openf1.org/v1"

mcp = FastMCP(
    "F1 Data",
    instructions="You can access real-time or historical Formula 1 (F1) data with this",
)


@mcp.tool()
async def get_sessions(
    date_start: str,
    session_type: Optional[Literal["Qualifying", "Practice", "Race"]] = None,
) -> List[Session]:
    """
    Get all racing sessions happening based on the filters
    Args:
        date_start: Start Date of the session to filter in ISO 8601 format
        session_type: Type of session to filter on
    Returns:
        List of sessions
    """
    url = f"{BASE_URL}/sessions?date_start>={date_start}"
    if session_type:
        url += f"&session_type={session_type}"
    session_response = await get_response(url)
    if session_response is None:
        logger.warning("Session response is None")
        return []
    sessions = []
    for session in session_response:
        meeting_key = session["meeting_key"]
        url = f"{BASE_URL}/meetings?meeting_key={meeting_key}"
        meeting_response = await get_response(url)
        if meeting_response is None:
            logger.warning("Meeting response is None")
            continue
        all_data = {**session, **meeting_response[0]}
        sessions.append(Session(**all_data))
    return sessions


@mcp.tool()
async def get_drivers(
    session_key: int, driver_number: Optional[int] = None
) -> List[Driver]:
    """
    Get all drivers participating in a given session. If a driver number is provided, it will return only that driver's information.
    Args:
        session_key: The key of the session to get drivers for
        driver_number: The number of the driver to get information for
    Returns:
        A list of drivers
    """
    url = f"{BASE_URL}/drivers?session_key={session_key}"
    if driver_number:
        url += f"&driver_number={driver_number}"
    drivers_response = await get_response(url)
    if drivers_response is None:
        logger.warning("Drivers response is None")
        return []
    return [Driver(**driver) for driver in drivers_response]


@mcp.tool()
async def get_laps(session_key: int, driver_number: int) -> List[Lap]:
    """
    Get all laps for a given driver in a given session
    Args:
        session_key: The key of the session to get laps for
        driver_number: The number of the driver to get laps for
    Returns:
        A list of laps
    """
    url = f"{BASE_URL}/laps?session_key={session_key}&driver_number={driver_number}"
    laps_response = await get_response(url)
    if laps_response is None:
        logger.warning("Laps response is None")
        return []
    laps = []
    for lap in laps_response:
        lap_data = {**lap}
        lap_data["segments_sector_1"] = [
            MiniSectorValue.from_value(value) for value in lap["segments_sector_1"]
        ]
        lap_data["segments_sector_2"] = [
            MiniSectorValue.from_value(value) for value in lap["segments_sector_2"]
        ]
        lap_data["segments_sector_3"] = [
            MiniSectorValue.from_value(value) for value in lap["segments_sector_3"]
        ]
        laps.append(Lap(**lap_data))
    return laps


@mcp.tool()
async def get_track_conditions(
    session_key: int, start_date: Optional[str] = None
) -> List[TrackConditions]:
    """
    Get all track conditions for a given session
    Args:
        session_key: The key of the session to get track conditions for
        start_date: The start date/timestamp from which to get track conditions
    Returns:
        A list of track conditions
    """
    url = f"{BASE_URL}/weather?session_key={session_key}"
    if start_date:
        url += f"&date>={start_date}"
    track_conditions_response = await get_response(url)
    if track_conditions_response is None:
        logger.warning("Track conditions response is None")
        return []
    return [
        TrackConditions(**track_condition)
        for track_condition in track_conditions_response
    ]


@mcp.tool()
async def get_current_date_and_time() -> str:
    """
    A clock for the LLM to get the current date and time
    Requires no arguments
    Returns:
        The current date and time in ISO 8601 format
    """
    return datetime.now().isoformat()


@mcp.prompt()
async def test_prompt(prompt: str) -> str:
    """
    A test prompt for the LLM to test the server
    Args:
        prompt: The prompt to test the server with
    """
    return prompt


if __name__ == "__main__":
    mcp.run()
