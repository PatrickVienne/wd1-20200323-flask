import urllib.request
import json

def get_city_weather(city):
    baseurl = "http://api.openweathermap.org/data/2.5/weather"
    appid = "d2791b4777d6146afbf3ae6fd22bbf25"
    city = "London"
    values = {'q': city,
              # 'units': 'metric',
              # 'appid': appid
              }

    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')  # data should be bytes
    req = urllib.request.Request(baseurl, data)

    with urllib.request.urlopen(req) as response:
        content = response.read()
    weather_info = json.loads(content)
    return weather_info

get_city_weather("London")