import requests
from dotenv import load_dotenv
import json
import os
from openai import OpenAI
from datetime import datetime
from serpapi import GoogleSearch

load_dotenv()
api_key = os.getenv('TRIP_PLANNER_API_KEY')
serpapi_key = os.getenv('serpAPI_API_KEY_2')

#utility functions



def get_complete_dictionary(flights, hotels, return_flights):
    # Initialize the complete dictionary
    complete_dict = {}

    # Create a new hotels dictionary with stripped keys
    hotels_stripped = {key.strip(): value for key, value in hotels.items()}

    # Loop through the flight dictionary
    for destination, flight_details in flights.items():
        # Strip extra spaces from destination name if any
        destination_stripped = destination.strip()

        # Check if the same destination exists in the hotels dictionary
        if destination_stripped in hotels_stripped:
            # Copy flight details and remove 'remaining_budget'
            flight_info = flight_details.copy()
            flight_info.pop('remaining_budget', None)  # Remove 'remaining_budget' from this specific flight details
            return_info = return_flights.get(destination_stripped, {})
            return_flight_numbers = return_info.get('return_flight_numbers', [])
            total_return_duration = return_info.get('total_return_duration', 0)

            flight_info_extended = {
                'depart_airport_code': flight_info['depart_airport_code'],
                'destination_airport_code': flight_info['destination_airport_code'],
                'is_direct_flight': flight_info['is_direct_flight'],
                'flight_numbers': flight_info['flight_numbers'],
                'total_duration': flight_info['total_duration'],
                'return_flight_numbers': return_flight_numbers,
                'total_return_duration': total_return_duration,
                'total_flight_price': flight_info['total_flight_price']
            }
            

            # Merge flight details and hotel details
            complete_dict[destination_stripped] = {
                **flight_info,
                **hotels_stripped[destination_stripped]
            }

    return complete_dict

