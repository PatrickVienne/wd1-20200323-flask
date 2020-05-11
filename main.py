from flask import Flask, render_template, request, redirect, url_for, make_response
import random
import datetime

app = Flask(__name__)


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
        secret_number = request.cookies.get("lucky_number/secret")
        if not secret_number:
            secret_number = random.randint(1, 10)

        context = {
            "date_of_number": datetime.datetime.now().isoformat(),
        }

        response = make_response(render_template("lucky_number.html", **context))
        response.set_cookie("lucky_number/secret", str(secret_number))

        return response

    elif request.method == "POST":
        user_guess = request.form.get('number')
        user_secret_cookie = request.cookies.get("lucky_number/secret")
        if user_guess == user_secret_cookie:
            response = make_response(redirect(url_for('lucky_number_success')))
            response.set_cookie("lucky_number/secret", expires=0)
            return response
        else:
            return redirect(url_for('lucky_number'))


@app.route("/lucky_number/success", methods=["GET"])
def lucky_number_success():
    return render_template("lucky_number_success.html")


# TODO TODAY:
# - Post Form finish, get input parameters from request
# - Cookies
# - Database


# TODO: 1) add boogle site
# TODO: 2) add hair dresser site


if __name__ == '__main__':
    app.run(debug=True)
