import requests
from dotenv import load_dotenv
import json
import os
from openai import OpenAI
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import base64
from datetime import datetime
import openai
from serpapi import GoogleSearch

load_dotenv()
api_key = os.getenv('TRIP_PLANNER_API_KEY')
serpapi_key = os.getenv('serpAPI_API_KEY')


#serAPI functions
def get_flights(destinations, start_date, end_date, budget, api_key):
    flight_results = {}
    for destination in destinations:
        params = {
            "engine": "google_flights",
            "departure_id": "TLV",  # Assuming 'TLV' is the ID for Tel Aviv Airport
            "arrival_id": get_airport_code(destination),  # This needs to be the airport code
            "outbound_date": start_date,
            "return_date": end_date,
            "currency": "USD",
            "hl": "en",
            "api_key": serpapi_key
            
        }
        print("Params:", params) # Debugging
        search = GoogleSearch(params)
        results = search.get_dict()
        best_flights = results.get('best_flights', [])

        if best_flights:
            # Sorting to find the cheapest round trip flight
            cheapest_flight = min(best_flights, key=lambda x: x['price'])
            flight_cost = cheapest_flight['price']
            flight_results[destination] = {
                "flight": cheapest_flight,
                "remaining_budget": budget - flight_cost
            }
        else:
            print(f"No flights found for {destination}.")
            flight_results[destination] = {
                "flight": None,
                "remaining_budget": budget
            }

    return flight_results

# openAI functions

def get_airport_code(location):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    body = json.dumps({
        'messages': [
            {'role': 'system',
             'content': 'You are an experienced trip-planner agent. Given a location in the world, just return its airport code. For example, if the location is "Paris", you should return "CDG". ONLY RETURN THE AIRPORT CODE, NOT ANYTHING ELSE.' 
             },
            {'role': 'user',
             'content': f'What is the airport code of {location}?'
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

#def get_dalle_image(chosen_location, daily_plan):
#     my_prompt = f'An artistic image of {chosen_location} depicting activities such as {daily_plan}'
#     client = OpenAI()
#     url = 'https://api.openai.com/v1/images/generations'
#     prompt = {
#         'subject': f'An artistic image of {chosen_location} depicting activities such as {daily_plan}',
#         'style': 'dalle'
#     }
#     image_params ={
#         'model': 'dall-e-2', #save money
#         'n': 4,
#         'size': '1024x1024',
#         'prompt': prompt,
#         'user': 'Shachar Bloch'
#     }

#     image_params.update({"response_format": "b64_json"})

#     try:
#         images_response = client.images.generate(**image_params)
#     except openai.APIConnectionError as e:
#         print("Server connection error: {e.__cause__}")  # from httpx.
#         raise
#     except openai.RateLimitError as e:
#         print(f"OpenAI RATE LIMIT error {e.status_code}: (e.response)")
#         raise
#     except openai.APIStatusError as e:
#         print(f"OpenAI STATUS error {e.status_code}: (e.response)")
#         raise
#     except openai.BadRequestError as e:
#         print(f"OpenAI BAD REQUEST error {e.status_code}: (e.response)")
#         raise
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         raise

#     # make a file name prefix from date-time of response
#     images_dt = datetime.utcfromtimestamp(images_response.created)
#     img_filename = images_dt.strftime('DALLE-%Y%m%d_%H%M%S')  # like 'DALLE-20231111_144356'


#     # get out all the images in API return, whether url or base64
#     # note the use of pydantic "model.data" style reference and its model_dump() method
#     image_url_list = []
#     image_data_list = []
#     for image in images_response.data:
#         image_url_list.append(image.model_dump()["url"])
#         image_data_list.append(image.model_dump()["b64_json"])

#     # Initialize an empty list to store the Image objects
#     image_objects = []

#     # Check whether lists contain urls that must be downloaded or b64_json images
#     if image_url_list and all(image_url_list):
#         # Download images from the urls
#         for i, url in enumerate(image_url_list):
#             while True:
#                 try:
#                     print(f"getting URL: {url}")
#                     response = requests.get(url)
#                     response.raise_for_status()  # Raises stored HTTPError, if one occurred.
#                 except requests.HTTPError as e:
#                     print(f"Failed to download image from {url}. Error: {e.response.status_code}")
#                     retry = input("Retry? (y/n): ")  # ask script user if image url is bad
#                     if retry.lower() in ["n", "no"]:  # could wait a bit if not ready
#                         raise
#                     else:
#                         continue
#                 break
#             image_objects.append(Image.open(BytesIO(response.content)))  # Append the Image object to the list
#             image_objects[i].save(f"{img_filename}_{i}.png")
#             print(f"{img_filename}_{i}.png was saved")
#     elif image_data_list and all(image_data_list):  # if there is b64 data
#         # Convert "b64_json" data to png file
#         for i, data in enumerate(image_data_list):
#             image_objects.append(Image.open(BytesIO(base64.b64decode(data))))  # Append the Image object to the list
#             image_objects[i].save(f"{img_filename}_{i}.png")
#             print(f"{img_filename}_{i}.png was saved")
#     else:
#         print("No image data was obtained. Maybe bad code?")

#     ## -- extra fun: pop up some thumbnails in your GUI if you want to see what was saved

#     if image_objects:
#         # Create a new window for each image
#         for i, img in enumerate(image_objects):
#             # Resize image if necessary
#             if img.width > 512 or img.height > 512:
#                 img.thumbnail((512, 512))  # Resize while keeping aspect ratio

#             # Create a new tkinter window
#             window = tk.Tk()
#             window.title(f"Image {i}")

#             # Convert PIL Image object to PhotoImage object
#             tk_image = ImageTk.PhotoImage(img)

#             # Create a label and add the image to it
#             label = tk.Label(window, image=tk_image)
#             label.pack()

#             # Run the tkinter main loop - this will block the script until images are closed
#             window.mainloop()


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
    flight_results = get_flights(destinations, start_date, end_date, budget, serpapi_key)
    print("Flights:", flight_results)
    chosen_location = destinations[0]
    daily_plan = get_daily_plan(chosen_location, start_date, end_date)
    print("Daily plan:", daily_plan)
    # image_urls = get_dalle_image(chosen_location, daily_plan)
    # print("Image URLs:", image_urls)

    