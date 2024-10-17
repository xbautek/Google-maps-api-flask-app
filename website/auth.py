from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from . import localize
import urllib.request, json
import googlemaps
from pprint import pprint
from dotenv import load_dotenv
import os


def configure():
    load_dotenv()


auth = Blueprint("auth", __name__)

# Route to log in the user
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)


# Route to log out the user
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# Route to sign up a new user
@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 4 characters.", category="error")
        elif "@" not in email:
            flash("Email must contain @.", category="error")
        elif len(firstName) < 2:
            flash("First name must be greater than 1 character.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category="error")
        else:
            new_user = User(
                email=email,
                firstName=firstName,
                password=generate_password_hash(password1, method="sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            return redirect(url_for("views.home"))

    return render_template("sign_up.html", user=current_user)


# Route to get weather data from API for the user's current location
@auth.route("/weather", methods=["GET"])
@login_required
def weather():
    configure()

    api_google = os.getenv("GOOGLE_MAPS_API_KEY")
    map_client = googlemaps.Client(key=api_google)
    response = map_client.geolocate()
    latitude = response["location"]["lat"]
    longitude = response["location"]["lng"]

    api = os.getenv("OPENWEATHERMAP_API_KEY")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api}"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return render_template("weather.html", user=current_user, data=data)


# API endpoint to get weather data for a specific city using the city name as a parameter in the URL path
@auth.route("/api/weather/<city>", methods=["GET"])
@login_required
def api_weather(city):
    configure()
    localization = localize.Location(city)

    latitude = localization.get_latitude()
    longitude = localization.get_longitude()
    api = os.getenv("OPENWEATHERMAP_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api}"

    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
    except urllib.error.URLError as e:
        return (
            jsonify({"error": "Failed to retrieve weather data", "details": str(e)}),
            500,
        )
    except json.JSONDecodeError as e:
        return (
            jsonify({"error": "Failed to parse weather data", "details": str(e)}),
            500,
        )

    return jsonify(data)


# api endpoint to get the top 5 restaurants near the user's current location
@auth.route("/api/places", methods=["GET"])
@login_required
def places():
    configure()

    api_google = os.getenv("GOOGLE_MAPS_API_KEY")
    map_client = googlemaps.Client(key=api_google)
    response = map_client.geolocate()
    latitude = response["location"]["lat"]
    longitude = response["location"]["lng"]

    response_places = map_client.places_nearby(
        location=(latitude, longitude), radius=500, type="restaurant"
    )
    places = response_places.get("results", [])

    if not places:
        return jsonify({"error": "No places found nearby"}), 404

    sorted_places = sorted(places, key=lambda x: x.get("rating", 0), reverse=True)
    top_5_places = sorted_places[:5]

    return jsonify(top_5_places)


# api endpoint to get the user's current location
@auth.route("/api/geolocation", methods=["GET"])
@login_required
def api_geolocation():
    configure()

    api_google = os.getenv("GOOGLE_MAPS_API_KEY")
    map_client = googlemaps.Client(key=api_google)

    try:
        response = map_client.geolocate()
        pprint(response)

        if "location" not in response:
            return jsonify({"error": "Geolocation data not found"}), 500

        latitude = response["location"]["lat"]
        longitude = response["location"]["lng"]

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    try:
        configure()
        api_geoweather = os.getenv("OPENWEATHERMAP_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_geoweather}"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)
