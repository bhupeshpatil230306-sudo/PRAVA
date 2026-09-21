from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import joblib
import os
import urllib.parse
import urllib.request
import json
import base64

# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_MODEL = "gemini-3.6-flash"

# =========================================================
# APP
# =========================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# ML MODEL
# =========================================================

model = joblib.load("crop_model.pkl")


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "PRAVA Backend is running!",
        "status": "online"
    }


# =========================================================
# CROP RECOMMENDATION
# =========================================================

class CropRequest(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float


@app.post("/crop-recommendation")
def crop_recommendation(data: CropRequest):

    features = [[
        data.N,
        data.P,
        data.K,
        data.temperature,
        data.humidity,
        data.ph,
        data.rainfall
    ]]

    prediction = model.predict(features)[0]

    prompt = f"""
You are PRAVA, an AI agricultural advisor for Indian farmers.

The machine learning model recommends: {prediction}

Farm conditions:
Nitrogen: {data.N}
Phosphorus: {data.P}
Potassium: {data.K}
Temperature: {data.temperature} °C
Humidity: {data.humidity} %
Soil pH: {data.ph}
Rainfall: {data.rainfall} mm

Explain briefly why this crop is suitable.

Return ONLY valid JSON:

{{
  "why_recommended": "short explanation",
  "tip_1": "one practical farming tip",
  "tip_2": "one practical farming tip"
}}

Keep it short and farmer-friendly.
"""

    try:
        response = client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt
        )

        ai_text = response.output_text

    except Exception as e:
        print("Gemini Crop Error:", e)

        ai_text = json.dumps({
            "why_recommended": (
                f"{prediction} was selected by PRAVA's crop recommendation "
                "model based on the provided soil and climate conditions."
            ),
            "tip_1": "Monitor soil moisture regularly.",
            "tip_2": "Adjust fertilizer use according to soil conditions."
        })

    return {
        "recommended_crop": prediction,
        "ai_advice": ai_text
    }


# =========================================================
# DISEASE DIAGNOSIS
# =========================================================

@app.post("/disease-diagnosis")
async def disease_diagnosis(file: UploadFile = File(...)):

    image_bytes = await file.read()

    mime_type = file.content_type or "image/jpeg"

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """
Analyze this crop/leaf image for agricultural disease diagnosis.

Return ONLY valid JSON:

{
  "crop": "crop name",
  "condition": "disease name or Healthy",
  "symptoms": "short description",
  "action_1": "practical action",
  "action_2": "practical action"
}

Keep every value short and farmer-friendly.

If the crop or condition cannot be identified reliably,
use "Unclear".
"""

    try:
        response = client.interactions.create(
            model=GEMINI_MODEL,
            input=[
                {
                    "type": "image",
                    "mime_type": mime_type,
                    "data": image_base64
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        )

        diagnosis = response.output_text

    except Exception as e:
        print("Gemini Disease Error:", e)

        diagnosis = json.dumps({
            "crop": "Unclear",
            "condition": "Unable to analyze",
            "symptoms": "AI diagnosis is temporarily unavailable.",
            "action_1": "Inspect the crop manually for visible symptoms.",
            "action_2": "Consult a local agricultural expert if symptoms continue."
        })

    return {
        "diagnosis": diagnosis,
        "model_used": GEMINI_MODEL
    }


# =========================================================
# WEATHER
# =========================================================

@app.get("/weather")
def get_weather(location: str):

    location = location.strip()

    if not location:
        return {"error": "Please enter a location"}

    # -----------------------------------------------------
    # 1. GEOCODING
    # -----------------------------------------------------

    params = urllib.parse.urlencode({
        "name": location,
        "count": 10,
        "language": "en",
        "format": "json",
        "countryCode": "IN"
    })

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?{params}"

    try:

        request = urllib.request.Request(
            geo_url,
            headers={
                "User-Agent": "PRAVA-Agricultural-Intelligence/1.0"
            }
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            geo_data = json.loads(response.read().decode("utf-8"))

        results = geo_data.get("results", [])

    except Exception as e:

        print("Geocoding error:", repr(e))

        return {
            "error": "Unable to search this location"
        }

    if not results:
        return {
            "error": f"Location '{location}' not found. Try a city name such as Pune or Kochi."
        }

    # First Indian matching result
    place = results[0]

    latitude = place["latitude"]
    longitude = place["longitude"]

    # -----------------------------------------------------
    # 2. WEATHER
    # -----------------------------------------------------

    weather_params = urllib.parse.urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,rain",
        "timezone": "auto"
    })

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?{weather_params}"
    )

    try:

        request = urllib.request.Request(
            weather_url,
            headers={
                "User-Agent": "PRAVA-Agricultural-Intelligence/1.0"
            }
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            weather_data = json.loads(response.read().decode("utf-8"))

        current = weather_data["current"]

        return {
            "location": place.get("name", location),
            "state": place.get("admin1", ""),
            "country": place.get("country", "India"),
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "rainfall": current["rain"]
        }

    except Exception as e:

        print("Weather error:", repr(e))

        return {
            "error": "Weather service unavailable"
        }
# =========================================================
# AGRO ADVISORY
# =========================================================

class AdvisoryRequest(BaseModel):
    crop: str
    location: str
    temperature: float
    humidity: float
    rainfall: float


@app.post("/agro-advisory")
def agro_advisory(data: AdvisoryRequest):

    prompt = f"""
You are PRAVA, an AI agricultural advisor for Indian farmers.

Crop: {data.crop}
Location: {data.location}
Temperature: {data.temperature} °C
Humidity: {data.humidity} %
Rainfall: {data.rainfall} mm

Give practical advice based on these conditions.

Return ONLY valid JSON:

{{
  "status": "short overall condition",
  "advice_1": "one practical action",
  "advice_2": "one practical action",
  "warning": "one important warning"
}}

Keep it short and farmer-friendly.
"""

    try:

        response = client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt
        )

        advisory = response.output_text

    except Exception as e:

        print("Gemini Advisory Error:", e)

        advisory = json.dumps({
            "status": "Farm conditions analyzed",
            "advice_1": (
                f"Monitor {data.crop} closely according to current weather."
            ),
            "advice_2": (
                "Maintain appropriate soil moisture and avoid unnecessary irrigation."
            ),
            "warning": (
                "Weather conditions can change quickly; check local forecasts regularly."
            )
        })

    return {
        "advisory": advisory
    }