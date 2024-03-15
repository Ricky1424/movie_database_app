import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from helpers import lookup, lookup_imdbid
from flask import redirect, url_for

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///movies.db")


# Taken from finance pset - Not actually sure if it is needed
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Display the landing page to the user
@app.route("/", methods=["GET", "POST"])
def landing():
    """Landing page for user"""

    return render_template("layout.html")

# Display the register page to the user
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""
    # Check for request method POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check to see if passwords match
        password_match_fail = "Passwords do not match"
        if password != confirmation:
            return render_template("register.html", error_message=password_match_fail)

        # Check to see if user already exists
        username_taken = "That username is taken"
        usernames = db.execute("SELECT username FROM users")
        for row in usernames:
            if row["username"] == username:
                return render_template("register.html", error_message=username_taken)

        # Insert new user into database
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, password)

        # Return user to login screen
        return redirect("/login")

    # Else if method was GET
    else:
        return render_template("register.html")

# Display the login page to the user
@app.route("/login", methods=["GET", "POST"])
def login():
    """Login a user"""
    # Forget any user_id
    session.clear()

    # Check for request method POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for the given username
        invalid_login = "Invalid username or password"
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or password != rows[0]["password"]:
            return render_template("login.html", error_message=invalid_login)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # If all checks are succesful
        return redirect("/home")

    # If method was GET
    else:
        return render_template("login.html")

# Display the login page to the user
@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Loogout a user"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

# Display the home page to the user
@app.route("/home", methods=["GET", "POST"])
def home():
    """User homepage"""
    # If method is POST
    if request.method == "POST":
        search = request.form.get("search")
        movie_data = lookup(search)
        print(movie_data["Search"])
        return render_template("results.html", movie_data=movie_data)
    else:
        return render_template("home.html")

# Display the movie title page to the user
@app.route("/title", methods=["GET", "POST"])
def title():
    """Movie title"""
    # If method is POST
    if request.method == "POST":
        title_id = request.form.get("title_id")
        movie_data = lookup_imdbid(title_id)

        print("#######################")
        print(title_id)

        if movie_data["Poster"]:
            poster = movie_data["Poster"]
        else:
            # Handle the case when 'Search' key is not present in movie_poster_data
            print("No search results found.")

        return render_template("title.html", movie_data=movie_data, poster=poster)
    else:
        return render_template("home.html")


# Add movie to watchlist
@app.route("/watchlist", methods=["GET", "POST"])
def watchlist():
    """Watchlist"""
    # If method is POST
    if request.method == "POST":
        # Gets the user id of the current session user
        current_user = session["user_id"]

        # Get the title id which is passed from the button
        title_id = request.form.get("title_id")
        movie_data = lookup_imdbid(title_id)

        # Insert the user id and title id into the watchlist table
        db.execute("INSERT INTO watchlist (user_id, movie_id) VALUES (?, ?)", current_user, title_id)

        # Retrive the watchlist table data to display to the user
        rows = db.execute("SELECT * FROM watchlist WHERE user_id = (?)", current_user)

        movie_ids = []
        for movie in rows:
            movie_ids.append(movie["movie_id"])

        return render_template("home.html")
    else:
         # Gets the user id of the current session user
        current_user = session["user_id"]

        # Retrive the watchlist table data to display to the user
        rows = db.execute("SELECT * FROM watchlist WHERE user_id = (?)", current_user)

        movie_ids = []
        for movie in rows:
            movie_ids.append(movie["movie_id"])

        # Retrieve movie data using the API
        movie_data = []
        for row in movie_ids:
            movie_data.append(lookup_imdbid(row))

        return render_template("watchlist.html", movie_data=movie_data)

# Add movies to mymovies
@app.route("/mymovies", methods=["GET", "POST"])
def mymovies():
    """Mymovies"""
    # If method is POST
    if request.method == "POST":
        # Gets the user id of the current session user
        current_user = session["user_id"]

        # Store all the information from the review modal
        title_id = request.form.get("title_id")
        my_rating = request.form.get("my_rating")
        my_review = request.form.get("my_review")

        # Get the movie data for the reviewed movie
        movie_data = lookup_imdbid(title_id)
        movie_name = movie_data["Title"]

        db.execute("INSERT INTO mymovies (user_id, movie_id, movie_name, my_rating, my_review) VALUES (?, ?, ?, ?, ?)", current_user, title_id, movie_name, my_rating, my_review)

        return render_template("home.html")
    else:
        # Gets the user id of the current session user
        current_user = session["user_id"]

        rows = db.execute("SELECT * FROM mymovies WHERE user_id = (?)", current_user)
        return render_template("mymovies.html", mymovies=rows)
