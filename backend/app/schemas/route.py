from typing import List, Optional
from pydantic import BaseModel, Field


class StopInput(BaseModel):
    name: str = Field(..., description="Location or facility name")
    latitude: Optional[float] = Field(None, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, description="Longitude in decimal degrees")


class OptimizeRouteRequest(BaseModel):
    stops: List[StopInput] = Field(..., description="List of locations to optimize route for")
    start_location_index: Optional[int] = Field(0, description="Index of starting depot location (default 0)")


class StopOutput(BaseModel):
    sequence_index: int
    name: str
    city: str
    latitude: float
    longitude: float
    is_start: bool = False


class RouteLeg(BaseModel):
    leg_number: int
    from_stop: str
    to_stop: str
    distance_km: float
    estimated_duration_minutes: int


class OptimizeRouteResponse(BaseModel):
    optimized_route: List[StopOutput]
    total_distance_km: float
    estimated_duration_minutes: int
    estimated_duration_formatted: str
    average_speed_kmh: float = 50.0
    legs: List[RouteLeg]
    algorithm: str = "Google OR-Tools TSP Solver"
    disclaimer: str = "Distance and duration estimates are computed using geographic coordinates assuming an average vehicle speed of 50 km/h. No live traffic or GPS data used."


class SupportedLocation(BaseModel):
    name: str
    city: str
    latitude: float
    longitude: float
    description: str
