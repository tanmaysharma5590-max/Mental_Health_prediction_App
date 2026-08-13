import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from fastapi.middleware.cors import CORSMiddleware

# IMPORTANT: filename must exactly match the .pkl file in your project folder
model = joblib.load('mental_health_model.pkl')

top_countries = ['Other', 'India', 'USA', 'Canada', 'Australia', 'UK', 'Germany', 'Mexico', 'Turkey', 'France']

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Input schema
class StudentData(BaseModel):
    age: int = Field(..., ge=10, le=100)
    gender: Literal['Male', 'Female']
    country: str
    academic_level: Literal['Undergraduate', 'Graduate', 'High School']
    most_used_platform: Literal[
        'Facebook', 'LinkedIn', 'Instagram', 'Snapchat', 'Twitter', 'YouTube',
        'TikTok', 'LINE', 'KakaoTalk', 'VKontakte', 'WhatsApp', 'WeChat'
    ]
    purpose_of_use: Literal['Networking', 'Education', 'Entertainment', 'News']
    avg_daily_usage_hours: float = Field(..., ge=0, le=24)
    daily_unlocks: int = Field(..., ge=0)
    study_hours: float = Field(..., ge=0, le=24)
    physical_activity_hours: float = Field(..., ge=0, le=24)
    sleep_hours_per_night: float = Field(..., ge=0, le=24)
    stress_level: Literal['Medium', 'Low', 'Very High', 'High']


# Output schema
class PredictionResponse(BaseModel):
    predicted_mental_health_score: float


@app.get('/')
def greet():
    return {'message': 'Welcome to Mental Health Score Predictor API'}


@app.post('/predict', response_model=PredictionResponse)
def predict(data: StudentData):
    try:
        country_group = data.country if data.country in top_countries else 'Other'

        # These column names EXACTLY match what the model was trained on
        input_row = pd.DataFrame([{
            'Study_Hours': data.study_hours,
            'Age': data.age,
            'Avg_Daily_Usage_Hours': data.avg_daily_usage_hours,
            'Daily_Unlocks': data.daily_unlocks,
            'Physical_Activity_Hours': data.physical_activity_hours,
            'Sleep_Hours_Per_Night': data.sleep_hours_per_night,
            'Stress_Level': data.stress_level,
            'Gender': data.gender,
            'Academic_Level': data.academic_level,
            'Most_Used_Platform': data.most_used_platform,
            'Purpose_Of_Use': data.purpose_of_use,
            'Grouped_country': country_group,
        }])

        prediction = model.predict(input_row)[0]
        return PredictionResponse(predicted_mental_health_score=round(float(prediction), 2))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))