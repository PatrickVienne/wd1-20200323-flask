import codecs
import json
import tempfile
import uuid

from flask import Flask, render_template, request, redirect, url_for, make_response, send_file
import random
import datetime
import hashlib
import json_api as API
from models import Users, SecretNumberStore, db

APPID = "439d4b804bc8187953eb36d2a8c26a02"

app = Flask(__name__)
db.create_all()

COOKIE_ID_STRING = "lucky_number/secret_number_identifier"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/fakebook")
def fakebook():
    return render_template("fakebook.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/lucky_number", methods=['GET', 'POST'])
def lucky_number():
    if request.method == "GET":

        secret_number_identifier = request.cookies.get(COOKIE_ID_STRING)
        secret_number_store = db.query(SecretNumberStore).filter_by(cookie_identifier=secret_number_identifier).first()

        if not secret_number_store:
            secret_number = random.randint(1, 10)
            cookie_identifier = str(uuid.uuid4())
            secret_number_store = SecretNumberStore(
                cookie_identifier=cookie_identifier,
                secret_number=secret_number
            )
            db.add(secret_number_store)
            db.commit()

        context = {
            "date_of_number": datetime.datetime.now().isoformat(),
        }

        response = make_response(render_template("lucky_number.html", **context))
        response.set_cookie(COOKIE_ID_STRING, str(secret_number_store.cookie_identifier))
        return response

    elif request.method == "POST":
        user_guess = request.form.get('number')
        cookie_identifier = request.cookies.get(COOKIE_ID_STRING)

        secret_number_store = db.query(SecretNumberStore).filter_by(cookie_identifier=cookie_identifier).first()

        app.logger.info(f"Secret Number Guess: user guess: {user_guess}, cookie identifier: {cookie_identifier}")

        if secret_number_store and (int(user_guess) == secret_number_store.secret_number):
            response = make_response(redirect(url_for('lucky_number_success')))
            response.set_cookie(COOKIE_ID_STRING, expires=0)

            db.delete(secret_number_store)
            db.commit()
            app.logger.info(f"User guessed number correctly, removing number with identifier: {cookie_identifier}")
            return response
        else:
            app.logger.info(f"User guessed number incorrectly, redirecting to guessing page")
            app.logger.error(f"ERROR: bad guess! do not repeat!")
            return redirect(url_for('lucky_number'))


@app.route("/lucky_number/success", methods=["GET"])
def lucky_number_success():
    return render_template("lucky_number_success.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        users = db.query(Users).all()
        context = {
            "users": users
        }
        return render_template("register.html", **context)
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # hash password, to protect against DB breaches
        hashed_password = hash_password(password)
        # save hashed password in the database with the new user
        new_user = Users(name=username, password=hashed_password, secret_number=10)
        db.add(new_user)
        db.commit()  # abspeichern aller geaddeten elemente, in einer transaktion.

        return redirect(url_for('register'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hashed_password = hash_password(password)
        user = db.query(Users).filter_by(name=username, password=hashed_password).first()
        if user is not None:
            # create new login token for the user and save it in the DB
            user.login_token = str(uuid.uuid4())
            db.add(user)
            db.commit()

            # set token in the browser, to identify logged in user in the future.
            response = make_response(redirect(url_for('main')))
            response.set_cookie('login_token', user.login_token)

            return response
        else:
            return redirect(url_for('login'))


@app.route("/logout", methods=["GET"])
def logout():
    # identify user in the DB based on token, if token is available
    login_token = request.cookies.get("login_token")
    # if no cookie is available, then redirect to login page directly
    if login_token is None:
        return redirect(url_for("login"))
    # if cookie is available, find user with that login token, and :
    # - remove token in DB (= overwrite with "")
    user = db.query(Users).filter_by(login_token=login_token).first()
    if user is not None:
        user.login_token = ""
        db.add(user)
        db.commit()

        # - remove cookie from browser
        response = make_response(redirect(url_for('login')))
        response.set_cookie("login_token", expires=0)
        return response

    # redirect to login page
    return redirect(url_for("login"))


@app.route("/users/<user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):

    user = db.query(Users).get(int(user_id))
    if user is None:
        return redirect(url_for('register'))

    if request.method == "GET":
        return render_template("user_edit.html", user=user)
    elif request.method == "POST":
        # post parameter
        secret_number = request.form.get("secret_number")
        login_token = request.form.get("login_token")

        user.secret_number = secret_number
        user.login_token = login_token

        db.add(user)
        db.commit()

        return redirect(url_for('register'))

# path variable
@app.route("/users/<user_id>/delete", methods=["GET"])
def delete_user(user_id):
    user = db.query(Users).get(int(user_id))
    if user is None:
        return redirect(url_for("register"))
    if request.method == "GET":
        response = make_response(redirect(url_for('register')))
        db.delete(user)
        db.commit()
        return response

# url parameters, get parameters
@app.route("/weather", methods=["GET"])
def weather():

    user_cities = request.args.get("city")
    if user_cities:
        weather_list = [API.get_city_weather(city, APPID) for city in user_cities.split(",")
                        if API.get_city_weather(city, APPID) is not None]
    else:
        cities = ["Berlin", "Barcelona", "Vienna", "Rome", "St. Pölten", "Athens", "Lisbon"]

        weather_list = [API.get_city_weather(city, appId=APPID) for city in cities]

    download_string = request.url_root + "download/weather"
    if user_cities:
        download_string += "?city="+user_cities

    context = {
        "weather_list": weather_list,
        "downloadlink": download_string
    }

    return render_template("weather.html", **context)


@app.route("/download/weather", methods=["GET"])
def download_weather():

    user_cities = request.args.get("city")
    if user_cities:
        weather_list = [API.get_city_weather(city, APPID) for city in user_cities.split(",")
                        if API.get_city_weather(city, APPID) is not None]
    else:
        cities = ["Berlin", "Barcelona", "Vienna", "Rome", "St. Pölten", "Athens", "Lisbon"]

        weather_list = [API.get_city_weather(city, appId=APPID) for city in cities]

    handle, filepath = tempfile.mkstemp()
    with codecs.open(filepath, "w", encoding="utf-8") as output:
        json.dump(weather_list, output)

    return send_file(filepath, as_attachment=True, attachment_filename="cities.json")

@app.route("/mockup", methods=["GET"])
def mockup():
    _directory_0 = request.args.get("pos_0", "")
    _directory_90 = request.args.get("pos_90", "")
    _result = request.args.get("result", "")
    if _directory_0:
        files: dict = {}
    if _directory_90:
        data_90 = {}

    if _result:
        return _result
    else:
        _result = [] if random.random()<0.5 else [1]
        return  json.dumps(_result)


# TODO TODAY:
# - Post Form finish, get input parameters from request
# - Cookies
# - Database


# TODO: 1) add boogle site
# TODO: 2) add hair dresser site


if __name__ == '__main__':
    app.run(debug=True)
