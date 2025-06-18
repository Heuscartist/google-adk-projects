import requests
from typing import List, Dict, Union
import os
from dotenv import load_dotenv
from pathlib import Path


env_path= Path(__file__).resolve().parent.parent / '.env'

load_dotenv(dotenv_path=env_path)

FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

def get_current_location_tool() -> Dict[str, Union[float, str]]:
    """
    Retrieves the user's current geographical location (latitude and longitude) and location name
    based on their IP address using ipinfo.io.

    Returns:
        dict: A dictionary containing:
            - 'latitude' (float)
            - 'longitude' (float)
            - 'location_name' (str): Formatted as 'City, Region, Country'
        If an error occurs, returns a dictionary with an 'error' key.
    """
    try:
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()
        data = response.json()
        
        lat, lon = map(float, data["loc"].split(","))
        city = data.get("city", "")
        region = data.get("region", "")
        country = data.get("country", "")
        location_name = ", ".join(filter(None, [city, region, country]))

        return {
            "latitude": lat,
            "longitude": lon,
            "location_name": location_name
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Network or API error: {e}"}
    except KeyError:
        return {"error": "Could not parse location data from API response."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


def get_location_from_prompt_tool(prompt: str) -> Dict[str, Union[str, float]]:
    """
    Converts a location name into latitude/longitude using Nominatim API.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": prompt, "format": "json"}
        headers = {
            "User-Agent": "Restaurant Finder/1.0 (adil.mubashir@gmail.com)"  # <-- Required
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return {
                "latitude": lat,
                "longitude": lon,
                "display_name": data[0]["display_name"]
            }
        else:
            return {"error": "No location found for the prompt."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network or API error: {e}"}
    except (IndexError, KeyError):
        return {"error": "Could not parse location data from API response."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


def find_restaurants_tool(lat: float, lon: float, cuisine: str) -> Union[List[Dict[str, Union[str, float]]], Dict[str, str]]:
    """
    Finds restaurants of a specific cuisine type near the given coordinates using Foursquare Places API.
    
    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        cuisine (str): Type of cuisine or keyword (e.g. 'Chinese', 'Pizza').
    
    Returns:
        List of restaurant dicts or a dict with a message/error.
    """
    try:
        headers = {
            "Accept": "application/json",
            "Authorization": FOURSQUARE_API_KEY
        }

        params = {
            "ll": f"{lat},{lon}",
            "query": cuisine if cuisine else "restaurant",
            "limit": 10,
            "radius": 1000  # in meters
        }

        url = "https://api.foursquare.com/v3/places/search"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for place in data.get('results', []):
            results.append({
                "name": place.get('name', 'Unknown'),
                "latitude": place.get('geocodes', {}).get('main', {}).get('latitude'),
                "longitude": place.get('geocodes', {}).get('main', {}).get('longitude'),
                "address": place.get('location', {}).get('formatted_address', 'No address')
            })

        return results if results else {"message": f"No {cuisine} restaurants found nearby."}
    except Exception as e:
        return {"error": str(e)}