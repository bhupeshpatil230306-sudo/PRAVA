<div align="center">

# 🌾 PRAVA

### AI-Powered Agricultural Intelligence for Smarter, Climate-Resilient Farming

**Turning agricultural data into simple, actionable decisions.**

[🚀 Live Demo](https://prava-1-30hu.onrender.com)

[![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react&logoColor=black)](#)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](#)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?logo=google)](#)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](#)
[![Machine Learning](https://img.shields.io/badge/ML-Random%20Forest-2E8B57)](#)

</div>







# PRAVA 🌾
AI-Powered Agricultural Intelligence for Smarter, Climate-Resilient Farming

PRAVA is an AI-powered agricultural intelligence platform designed to help farmers make faster and more informed decisions using machine learning, multimodal AI, weather data, and farm-condition analysis.

Don't make farmers understand data. Make PRAVA understand data and give farmers a simple decision.

## Problem
Farmers often need to make critical decisions about:

- Which crop is suitable for current farm conditions?
- What could be affecting a crop or leaf?
- What action should be taken based on current weather?
- How can complex agricultural data be converted into simple, practical advice?

Agricultural information is often fragmented across different sources and can be difficult to interpret quickly.

PRAVA brings these intelligence capabilities into one simple farmer-focused platform.

## Our Solution
PRAVA combines:
Machine Learning + Generative AI + Weather Intelligence + Image Analysis
to provide three core agricultural intelligence modules.

### 1.Smart Crop Recommendation
Farm conditions are analyzed using:
- Nitrogen (N)
- Phosphorus (P)
- Potassium (K)
- Temperature
- Humidity
- Soil pH
- Rainfall

A Random Forest machine-learning model predicts a suitable crop.
Gemini then explains:
Why PRAVA recommends this crop and provides practical farming tips.

2. AI Crop Disease Diagnosis
Farmers can upload a crop or leaf image.
PRAVA uses Gemini's multimodal vision capabilities to analyze the image and return:
- Crop identification
- Possible condition/disease
- Symptoms
- Recommended action
- Additional practical action

The system is designed to provide understandable guidance rather than overwhelming users with technical terminology.

3. Smart Agro-Advisory
Farmers provide:
- Crop
- Location
- Temperature
- Humidity
- Rainfall

PRAVA combines these conditions with Gemini to generate:
- Overall farm status
- Practical action
- Additional recommendation
- Important warning

The platform also retrieves current weather information using Open-Meteo.

## AI & Machine Learning Architecture
                    ┌──────────────────────┐
                    │      PRAVA Web App   │
                    │   React Frontend     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌─────────────┐  ┌─────────────┐
       │ Random     │   │   Gemini    │  │ Open-Meteo  │
       │ Forest ML  │   │ Multimodal  │  │   Weather   │
       └─────┬──────┘   └──────┬──────┘  └──────┬──────┘
             │                 │                │
             └─────────────────┼────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Farmer-Friendly      │
                    │ Agricultural Advice  │
                    └──────────────────────┘

## Crop Intelligence
Farm Conditions
      ↓
Random Forest Model
      ↓
Crop Prediction
      ↓
Gemini Reasoning
      ↓
Explanation + Farming Tips

## Disease Intelligence
Crop / Leaf Image
      ↓
Gemini Multimodal Vision
      ↓
Condition Analysis
      ↓
Symptoms + Actions

## Agro-Advisory
Crop + Location + Weather
            ↓
      Gemini Analysis
            ↓
     Farm Condition
            ↓
 Actions + Warning

## Supported Crop Categories
The current ML dataset contains 22 crop categories:
- Rice
- Maize
- Chickpea
- Kidney Beans
- Pigeon Peas
- Moth Beans
- Mung Bean
- Black Gram
- Lentil
- Pomegranate
- Banana
- Mango
- Grapes
- Watermelon
- Muskmelon
- Apple
- Orange
- Papaya
- Coconut
- Cotton
- Jute
- Coffee
Based on the indian weather.

## Technology Stack

1. Frontend
- React
- React Router
- CSS
- Responsive web interface
2. Backend
- Python
- FastAPI
- Uvicorn
- Pydantic
3. AI
- Google Gemini
- Gemini multimodal image analysis
- Generative AI reasoning
4. Machine Learning
- Scikit-learn
- Random Forest
- Joblib
- Pandas
5. Data & APIs
- Crop Recommendation Dataset
- Open-Meteo Weather API
6. Deployment
- GitHub
- Render

## API Architecture
The backend exposes dedicated endpoints for the three intelligence modules:
POST /crop-recommendation
POST /disease-diagnosis
POST /agro-advisory
GET  /weather


## Impact Vision
PRAVA aims to turn complex agricultural information into simple, actionable decisions.
Instead of asking a farmer to interpret:
- soil parameters
- weather values
- crop datasets
- disease symptoms
- AI outputs

## Backend
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
pip install -r requirements.txt
 
## Frontend
cd frontend
npm install


## Frontend
PRAVA Web Application

https://prava-1-30hu.onrender.com

## Backend API
PRAVA FastAPI Backend

https://prava-ntpx.onrender.com

npm start


## Team 
Team PRAVA
Developed for Build with AI: Code for Communities — Second Edition 2026

## License
This project was developed for educational and hackathon purposes.
