import requests


def get_users():
    url = "https://jsonplaceholder.typicode.com/users"

    response = requests.get(url)
    users = response.json()
    for user in users:
        print(f"{user['id']}, {user['name']}, {user['address']['city']}")
    return users


def get_posts(user_id=None):
    url = "https://jsonplaceholder.typicode.com/posts"

    if user_id is not None:
        url += f"?userId={user_id}"
    response = requests.get(url)
    posts = response.json()

    for post in posts:
        print(f"{post['id']}, {post['userId']}, {post['title']}")
    return posts


def get_city_weather(city="London", appId=""):
    url = "https://openweathermap.org/data/2.5/weather"
    parameters = f"?q={city}&appid={appId}"
    url = url + parameters

    response = requests.get(url)
    data = response.json()
    if "name" not in data:
        return None
    return data


if __name__ == '__main__':
    get_city_weather(city="Mexiko City", appId="439d4b804bc8187953eb36d2a8c26a02")



