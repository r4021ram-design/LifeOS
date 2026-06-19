from fastapi import APIRouter, Query, status
import datetime
from app.services.pyswisseph_panchang import calculate_precise_panchang
from app.schemas.schemas import PanchangResponse

router = APIRouter(prefix="/panchang", tags=["panchang"])

@router.get("/", response_model=PanchangResponse)
def get_panchang(
    date_str: str = Query(None, description="ISO Date format YYYY-MM-DD"),
    lat: float = Query(28.6139, description="Latitude of location (default New Delhi)"),
    lon: float = Query(77.2090, description="Longitude of location (default New Delhi)")
):
    if date_str:
        try:
            target_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            target_date = datetime.date.today()
    else:
        target_date = datetime.date.today()

    # Call the high-precision calculator
    panchang_data = calculate_precise_panchang(target_date, lat, lon)
    return panchang_data
