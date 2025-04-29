from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from kundli_calculator import KundliCalculator
from api import get_access_token, get_kundli, get_kundli_advanced, get_chart

app = FastAPI()
kundli_calc = KundliCalculator()

class KundliRequest(BaseModel):
    dob: str  # Format: YYYY-MM-DD
    tob: str  # Format: HH:MM:SS
    place: str

from fastapi import Body

@app.post("/generate_kundli", summary="Generate Kundli", response_description="Kundli details", tags=["Kundli"])
def generate_kundli(
    req: KundliRequest = Body(
        ..., 
        example={
            "dob": "1990-01-01",
            "tob": "10:30:00",
            "place": "Delhi, India"
        }
    )
):
    try:
        kundli = kundli_calc.calculate_kundli(req.dob, req.tob, req.place)
        return {"success": True, "kundli": kundli}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{str(e)}\nTraceback:\n{tb}")

@app.get("/prokerala/kundli", summary="Prokerala Basic Kundli", tags=["Prokerala"])
def prokerala_kundli(
    ayanamsa: int = Query(1, description="Ayanamsa system: 1=Lahiri, 3=Raman, 5=KP"),
    coordinates: str = Query(..., description="Latitude,Longitude e.g. 23.1765,75.7885"),
    datetime_str: str = Query(..., description="ISO datetime e.g. 2022-03-17T10:50:40+00:00")
):
    try:
        access_token = get_access_token()
        result = get_kundli(access_token, ayanamsa, coordinates, datetime_str)
        return {"success": True, "data": result}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{str(e)}\nTraceback:\n{tb}")

@app.get("/prokerala/kundli-advanced", summary="Prokerala Advanced Kundli", tags=["Prokerala"])
def prokerala_kundli_advanced(
    ayanamsa: int = Query(1, description="Ayanamsa system: 1=Lahiri, 3=Raman, 5=KP"),
    coordinates: str = Query(..., description="Latitude,Longitude e.g. 23.1765,75.7885"),
    datetime_str: str = Query(..., description="ISO datetime e.g. 2022-03-17T10:50:40+00:00")
):
    try:
        access_token = get_access_token()
        result = get_kundli_advanced(access_token, ayanamsa, coordinates, datetime_str)
        return {"success": True, "data": result}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{str(e)}\nTraceback:\n{tb}")

@app.get("/prokerala/chart", summary="Prokerala SVG Chart (JSON)", tags=["Prokerala"])
def prokerala_chart(
    ayanamsa: int = Query(1, description="Ayanamsa system: 1=Lahiri, 3=Raman, 5=KP"),
    coordinates: str = Query("23.1765,75.7885", description="Latitude,Longitude e.g. 23.1765,75.7885"),
    datetime_str: str = Query(
        "2022-03-17T10:50:40+00:00",
        description="ISO datetime e.g. 2022-03-17T10:50:40+00:00 (use + in API calls, %2B in browser URLs)"
    ),
    chart_type: str = Query("rasi", description="Chart type, e.g. rasi, navamsa, lagna, etc."),
    chart_style: str = Query("north-indian", description="Chart style: north-indian, south-indian, east-indian"),
    format: str = Query("svg", description="Output format, only svg supported"),
    la: str = Query(None, description="Language: en, hi, ta, te, ml", alias="la"),
    upagraha_position: str = Query(None, description="Upagraha position: start, middle, end", alias="upagraha_position"),
    request: Request = None
):
    try:
        access_token = get_access_token()
        svg = get_chart(
            access_token,
            ayanamsa=ayanamsa,
            coordinates=coordinates,
            datetime_str=datetime_str,
            chart_type=chart_type,
            chart_style=chart_style,
            format=format,
            la=la,
            upagraha_position=upagraha_position
        )
        # Construct direct view URL using actual user-provided values
        import urllib.parse
        base_url = str(request.base_url) if request else "http://localhost:8000/"
        params = {
            "ayanamsa": ayanamsa,
            "coordinates": coordinates,
            "datetime_str": datetime_str,
            "chart_type": chart_type,
            "chart_style": chart_style,
            "format": format
        }
        if la:
            params["la"] = la
        if upagraha_position:
            params["upagraha_position"] = upagraha_position
        view_url = base_url.rstrip("/") + "/prokerala/chart-view?" + urllib.parse.urlencode(params)
        return {"svg": svg, "view_url": view_url}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{str(e)}\nTraceback:\n{tb}")

# /prokerala/chart-view endpoint with no .replace logic
from fastapi.responses import HTMLResponse
@app.get("/prokerala/chart-view", summary="Prokerala SVG Chart (HTML view)", tags=["Prokerala"])
def prokerala_chart_view(
    ayanamsa: int = Query(1),
    coordinates: str = Query("23.1765,75.7885"),
    datetime_str: str = Query("2022-03-17T10:50:40+00:00"),
    chart_type: str = Query("rasi"),
    chart_style: str = Query("north-indian"),
    format: str = Query("svg"),
    la: str = Query(None),
    upagraha_position: str = Query(None)
):
    try:
        access_token = get_access_token()
        svg = get_chart(
            access_token,
            ayanamsa=ayanamsa,
            coordinates=coordinates,
            datetime_str=datetime_str,
            chart_type=chart_type,
            chart_style=chart_style,
            format=format,
            la=la,
            upagraha_position=upagraha_position
        )
        html = f"""
        <html>
        <head>
            <title>Prokerala Chart</title>
            <style>
                body {{ text-align: center; margin-top: 40px; }}
                svg {{ border: 1px solid #aaa; background: #fff; }}
            </style>
        </head>
        <body>
            <h2>Prokerala SVG Chart</h2>
            {svg}
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{str(e)}\nTraceback:\n{tb}")