#serAPI functions
def get_flights(destinations, start_date, end_date, budget):
    flight_results = {}
    for destination in destinations:
        params = {
            "engine": "google_flights",
            "departure_id": "TLV",  # Assuming 'TLV' is the ID for Tel Aviv Airport
            "arrival_id": get_airport_code(destination),  # get_airport_code() is a function that returns the airport code for a given location
            "outbound_date": start_date,
            "return_date": end_date,
            "currency": "USD",
            "hl": "en",
            "api_key": serpapi_key
            
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        best_flights = results.get('best_flights', [])

        if best_flights:
            cheapest_flight = min(best_flights, key=lambda x: x['price'])
            flight_cost = cheapest_flight['price']
            is_direct_flight = 'no' if cheapest_flight['layovers'] else 'yes'
            total_minutes = cheapest_flight['total_duration']
            hours, minutes = divmod(total_minutes, 60)
            Departures_flight_numbers = [flight['flight_number'] for flight in cheapest_flight['flights']]
            total_duration = '{:02}:{:02}'.format(hours, minutes)
            departure_airport = cheapest_flight['flights'][0]['departure_airport']['id']
            destination_airport = cheapest_flight['flights'][-1]['arrival_airport']['id']

            flight_results[destination] = {
                "depart_airport_code": departure_airport,
                "destination_airport_code": destination_airport,
                "is_direct_flight": is_direct_flight,
                "total_duration": total_duration,
                "flight_numbers": Departures_flight_numbers,
                "total_flight_price": flight_cost,
                "remaining_budget": budget - flight_cost
            }
        else:
            print(f"No flights found for {destination}.")
            flight_results[destination] = {
                "depart_airport_code": None,
                "destination_airport_code": None,
                "is_direct_flight": "no",
                "total_duration": None,
                "flight_numbers": [],
                "total_flight_price": None,
                "remaining_budget": budget
            }

    return flight_results

# def get_return_flights(destinations, end_date):
    return_flight_results = {}
    for destination in destinations:
        params = {
            "engine": "google_flights",
            "departure_id": get_airport_code(destination),  
            "arrival_id": "TLV",  
            "outbound_date": end_date,
            "currency": "USD",
            "hl": "en",
            "api_key": serpapi_key
        }
        try:
            response = requests.get('https://api.serpapi.com/search', params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            results = response.json()
            best_flights = results.get('best_flights', [])

            if best_flights:
                cheapest_flight = min(best_flights, key=lambda x: x['price'])
                return_flight_numbers = [flight['flight_number'] for flight in cheapest_flight['flights']]
                total_minutes = cheapest_flight['total_duration']
                hours, minutes = divmod(total_minutes, 60)
                total_return_duration = '{:02}:{:02}'.format(hours, minutes)
                return_flight_results[destination] = {
                    "return_flight_numbers": return_flight_numbers,
                    "total_return_duration": total_return_duration
                }
            else:
                print(f"No flights found for {destination}.")
                return_flight_results[destination] = {
                    "return_flight_numbers": [],
                    "total_return_duration": None
                }
        except requests.RequestException as e:
            print(f"Request error for {destination}: {str(e)}")
        except json.JSONDecodeError:
            print(f"JSON decode error for {destination}")
        except KeyError as e:
            print(f"Key error: {destination} - {str(e)}")

    return return_flight_results


def get_hotels(flights, start_date, end_date):

    hotel_results = {}
    for destination, flight_details in flights.items():
        remaining_budget = flight_details['remaining_budget']
        duration = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days # may not need this
        params = {
            "engine": "google_hotels",
            "q": f"{destination.strip()} resorts",  # Search for resorts
            "vacation_rentals": "true",
            "check_in_date": start_date,
            "check_out_date": end_date,
            "adults": "2",
            "currency": "USD",
            "gl": "il",  # Adjusted for Israel, adjust as needed
            "hl": "en",
            "api_key": serpapi_key,
            "max_price": str(remaining_budget)
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        properties = results.get('properties', [])  # Get the list of properties
        affordable_hotels = [hotel for hotel in properties if hotel.get('total_rate', {}).get('extracted_lowest', 0) <= remaining_budget]

        if properties:
            # Finding the most expensive hotel within the budget
            if affordable_hotels:
                most_expensive_hotel = max(affordable_hotels, key=lambda x: x.get('total_rate', {}).get('extracted_lowest', 0))
            else:
                most_expensive_hotel = None
            hotel_cost = most_expensive_hotel.get('total_rate', {}).get('extracted_lowest', 0)
            hotel_name = most_expensive_hotel.get('name', 'Unknown')
            hotel_address = most_expensive_hotel.get('address', 'No address provided')
            hotel_rating = most_expensive_hotel.get('overall_rating', 'No rating')

            hotel_results[destination] = {
                "hotel_name": hotel_name,
                "hotel_address": hotel_address,
                "hotel_rating": hotel_rating,
                "total_hotel_price": hotel_cost,
                "remaining_budget": remaining_budget - hotel_cost
            }
        else:
            print(f"No hotels found for {destination}.")
            hotel_results[destination] = {
                "hotel_name": None,
                "hotel_address": None,
                "hotel_rating": None,
                "total_hotel_price": None,
                "remaining_budget": remaining_budget
            }

    return hotel_results

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
             'content': f'I am going to {chosen_location} from {start_date} to {end_date}. Can you give me a daily plan for my trip? I want a detailed plan for each day. no need to go hour by hour, just in a sentence what we should do that day'
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

def get_dalle_image(chosen_location, daily_plan):
    for i in range(5):
    
        url = 'https://api.openai.com/v1/images/generations'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        data= {
            "model": "dall-e-3",
            "prompt": f"An image of {chosen_location} with the following daily plan: {daily_plan}",
            "n": 1,
            "size": "1024x1024"

        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            result = response.json()
            print("Generated image URL:", result['data'][0]['url'])
        else:
            print("Error:", response.status_code, response.text)


# Main function to test the APIs
if __name__ == "__main__":
    api_key = os.getenv('TRIP_PLANNER_API_KEY')
    start_date = '2024-07-01'
    end_date = '2024-07-08'
    budget = 20000 
    trip_type = 'beach'
    
    
    destinations = get_options(api_key, start_date, end_date, budget, trip_type)
    print("Found destinations:", destinations)
    flight_results = get_flights(destinations, start_date, end_date, budget)
    return_flights = get_return_flights(destinations, end_date)
    hotels = get_hotels(flight_results, start_date, end_date)
    complete_dict = get_complete_dictionary(flight_results, hotels, return_flights)
    print("Complete dictionary:", complete_dict)
    chosen_location = destinations[0] #just for now, later will get user input
    daily_plan = get_daily_plan(chosen_location, start_date, end_date)
    print("Daily plan:", daily_plan)
    image_urls = get_dalle_image(chosen_location, daily_plan)


    