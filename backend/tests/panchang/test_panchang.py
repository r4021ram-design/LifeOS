import datetime
from unittest.mock import patch, MagicMock
import pytest
from app.services.pyswisseph_panchang import (
    calculate_precise_panchang,
    SwissEphProvider,
    FallbackProvider,
    SWISSEPH_AVAILABLE
)

# Test dates
TEST_DATES = [
    datetime.date(2026, 6, 18),  # Current Year
    datetime.date(2024, 2, 29),  # Leap Year 2024
    datetime.date(2028, 2, 29),  # Leap Year 2028
    datetime.date(2026, 8, 12),  # Solar Eclipse Date
    datetime.date(2026, 3, 3),   # Lunar Eclipse Date
    datetime.date(2026, 5, 31),  # Month boundary May
    datetime.date(2026, 6, 1),   # Month boundary June
]

# Test locations
TEST_LOCATIONS = [
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
    {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
]

def test_fallback_provider_calculation():
    provider = FallbackProvider()
    date_val = datetime.date(2026, 6, 18)
    panchang = provider.calculate_panchang(date_val, 28.6139, 77.2090)
    
    assert panchang["date"] == "2026-06-18"
    assert "tithi" in panchang
    assert "nakshatra" in panchang
    assert "yoga" in panchang
    assert "karana" in panchang
    assert "sunrise" in panchang
    assert "sunset" in panchang
    assert isinstance(panchang["festivals"], list)
    assert len(panchang["muhurats"]) > 0

def test_fallback_provider_all_locations_and_dates():
    provider = FallbackProvider()
    for dt in TEST_DATES:
        for loc in TEST_LOCATIONS:
            res = provider.calculate_panchang(dt, loc["lat"], loc["lon"])
            assert res["date"] == dt.isoformat()
            assert "tithi" in res
            assert "sunrise" in res
            assert "sunset" in res

def test_swisseph_provider_not_loaded_error():
    # When SWISSEPH_AVAILABLE is False, SwissEphProvider should raise RuntimeError
    with patch("app.services.pyswisseph_panchang.SWISSEPH_AVAILABLE", False):
        provider = SwissEphProvider()
        with pytest.raises(RuntimeError, match="Swiss Ephemeris wrapper is not loaded."):
            provider.calculate_panchang(datetime.date(2026, 6, 18), 28.61, 77.20)

def test_swisseph_provider_mocked_all_locations_and_dates():
    mock_swe = MagicMock()
    mock_swe.SUN = 0
    mock_swe.MOON = 1
    mock_swe.julday.return_value = 2451545.25
    
    # We will test different angles to hit all festival rules in SwissEphProvider:
    # 1. Purnima: diff_long = 168 (14 * 12 = 168) -> sun=0, moon=168
    # 2. Amavasya: diff_long = 348 (29 * 12 = 348) -> sun=0, moon=348
    # 3. Ekadashi: diff_long = 120 (10 * 12 = 120) -> sun=0, moon=120
    # 4. Sankashti Chaturthi: diff_long = 216 (18 * 12 = 216) -> sun=0, moon=216
    angle_cases = [168.0, 348.0, 120.0, 216.0]
    
    for angle in angle_cases:
        def calc_ut_mock(jd, body):
            if body == 0:  # SUN
                return (0.0, 0, 0, 0, 0, 0)
            else:  # MOON
                return (angle, 0, 0, 0, 0, 0)
        
        mock_swe.calc_ut.side_effect = calc_ut_mock
        
        with patch("app.services.pyswisseph_panchang.SWISSEPH_AVAILABLE", True):
            with patch("app.services.pyswisseph_panchang.swe", mock_swe, create=True):
                provider = SwissEphProvider()
                
                for dt in TEST_DATES:
                    for loc in TEST_LOCATIONS:
                        res = provider.calculate_panchang(dt, loc["lat"], loc["lon"])
                        assert res["date"] == dt.isoformat()
                        assert "tithi" in res
                        assert "sunrise" in res
                        assert "sunset" in res
                        
                        # Assert specific festival mappings based on diff_long
                        if angle == 168.0:
                            assert "Purnima Vrat" in res["festivals"]
                        elif angle == 348.0:
                            assert "Amavasya Pitru Tarpan" in res["festivals"]
                        elif angle == 120.0:
                            assert "Ekadashi Vrat" in res["festivals"]
                        elif angle == 216.0:
                            assert "Sankashti Chaturthi" in res["festivals"]

def test_precise_router_falls_back():
    date_val = datetime.date(2026, 6, 18)
    with patch("app.services.pyswisseph_panchang.SWISSEPH_AVAILABLE", False):
        panchang = calculate_precise_panchang(date_val, 28.6139, 77.2090)
        assert panchang["date"] == "2026-06-18"
        assert "tithi" in panchang

def test_router_fallback_on_exception():
    mock_swe = MagicMock()
    mock_swe.julday.side_effect = Exception("SwissEph C Error")
    
    with patch("app.services.pyswisseph_panchang.SWISSEPH_AVAILABLE", True):
        with patch("app.services.pyswisseph_panchang.swe", mock_swe, create=True):
            res = calculate_precise_panchang(datetime.date(2026, 6, 18), 28.61, 77.20)
            assert res is not None
            assert "tithi" in res

def test_api_panchang_endpoint_success(client):
    response = client.get("/api/v1/panchang/?date_str=2026-06-18&lat=28.6&lon=77.2")
    assert response.status_code == 200
    data = response.json()
    assert "tithi" in data
    assert data["date"] == "2026-06-18"

def test_api_panchang_endpoint_invalid_date(client):
    response = client.get("/api/v1/panchang/?date_str=invalid-date")
    assert response.status_code == 200
    data = response.json()
    assert "tithi" in data

def test_api_panchang_endpoint_no_date(client):
    response = client.get("/api/v1/panchang/")
    assert response.status_code == 200
    data = response.json()
    assert "tithi" in data
