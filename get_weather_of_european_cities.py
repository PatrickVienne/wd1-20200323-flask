import json_api as API
import app_csv_util as CSVUTIL

if __name__ == '__main__':
    APPID = "439d4b804bc8187953eb36d2a8c26a02"

    cities = ["Berlin", "Barcelona", "Vienna", "Rome", "St. Pölten", "Athens", "Lisbon"]

    city_data = {}
    for city in cities:
        data = API.get_city_weather(city=city, appId=APPID)
        city_data[city] = data

    # -> for each city, we want: temperature, humidity, description
    # -> transform to list of lists, with the wanted entries
    contents = []
    for city, data in city_data.items():
        city_line = [city, data["main"]["temp"], data["main"]["humidity"], data["weather"][0]["description"]]
        contents.append(city_line)

    CSVUTIL.write_to_csv("city_weather.csv", contents)

print("DONE")
