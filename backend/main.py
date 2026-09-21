from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import joblib
import os
import urllib.parse
import urllib.request
import json

# =========================
# ENVIRONMENT
# =========================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# =========================
# APP
# =========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ML MODEL
# =========================

model = joblib.load("crop_model.pkl")

# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {
        "message": "PRAVA Backend is running!",
        "status": "online"
    }

# =========================
# CROP RECOMMENDATION
# =========================

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

Explain briefly why {prediction} is suitable.

Give two practical farming tips.

Keep the response short and farmer-friendly.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {
                    "why_recommended": {
                        "type": "string"
                    },
                    "tip_1": {
                        "type": "string"
                    },
                    "tip_2": {
                        "type": "string"
                    }
                },
                "required": [
                    "why_recommended",
                    "tip_1",
                    "tip_2"
                ]
            }
        }
    )

    return {
        "recommended_crop": prediction,
        "ai_advice": interaction.output_text
    }


# =========================
# DISEASE DIAGNOSIS
# =========================

@app.post("/disease-diagnosis")
async def disease_diagnosis(file: UploadFile = File(...)):

    image_bytes = await file.read()

    prompt = """
Analyze this crop or leaf image for agricultural disease diagnosis.

Return ONLY JSON with:

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

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=file.content_type or "image/jpeg"
    )

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=[
            image_part,
            prompt
        ],
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {
                    "crop": {
                        "type": "string"
                    },
                    "condition": {
                        "type": "string"
                    },
                    "symptoms": {
                        "type": "string"
                    },
                    "action_1": {
                        "type": "string"
                    },
                    "action_2": {
                        "type": "string"
                    }
                },
                "required": [
                    "crop",
                    "condition",
                    "symptoms",
                    "action_1",
                    "action_2"
                ]
            }
        }
    )

    return {
        "diagnosis": interaction.output_text,
        "model_used": "gemini-3.6-flash"
    }


# =========================
# WEATHER
# =========================

@app.get("/weather")
def get_weather(location: str):

    location = location.strip()

    candidates = [
        location,
        location.split(",")[0].strip(),
        location.split()[0].strip()
    ]

    place = None

    for candidate in candidates:

        if not candidate:
            continue

        encoded_location = urllib.parse.quote(candidate)

        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={encoded_location}"
            "&count=10"
            "&language=en"
            "&format=json"
        )

        try:

            with urllib.request.urlopen(geo_url) as response:
                geo_data = json.loads(response.read())

            results = geo_data.get("results", [])

            india_results = [
                r for r in results
                if r.get("country_code") == "IN"
            ]

            if india_results:
                place = india_results[0]
                break

            if results:
                place = results[0]
                break

        except Exception:
            continue

    if not place:
        return {
            "error": "Location not found"
        }

    latitude = place["latitude"]
    longitude = place["longitude"]

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current=temperature_2m,relative_humidity_2m,rain"
        "&timezone=auto"
    )

    with urllib.request.urlopen(weather_url) as response:
        weather_data = json.loads(response.read())

    current = weather_data["current"]

    return {
        "location": place["name"],
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "rainfall": current["rain"]
    }


# =========================
# AGRO ADVISORY
# =========================

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

Give practical advice for the farmer based on these conditions.

Return JSON with:

status:
Short overall farm condition.

advice_1:
One practical action.

advice_2:
One practical action.

warning:
One important warning.

Keep everything concise and farmer-friendly.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string"
                    },
                    "advice_1": {
                        "type": "string"
                    },
                    "advice_2": {
                        "type": "string"
                    },
                    "warning": {
                        "type": "string"
                    }
                },
                "required": [
                    "status",
                    "advice_1",
                    "advice_2",
                    "warning"
                ]
            }
        }
    )

    return {
        "advisory": interaction.output_text
    }