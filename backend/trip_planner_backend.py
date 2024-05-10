import requests
from dotenv import load_dotenv
import json
import os
from openai import OpenAI

load_dotenv()
api_key = os.getenv('TRIP_PLANNER_API_KEY')

# openAI functions

def get_options(api_key, start_date, end_date, budget, trip_type):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    body = json.dumps({
        'messages': [
            {'role': 'system',
             'content': 'You are an experienced trip-planner agent. You need to give a customer five destination options for a trip around the world, based on the information the customer provided for you. return a sting of five locations, seperated by _. DONT INCLUDE ANY DIGITS IN YOUR RESPONSE'
             },
            {'role': 'user',
             'content': f'I want to go on a {trip_type} trip. My overall budget is {budget}. I want to leave on {start_date} and come back on {end_date}. Can you give me five destination options?'
            }
        ],
        'model': 'gpt-3.5-turbo',
        'temperature': 0.5
    })

    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        destinations_str = response.json()['choices'][0]['message']['content']
        destinations = destinations_str.split('_')
        return destinations
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            print("Looks like your API key is incorrect. Please check your API key and try again.")
        else:
            print(f"Failed to fetch recommendations. Status code: {response.status_code}")
    except Exception as err:
        print(f"An error occurred returning recommendations: {err}")

def get_daily_plan(chosen_location, start_date, end_date):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    body = json.dumps({
        'messages': [
            {'role': 'system',
             'content': 'You are an experienced trip-planner agent. You need to give a customer a daily plan for their trip to a specific location, based on the information the customer provided for you. Return a string of the daily plan. Just specify what he should do on every day, dont add any greetings etc.'
             },
            {'role': 'user',
             'content': f'I am going to {chosen_location} from {start_date} to {end_date}. Can you give me a daily plan for my trip?'
            }
        ],
        'model': 'gpt-3.5-turbo',
        'temperature': 0.5
    })
    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        daily_plan = response.json()['choices'][0]['message']['content']
        return daily_plan
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            print("Looks like your API key is incorrect. Please check your API key and try again.")
        else:
            print(f"Failed to fetch daily plan. Status code: {response.status_code}")
    except Exception as err:
        print(f"An error occurred planning a daily plan: {err}")

# def get_dalle_image(chosen_location, daily_plan):
#     url = 'https://api.openai.com/v1/images/generations'
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {api_key}'
#     }
#     body = json.dumps({
#         'prompt': f'An artistic image of {chosen_location} with the following daily plan: {daily_plan}',
#         'model': 'dall-e-3'
#         'num_images': '4'
#         'size': '512X512'
#     })
#     try:
#         response = requests.post(url, headers=headers, data=body)
#         response.raise_for_status()  # Raises an HTTPError for bad responses
#         image_urls = response.json()['images']
#         return image_urls
#     except requests.exceptions.HTTPError as http_err:
#         if response.status_code == 401:
#             print("Looks like your API key is incorrect. Please check your API key and try again.")
#         else:
#             print(f"Failed to fetch images. Status code: {response.status_code}")
#     except Exception as err:
#         print(f"An error occurred fetching images: {err}")

# Main function to test the APIs
if __name__ == "__main__":
    api_key = os.getenv('TRIP_PLANNER_API_KEY')
    start_date = '2024-07-01'
    end_date = '2024-07-15'
    budget = 3000
    trip_type = 'beach'
    
    print(api_key)
    destinations = get_options(api_key, start_date, end_date, budget, trip_type)
    print("Found destinations:", destinations)
    chosen_location = destinations[0]
    daily_plan = get_daily_plan(chosen_location, start_date, end_date)
    print("Daily plan:", daily_plan)

    