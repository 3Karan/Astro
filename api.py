import os
from dotenv import load_dotenv
import requests
import urllib.parse

load_dotenv()

CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")
CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")

def get_access_token():
    url = "https://api.prokerala.com/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_kundli(access_token, ayanamsa, coordinates, datetime_str):
    url = "https://api.prokerala.com/v2/astrology/kundli"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {
        "ayanamsa": ayanamsa,
        "coordinates": coordinates,
        "datetime": datetime_str,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_kundli_advanced(access_token, ayanamsa, coordinates, datetime_str):
    url = "https://api.prokerala.com/v2/astrology/kundli/advanced"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {
        "ayanamsa": ayanamsa,
        "coordinates": coordinates,
        "datetime": datetime_str,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_chart(access_token, ayanamsa, coordinates, datetime_str, chart_type, chart_style, format,
              la=None, upagraha_position=None):
    url = "https://api.prokerala.com/v2/astrology/chart"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {
        "ayanamsa": ayanamsa,
        "coordinates": coordinates,
        "datetime": datetime_str,
        "chart_type": chart_type,
        "chart_style": chart_style,
        "format": format
    }
    if la:
        params["la"] = la
    if upagraha_position:
        params["upagraha_position"] = upagraha_position
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.text
if __name__ == "__main__":
    access_token = get_access_token()
    # Example parameters
    ayanamsa = 1  # Lahiri
    coordinates = "23.1765,75.7885"
    datetime_str = "2022-03-17T10:50:40+00:00"
    # Encode datetime for URL safety (requests handles this, but for manual URLs use urllib.parse.quote)

    print("--- /v2/astrology/kundli ---")
    kundli = get_kundli(access_token, ayanamsa, coordinates, datetime_str)
    print(kundli)

    print("\n--- /v2/astrology/kundli/advanced ---")
    kundli_adv = get_kundli_advanced(access_token, ayanamsa, coordinates, datetime_str)
    print(kundli_adv)

    print("\n--- /v2/astrology/chart (SVG) ---")
    # Example: rasi chart, north-indian style, svg format
    chart_svg = get_chart(
        access_token,
        ayanamsa=ayanamsa,
        coordinates=coordinates,
        datetime_str=datetime_str,
        chart_type="rasi",
        chart_style="north-indian",
        format="svg"
    )
    print(chart_svg)