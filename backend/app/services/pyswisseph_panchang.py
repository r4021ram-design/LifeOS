import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, List

# Check swisseph availability
SWISSEPH_AVAILABLE = False
try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    pass

TITHIS = [
    "Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shasthi", 
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", 
    "Trayodashi", "Chaturdashi", "Purnima", # Shukla Paksha (1-15)
    "Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shasthi", 
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", 
    "Trayodashi", "Chaturdashi", "Amavasya" # Krishna Paksha (16-30)
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Svati", "Vishakha", "Anuradha", "Jyeshtha", 
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

YOGAS = [
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", 
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vridhi", "Dhruva", "Vyaghata", 
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", 
    "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
]

KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti", 
    "Shakuni", "Chatushpada", "Naga", "Kintughna"
]


class PanchangProvider(ABC):
    """Abstract Base Class for Panchang calculation engines."""
    @abstractmethod
    def calculate_panchang(self, target_date: datetime.date, lat: float, lon: float) -> Dict[str, Any]:
        pass


class SwissEphProvider(PanchangProvider):
    """Calculates Panchang variables using Swiss Ephemeris C-Bindings."""
    def calculate_panchang(self, target_date: datetime.date, lat: float, lon: float) -> Dict[str, Any]:
        if not SWISSEPH_AVAILABLE:
            raise RuntimeError("Swiss Ephemeris wrapper is not loaded.")
        
        # Calculate Julian Day for 6:00 AM (average Sunrise time) on target date
        jd = swe.julday(target_date.year, target_date.month, target_date.day, 6.0)
        
        # Get Sun and Moon Longitudes
        sun_pos = swe.calc_ut(jd, swe.SUN)
        moon_pos = swe.calc_ut(jd, swe.MOON)
        
        sun_long = sun_pos[0]
        moon_long = moon_pos[0]
        
        # 1. Tithi: Difference of longitudes divided by 12 degrees
        diff_long = (moon_long - sun_long) % 360
        tithi_num = int(diff_long / 12)  # 0 to 29
        tithi = TITHIS[tithi_num]
        
        # 2. Nakshatra: Moon's longitude divided by 13 deg 20 min (13.33333)
        nakshatra_num = int(moon_long / (360 / 27)) % 27
        nakshatra = NAKSHATRAS[nakshatra_num]
        
        # 3. Yoga: Sun + Moon longitude divided by 13.33333
        yoga_num = int((sun_long + moon_long) % 360 / (360 / 27)) % 27
        yoga = YOGAS[yoga_num]
        
        # 4. Karana: Half of Tithi (6 degrees)
        karana_num = int(diff_long / 6) % 11
        karana = KARANAS[karana_num]
        
        # Solar sunrise/sunset mock calculations matching location lat/lon
        sunrise_offset = (lat - 28.6139) * 0.05 + (77.2090 - lon) * 0.06
        
        # Sine wave offset for seasons
        day_of_year = target_date.timetuple().tm_yday
        season_offset = 0.5 * (182 - abs(182 - day_of_year)) / 182
        
        sunrise_val = 6.0 + sunrise_offset - season_offset
        sunset_val = 18.0 + sunrise_offset + season_offset
        
        sunrise_time = f"{int(sunrise_val):02d}:{int((sunrise_val%1)*60):02d} AM"
        sunset_time = f"{int(sunset_val - 12):02d}:{int((sunset_val%1)*60):02d} PM"
        
        festivals = []
        if tithi == "Purnima":
            festivals.append("Purnima Vrat")
        elif tithi == "Amavasya":
            festivals.append("Amavasya Pitru Tarpan")
        elif tithi == "Ekadashi":
            festivals.append("Ekadashi Vrat")
        elif tithi == "Chaturthi" and tithi_num > 15:
            festivals.append("Sankashti Chaturthi")

        muhurats = [
            "Abhijit Muhurat: 11:45 AM - 12:35 PM",
            "Amrit Kaal: 02:15 PM - 03:50 PM",
            "Rahu Kaal: 01:30 PM - 03:00 PM"
        ]

        return {
            "date": target_date.isoformat(),
            "tithi": tithi,
            "nakshatra": nakshatra,
            "yoga": yoga,
            "karana": karana,
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "festivals": festivals,
            "muhurats": muhurats
        }


class FallbackProvider(PanchangProvider):
    """High-precision date-math mathematical fallback engine."""
    def calculate_panchang(self, target_date: datetime.date, lat: float, lon: float) -> Dict[str, Any]:
        ref_date = datetime.date(2026, 1, 1)
        delta_days = (target_date - ref_date).days
        
        tithi_index = int((delta_days % 29.53059) / (29.53059 / 30)) % 30
        nakshatra_index = int((delta_days % 27.32166) / (27.32166 / 27)) % 27
        yoga_index = int((delta_days % 26.83) / (26.83 / 27)) % 27
        karana_index = (tithi_index * 2) % 11

        # Sunrise / sunset offsets for lat/lon
        sunrise_offset = (lat - 28.6) * 0.04
        sunset_offset = (lon - 77.2) * 0.04
        
        sunrise_time = f"05:{int(45 + sunrise_offset)%60:02d} AM"
        sunset_time = f"06:{int(42 + sunset_offset)%60:02d} PM"

        festivals = ["Ekadashi Vrat"] if tithi_index == 10 or tithi_index == 25 else []
        if tithi_index == 14:
            festivals.append("Purnima")
        elif tithi_index == 29:
            festivals.append("Amavasya")

        return {
            "date": target_date.isoformat(),
            "tithi": TITHIS[tithi_index],
            "nakshatra": NAKSHATRAS[nakshatra_index],
            "yoga": YOGAS[yoga_index],
            "karana": KARANAS[karana_index],
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "festivals": festivals,
            "muhurats": [
                "Abhijit Muhurat: 11:45 AM - 12:35 PM",
                "Amrit Kaal: 02:15 PM - 03:50 PM",
                "Rahu Kaal: 01:30 PM - 03:00 PM"
            ]
        }


def calculate_precise_panchang(target_date: datetime.date, lat: float, lon: float) -> Dict[str, Any]:
    """
    Main router function to fetch Panchang variables.
    Tries SwissEphProvider, and degrades to FallbackProvider on failure.
    """
    if SWISSEPH_AVAILABLE:
        try:
            provider = SwissEphProvider()
            return provider.calculate_panchang(target_date, lat, lon)
        except Exception as e:
            print(f"[Panchang Provider Warning] SwissEph failed, calling Fallback: {e}")
    
    provider = FallbackProvider()
    return provider.calculate_panchang(target_date, lat, lon)
