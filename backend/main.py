from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from trip_planner_backend import get_options, get_flights, get_return_flights, get_hotels, get_complete_dictionary,get_daily_plan, get_dalle_image
from dotenv import load_dotenv
import requests
import json

load_dotenv()
api_key = os.getenv('TRIP_PLANNER_API_KEY')
serpapi_key = os.getenv('serpAPI_PI_KEY_ROI')
class_api_key = os.getenv('CLASS_OPENAI_API_KEY')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class TripRequest(BaseModel):
    start_date: str
    end_date: str
    budget: int
    trip_type: str


@app.get("/search_options")
async def search(start_date: str, end_date: str, budget: int, trip_type: str):
    if start_date and end_date and budget and trip_type:
        try:
            destinations = get_options(api_key, start_date, end_date, budget, trip_type)
            flight_results = get_flights(destinations, start_date, end_date, budget)
            return_flights = get_return_flights(destinations, end_date)
            hotels = get_hotels(flight_results, start_date, end_date)
            complete_dict = get_complete_dictionary(flight_results, hotels, return_flights)
            results = complete_dict
            return {"data": results}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"detail": "start date, return date, budget and vacation type are required"}
    
@app.get("/chosen_destination_daily_plan")
async def chosen_destination(destination: str, start_date: str, end_date: str):
    if destination and start_date and end_date:
        try:
            daily_plan = get_daily_plan(destination, start_date, end_date)
            return {"data": daily_plan}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"detail": "destination, start date, return date and budget are required"}
    
@app.get("/dalle_image")
async def dalle_image(destination:str, daily_plan: str):
    if daily_plan:
        try:
            images = get_dalle_image(destination, daily_plan)
            return {"data": images}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"detail": "daily_plan is required"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
