import requests


WEATHER_API_KEY = "d19fef121990e40610dd36d828cc9eac"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()
    print(res)

get_weather("delhi")