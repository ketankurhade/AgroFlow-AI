from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User
from app.schemas.route import (
    OptimizeRouteRequest,
    OptimizeRouteResponse,
    SupportedLocation
)
from app.services.route_service import (
    AGROFLOW_LOCATIONS,
    resolve_location,
    solve_route_optimization
)
from app.services.auth_service import require_roles

router = APIRouter(prefix="/routes", tags=["Route Optimization"])


@router.get("/locations", response_model=List[SupportedLocation])
def get_supported_locations(
    current_user: User = Depends(require_roles("admin", "distributor", "supply_chain_manager"))
):
    """
    Returns the list of controlled AgroFlow MVP locations with latitude/longitude coordinates.
    """
    result = []
    for loc_name, details in AGROFLOW_LOCATIONS.items():
        result.append(
            SupportedLocation(
                name=loc_name,
                city=details["city"],
                latitude=details["latitude"],
                longitude=details["longitude"],
                description=details["description"]
            )
        )
    return result


@router.post("/optimize", response_model=OptimizeRouteResponse)
def optimize_route(
    payload: OptimizeRouteRequest,
    current_user: User = Depends(require_roles("admin", "distributor"))
):
    """
    Accepts a list of delivery locations/stops and uses Google OR-Tools to solve the Traveling
    Salesperson Problem (TSP) to calculate an efficient visit sequence, distances, and duration.
    """
    if not payload.stops or len(payload.stops) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 delivery stops are required to perform route optimization."
        )

    resolved_stops = []
    for stop_input in payload.stops:
        try:
            resolved = resolve_location(
                name=stop_input.name,
                latitude=stop_input.latitude,
                longitude=stop_input.longitude
            )
            resolved_stops.append(resolved)
        except ValueError as ve:
            supported_names = ", ".join(list(AGROFLOW_LOCATIONS.keys()))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{str(ve)} Supported locations: {supported_names}"
            )

    try:
        result = solve_route_optimization(
            resolved_stops=resolved_stops,
            start_index=payload.start_location_index or 0
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route optimization failed: {str(e)}"
        )

