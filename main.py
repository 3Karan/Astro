from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kundli_calculator import KundliCalculator

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
