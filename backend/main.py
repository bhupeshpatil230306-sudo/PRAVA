from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import joblib
import os
import urllib.parse
import urllib.request
import urllib.error
import json
import base64
import time


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

# Stable, low-cost, multimodal Gemini model
GEMINI_MODEL = "gemini-3.5-flash-lite"

# 30-second client timeout
client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"timeout": 30000}
)


# =========================================================
# APP
# =========================================================

app = FastAPI(title="PRAVA Agricultural Intelligence")


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
        "status": "online",
        "gemini_model": GEMINI_MODEL
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

    # ML prediction
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
            input=prompt,
            generation_config={
                "thinking_level": "minimal"
            }
        )

        ai_text = response.output_text.strip()

    except Exception as e:
        print("Gemini Crop Error:", repr(e))

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
        "ai_advice": ai_text,
        "model_used": GEMINI_MODEL
    }


# =========================================================
# DISEASE DIAGNOSIS
# =========================================================

@app.post("/disease-diagnosis")
async def disease_diagnosis(file: UploadFile = File(...)):

    image_bytes = await file.read()

    if not image_bytes:
        return {
            "diagnosis": {
                "crop": "Unknown",
                "condition": "Invalid image",
                "symptoms": "No image data was received.",
                "action_1": "Upload a valid crop or leaf image.",
                "action_2": "Try a clear, well-lit image."
            },
            "model_used": GEMINI_MODEL
        }

    mime_type = file.content_type or "image/jpeg"

    # Make sure the uploaded file is actually an image
    if not mime_type.startswith("image/"):
        return {
            "diagnosis": {
                "crop": "Unknown",
                "condition": "Invalid file",
                "symptoms": "The uploaded file is not an image.",
                "action_1": "Upload a JPG, JPEG, PNG or other image.",
                "action_2": "Try uploading a clear crop leaf photo."
            },
            "model_used": GEMINI_MODEL
        }

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """
Analyze this crop or leaf image carefully.

Identify:
- crop name
- visible disease or healthy condition
- visible symptoms
- two practical actions

Return ONLY a JSON object.

Required format:

{
  "crop": "crop name",
  "condition": "disease name or Healthy",
  "symptoms": "short description of visible symptoms",
  "action_1": "practical action",
  "action_2": "practical action"
}

Rules:
- If the crop cannot be identified reliably, use "Unknown".
- If no disease is visible, use "Healthy".
- Do not use markdown.
- Do not use ```json.
- Do not add explanation outside the JSON.
- Keep the response short and practical.
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
            ],
            generation_config={
                "thinking_level": "minimal"
            }
        )

        raw_text = response.output_text.strip()

        # Remove markdown fences if model adds them
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "")
            raw_text = raw_text.replace("```", "")
            raw_text = raw_text.strip()

        diagnosis = json.loads(raw_text)

        diagnosis = {
            "crop": diagnosis.get("crop", "Unknown"),
            "condition": diagnosis.get("condition", "Unclear"),
            "symptoms": diagnosis.get(
                "symptoms",
                "No clear symptoms identified."
            ),
            "action_1": diagnosis.get(
                "action_1",
                "Monitor the crop regularly."
            ),
            "action_2": diagnosis.get(
                "action_2",
                "Consult a local agricultural expert if symptoms continue."
            )
        }

    except Exception as e:

        print("Gemini Disease Error:", repr(e))

        diagnosis = {
            "crop": "Unknown",
            "condition": "Unable to analyze",
            "symptoms": "AI diagnosis is temporarily unavailable.",
            "action_1": "Inspect the crop manually for visible symptoms.",
            "action_2": (
                "Consult a local agricultural expert if symptoms continue."
            )
        }

    return {
        "diagnosis": diagnosis,
        "model_used": GEMINI_MODEL
    }


# =========================================================
# WEATHER HELPERS
# =========================================================

def open_meteo_request(url, retries=2):

    for attempt in range(retries + 1):

        try:

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "PRAVA-Agricultural-Intelligence/1.0"
                }
            )

            with urllib.request.urlopen(request, timeout=10) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as e:

            print(
                f"Weather HTTP error attempt {attempt + 1}: "
                f"{e.code}"
            )

            if e.code == 429 and attempt < retries:
                time.sleep(2 ** attempt)
                continue

            raise

        except Exception as e:

            print(
                f"Weather request error attempt {attempt + 1}: "
                f"{repr(e)}"
            )

            if attempt < retries:
                time.sleep(1)
                continue

            raise

    return None


def wttr_weather(location):

    encoded_location = urllib.parse.quote(location)

    url = (
        f"https://wttr.in/{encoded_location}"
        "?format=j1"
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "PRAVA-Agricultural-Intelligence/1.0"
        }
    )

    with urllib.request.urlopen(request, timeout=10) as response:

        data = json.loads(
            response.read().decode("utf-8")
        )

    current = data["current_condition"][0]

    return {
        "location": location,
        "state": "",
        "country": "India",
        "temperature": float(
            current["temp_C"]
        ),
        "humidity": float(
            current["humidity"]
        ),
        "rainfall": float(
            current.get("precipMM", 0)
        ),
        "source": "wttr.in"
    }


# =========================================================
# WEATHER
# =========================================================

@app.get("/weather")
def get_weather(location: str):

    location = location.strip()

    if not location:
        return {
            "error": "Please enter a location"
        }

    # -----------------------------------------------------
    # 1. GEOCODING WITH OPEN-METEO
    # -----------------------------------------------------

    params = urllib.parse.urlencode({
        "name": location,
        "count": 10,
        "language": "en",
        "format": "json",
        "countryCode": "IN"
    })

    geo_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?{params}"
    )

    try:

        geo_data = open_meteo_request(
            geo_url,
            retries=2
        )

        results = geo_data.get(
            "results",
            []
        )

    except Exception as e:

        print(
            "Geocoding failed:",
            repr(e)
        )

        # Try wttr directly if geocoding fails
        try:
            return wttr_weather(location)

        except Exception as wttr_error:

            print(
                "WTTR fallback failed:",
                repr(wttr_error)
            )

            return {
                "error": "Weather service temporarily unavailable"
            }

    if not results:

        # Try direct wttr fallback
        try:
            return wttr_weather(location)

        except Exception:
            return {
                "error": (
                    f"Location '{location}' not found. "
                    "Try a city name such as Pune or Kochi."
                )
            }

    place = results[0]

    latitude = place["latitude"]
    longitude = place["longitude"]

    # -----------------------------------------------------
    # 2. CURRENT WEATHER
    # -----------------------------------------------------

    weather_params = urllib.parse.urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "rain"
        ),
        "timezone": "auto"
    })

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?{weather_params}"
    )

    try:

        weather_data = open_meteo_request(
            weather_url,
            retries=2
        )

        current = weather_data["current"]

        return {
            "location": place.get(
                "name",
                location
            ),
            "state": place.get(
                "admin1",
                ""
            ),
            "country": place.get(
                "country",
                "India"
            ),
            "temperature": current[
                "temperature_2m"
            ],
            "humidity": current[
                "relative_humidity_2m"
            ],
            "rainfall": current[
                "rain"
            ],
            "source": "Open-Meteo"
        }

    except Exception as e:

        print(
            "Open-Meteo weather failed:",
            repr(e)
        )

        # -------------------------------------------------
        # 3. WEATHER FALLBACK
        # -------------------------------------------------

        try:

            return wttr_weather(
                location
            )

        except Exception as wttr_error:

            print(
                "WTTR weather fallback failed:",
                repr(wttr_error)
            )

            return {
                "error": (
                    "Weather service temporarily unavailable. "
                    "Please try again shortly."
                )
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

Current weather:
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
            input=prompt,
            generation_config={
                "thinking_level": "minimal"
            }
        )

        advisory = response.output_text.strip()

    except Exception as e:

        print(
            "Gemini Advisory Error:",
            repr(e)
        )

        advisory = json.dumps({
            "status": "Farm conditions analyzed",
            "advice_1": (
                f"Monitor {data.crop} closely "
                "according to current weather."
            ),
            "advice_2": (
                "Maintain appropriate soil moisture "
                "and avoid unnecessary irrigation."
            ),
            "warning": (
                "Weather conditions can change quickly; "
                "check local forecasts regularly."
            )
        })

    return {
        "advisory": advisory,
        "model_used": GEMINI_MODEL
    }