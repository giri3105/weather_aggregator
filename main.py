import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests

# OpenWeatherMap API configuration
API_KEY = '2b005cdf180f7c2b16a805cb7e3d7294'  # Replace with your OpenWeatherMap API key
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

def kelvin_to_celsius(kelvin):
    """
    Convert temperature from Kelvin to Celsius.
    
    Parameters:
    kelvin (float): Temperature in Kelvin.
    
    Returns:
    float: Temperature in Celsius.
    """
    return kelvin - 273.15

def get_weather_data(city_name):
    """
    Fetch weather data for a given city from OpenWeatherMap API.
    
    Parameters:
    city_name (str): Name of the city to fetch weather data for.
    
    Returns:
    dict: A dictionary containing weather details if successful, None otherwise.
    """
    try:
        params = {
            'q': city_name,
            'appid': API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['cod'] != 200:
            return handle_error(data['cod'], city_name)
        
        weather = {
            'city': city_name,
            'temperature': {
                'current': kelvin_to_celsius(data['main']['temp']),
                'min': kelvin_to_celsius(data['main']['temp_min']),
                'max': kelvin_to_celsius(data['main']['temp_max']),
            },
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
        }
        return weather
    except requests.exceptions.HTTPError as http_err:
        handle_http_error(response.status_code, city_name, http_err)
    except requests.exceptions.ConnectionError as conn_err:
        messagebox.showerror("Connection Error", f"Connection error occurred while fetching data for city '{city_name}': {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        messagebox.showerror("Timeout Error", f"Timeout error occurred while fetching data for city '{city_name}': {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        messagebox.showerror("Error", f"An error occurred while fetching data for city '{city_name}': {req_err}")
    return None

def handle_error(code, city_name):
    """
    Handle specific API error codes by displaying appropriate error messages.
    
    Parameters:
    code (int): The error code returned by the API.
    city_name (str): Name of the city that caused the error.
    
    Returns:
    None
    """
    if code == 401:
        messagebox.showerror("Unauthorized", f"Unauthorized access for city '{city_name}'. Please check your API key.")
    elif code == 404:
        messagebox.showerror("Not Found", f"City '{city_name}' not found. Please check the city name.")
    elif code == 429:
        messagebox.showerror("Too Many Requests", f"Too many requests for city '{city_name}'. Please try again later.")
    elif code in (500, 502, 503, 504):
        messagebox.showerror("Server Error", f"Server error occurred while fetching data for city '{city_name}'. Please try again later.")
    else:
        messagebox.showerror("Error", f"An error occurred for city '{city_name}': {code}")
    return None

def handle_http_error(status_code, city_name, http_err):
    """
    Handle HTTP errors by displaying appropriate error messages.
    
    Parameters:
    status_code (int): The HTTP status code returned by the request.
    city_name (str): Name of the city that caused the error.
    http_err (Exception): The HTTP error exception.
    
    Returns:
    None
    """
    if status_code == 401:
        messagebox.showerror("Unauthorized", f"Unauthorized access for city '{city_name}'. Please check your API key.")
    elif status_code == 404:
        messagebox.showerror("Not Found", f"City '{city_name}' not found. Please check the city name.")
    elif status_code == 429:
        messagebox.showerror("Too Many Requests", f"Too many requests for city '{city_name}'. Please try again later.")
    elif status_code in (500, 502, 503, 504):
        messagebox.showerror("Server Error", f"Server error occurred while fetching data for city '{city_name}'. Please try again later.")
    else:
        messagebox.showerror("HTTP Error", f"HTTP error occurred for city '{city_name}': {http_err}")

def display_weather_data(weather_data):
    """
    Display weather data in the scrolled text widget.
    
    Parameters:
    weather_data (dict): A dictionary containing weather details.
    
    Returns:
    None
    """
    if not weather_data:
        return
    
    result = (
        f"Weather in {weather_data['city']}:\n"
        f"Temperature: {weather_data['temperature']['current']:.2f}°C\n"
        f"Min Temperature: {weather_data['temperature']['min']:.2f}°C\n"
        f"Max Temperature: {weather_data['temperature']['max']:.2f}°C\n"
        f"Humidity: {weather_data['humidity']}%\n"
        f"Weather Description: {weather_data['description'].capitalize()}\n"
        f"{'-'*40}\n"
    )
    result_text.insert(tk.END, result)
    result_text.yview(tk.END)

def fetch_weather():
    """
    Fetch and display weather data for cities entered by the user.
    
    Returns:
    None
    """
    cities = entry.get()
    if not cities:
        messagebox.showerror("Input Error", "No city names provided.")
        return
    
    city_list = [city.strip() for city in cities.split(',') if city.strip()]
    result_text.delete(1.0, tk.END)
    for city in city_list:
        weather_data = get_weather_data(city)
        display_weather_data(weather_data)

# Create the main window
root = tk.Tk()
root.title("Weather App")

# Create and place the widgets
label = tk.Label(root, text="Enter city names separated by commas:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=10)
entry.bind('<Return>', lambda event: fetch_weather())

button = tk.Button(root, text="Get Weather", command=fetch_weather)
button.pack(pady=10)

result_text = scrolledtext.ScrolledText(root, width=60, height=20, wrap=tk.WORD)
result_text.pack(pady=10)

# Start the main loop
root.mainloop()
