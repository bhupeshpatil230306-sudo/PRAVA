from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
from google import genai
from google.genai import types
import os
import urllib.parse
import urllib.request
import json

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("crop_model.pkl")


class CropRequest(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float


@app.get("/")
def home():
    return {"message": "PRAVA Backend is running!"}

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

The ML model recommends: {prediction}

Farm conditions:
Nitrogen: {data.N}
Phosphorus: {data.P}
Potassium: {data.K}
Temperature: {data.temperature} °C
Humidity: {data.humidity} %
Soil pH: {data.ph}
Rainfall: {data.rainfall} mm

Explain why {prediction} is suitable based on these conditions.

Return ONLY valid JSON:
{{
  "why_recommended": "short farmer-friendly explanation",
  "tip_1": "one practical farming tip",
  "tip_2": "one practical farming tip"
}}

Keep the response concise.
"""

    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return {
        "recommended_crop": prediction,
        "ai_advice": response.output_text
    }
@app.post("/disease-diagnosis")
async def disease_diagnosis(file: UploadFile = File(...)):

    image_bytes = await file.read()

    from google.genai import types

    prompt = """
Analyze this crop/leaf image for agricultural disease diagnosis.

Return ONLY valid JSON with:
{
  "crop": "crop name",
  "condition": "disease name or Healthy",
  "symptoms": "short description",
  "action_1": "practical action",
  "action_2": "practical action"
}

Keep every value short and farmer-friendly.
If something cannot be identified, use "Unclear".
"""

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "crop": {"type": "STRING"},
                "condition": {"type": "STRING"},
                "symptoms": {"type": "STRING"},
                "action_1": {"type": "STRING"},
                "action_2": {"type": "STRING"}
            },
            "required": [
                "crop",
                "condition",
                "symptoms",
                "action_1",
                "action_2"
            ]
        },
        max_output_tokens=200
    )

    models = [
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.6-flash"
    ]

    last_error = None

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=file.content_type
                    ),
                    prompt
                ],
                config=config
            )

            return {
                "diagnosis": response.text,
                "model_used": model_name
            }

        except Exception as e:
            last_error = e
            continue

    return {
        "diagnosis": "AI service is temporarily unavailable. Please try again shortly.",
        "error": str(last_error)
    }


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

Return ONLY JSON:
{{
  "status": "short overall condition",
  "advice_1": "one practical action",
  "advice_2": "one practical action",
  "warning": "one important warning"
}}

Keep it under 100 words.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=180
        )
    )

    return {
        "advisory": response.text
    }

@app.get("/weather")
def get_weather(location: str):

    location = location.strip()

    # Try multiple location formats
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
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?name={encoded_location}"
            f"&count=10"
            f"&language=en"
            f"&format=json"
        )

        try:
            with urllib.request.urlopen(geo_url) as response:
                geo_data = json.loads(response.read())

            results = geo_data.get("results", [])

            # Prefer India
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
        return {"error": "Location not found"}

    latitude = place["latitude"]
    longitude = place["longitude"]

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,rain"
        f"&timezone=auto"
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
