import requests
from .config import GEOCODE_API_KEY

def get_country_code(location: str) -> str:
    """Get ISO country code from location name."""
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={GEOCODE_API_KEY}"
    resp = requests.get(url).json()
    if resp.get("results"):
        return resp["results"][0]["components"].get("country_code", "").upper()
    return None
