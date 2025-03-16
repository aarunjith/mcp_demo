from pydantic import BaseModel, Field
from typing import Literal, Optional, List


class Session(BaseModel):
    session_key: int = Field(description="Unique identifier for the session")
    session_name: str = Field(description="Name of the session")
    session_type: Literal["Qualifying", "Practice", "Race"] = Field(
        description="Type of session"
    )
    date_start: str = Field(
        description="Starting timestamp of the session in ISO 8601 format"
    )
    date_end: Optional[str] = Field(
        None, description="Ending timestamp of the session in ISO 8601 format"
    )
    meeting_key: int = Field(description="Unique identifier for the meeting")
    circuit_short_name: str = Field(description="Short name of the circuit")
    country_name: str = Field(description="Name of the country")
    meeting_official_name: Optional[str] = Field(
        None, description="Official name of the race"
    )

    class Config:
        extra = "ignore"


class Driver(BaseModel):
    broadcast_name: str = Field(
        description="Name of the driver as shown in the broadcast"
    )
    driver_number: int = Field(description="Driver number on the car")
    first_name: str = Field(description="First name of the driver")
    last_name: str = Field(description="Last name of the driver")
    name_acronym: str = Field(description="Three letter acronym for the driver")
    team_name: str = Field(description="Name of the team")
    team_colour: Optional[str] = Field(
        description="The hexadecimal color value (RRGGBB) of the driver's team."
    )
    headshot_url: Optional[str] = Field(description="URL to the headshot of the driver")

    class Config:
        extra = "ignore"


class MiniSectorValue(BaseModel):
    performance: Optional[str] = Field(
        "Unknown Performance",
        description=(
            "Performance in the mini-sector. Purple is faster than anyone else, "
            "green is personal best, yellow is worse than the personal best, "
            "and then pitlane which indicates that the driver was in the pitlane."
        ),
    )

    @classmethod
    def from_value(cls, value: int) -> "MiniSectorValue":
        match value:
            case 0:
                return cls(performance="Not available")
            case 2048:
                return cls(performance="Yellow")
            case 2049:
                return cls(performance="Green")
            case 2051:
                return cls(performance="Purple")
            case 2064:
                return cls(performance="Pitlane")
            case _:
                return cls(performance="Unknown Performance")


class Lap(BaseModel):
    date_start: Optional[str] = Field(
        None,
        description="The UTC starting date and time of the lap, in ISO 8601 format",
    )
    duration_sector_1: Optional[float] = Field(
        None, description="Time taken to complete the first sector"
    )
    duration_sector_2: Optional[float] = Field(
        None, description="Time taken to complete the second sector"
    )
    duration_sector_3: Optional[float] = Field(
        None, description="Time taken to complete the third sector"
    )
    i1_speed: Optional[float] = Field(
        None,
        description="The speed of the car, in km/h, at the first intermediate point on the track.",
    )
    i2_speed: Optional[float] = Field(
        None,
        description="The speed of the car, in km/h, at the second intermediate point on the track.",
    )
    st_speed: Optional[float] = Field(
        None,
        description="The speed of the car, in km/h, at the speed trap, which is a specific point on the track where the highest speeds are usually recorded.",
    )
    is_pit_out_lap: Optional[bool] = Field(
        None,
        description='A boolean value indicating whether the lap is an "out lap" from the pit (true if it is, false otherwise).',
    )
    lap_duration: Optional[float] = Field(
        None,
        description="The total time taken, in seconds, to complete the entire lap.",
    )
    segments_sector_1: Optional[List[MiniSectorValue]] = Field(
        default=[],
        description="A list of values representing performance in the 'mini-sectors' within the first sector",
    )
    segments_sector_2: Optional[List[MiniSectorValue]] = Field(
        default=[],
        description="A list of values representing performance in the 'mini-sectors' within the second sector",
    )
    segments_sector_3: Optional[List[MiniSectorValue]] = Field(
        default=[],
        description="A list of values representing performance in the 'mini-sectors' within the third sector",
    )

    class Config:
        extra = "ignore"


class TrackConditions(BaseModel):
    session_key: int = Field(description="Unique identifier for the session")
    date: str = Field(
        description="The UTC starting date and time of the lap, in ISO 8601 format"
    )
    air_temperature: float = Field(description="The air temperature in degrees Celsius")
    humidity: float = Field(description="The humidity in percent")
    pressure: float = Field(description="Air pressure (mbar)")
    rainfall: float = Field(
        description="Whether there is rain or not. 0 is no rain and 1 is rain"
    )
    track_temperature: float = Field(
        description="The track temperature in degrees Celsius"
    )
    wind_direction: float = Field(
        description="The wind direction in degrees from 0° to 359°."
    )
    wind_speed: float = Field(description="The wind speed in m/s")

    class Config:
        extra = "ignore"
