import os
from flask import Flask, flash, render_template, url_for, redirect, request, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # CHECK IF USERNAME ALREADY EXISTS IN DB
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "full_name": request.form.get("full_name").capitalize(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        flash("Registration Successful! Please Login now.")
        return redirect(url_for("register"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #check if the username exists in db
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # Invalid password match
                flash("Incorrect Username and Password")
                return redirect(url_for("login"))
        else:
            # Username doesn't exist
            flash("Incorrect Username or Password")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    # Remove user from session cookies
    flash("You are logged out")
    session.clear()
    return redirect(url_for("login"))


#User profile page
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # taking the users from the db
    user = mongo.db.users.find_one(session["user"])
    parker = list(mongo.db.vehicleinfo.find())
    
    if "user" in session:
        return render_template("profile.html", user=user, parkers=parker)


#notices = list(mongo.db.users.find())
# Route for home page
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/park", methods=["GET", "POST"])
def park():
    if request.method == "POST":
        park = {
            "lot": request.form.get("lot"),
            "vehicle": request.form.get("vehicle"),
            "model": request.form.get("model"),
            "year": request.form.get("year"),
            "plate_number": request.form.get("plate_number"),
            "color": request.form.get("color"),
            "parked_by": session["user"]
        }
        mongo.db.vehicleinfo.insert_one(park)
        flash("Thank you for using Our Services")
    
    return render_template("park.html")


# Edit department page route
@app.route("/edit_park/<park_id>", methods=["GET", "POST"])
def edit_park(park_id):
    if request.method == "POST":
        parking = {
            "lot": request.form.get("lot"),
            "vehicle": request.form.get("vehicle"),
            "model": request.form.get("model"),
            "year": request.form.get("year"),
            "plate_number": request.form.get("plate_number"),
            "color": request.form.get("color"),
            "parked_by": session["user"]
        }
        mongo.db.vehicleinfo.update({"_id": ObjectId(park_id)}, parking)
        flash("Parking updated successfully")
        return redirect(url_for("profile", username=session["user"]))
 
    park = mongo.db.vehicleinfo.find_one({"_id": ObjectId(park_id)})
    return render_template("edit_park.html", park=park)


@app.route("/delete_parking/<park_id>")
def delete_parking(park_id):
    mongo.db.vehicleinfo.remove({"_id": ObjectId(park_id)})
    flash("Parking Deleted Successfully")
    return redirect(url_for("profile", username=session["user"]))
 

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
