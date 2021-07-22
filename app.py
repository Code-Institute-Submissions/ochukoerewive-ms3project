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



@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        #check if the user already exists in db
        existing_user = mongo.db.products.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            flash("user already exists")
            return redirect(url_for("home"))
        
        register = {
            "username": request.form.get("username").lower(),
            "password": request.form.get("password")
            #"password": generate_password_hash(request.form.get("password"))
             #"password": request.form.get("password")
        }
        mongo.db.products.users.insert_one(register)

        #putting new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("You have registered successfully")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


# The login and registration section 

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            # ensure user password match
            if existing_user["password"]. request.form.get("password"):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                #invalid password match
                flash("Incorrect Username or Password")
                return redirect(url_for("login"))

        else:
            #username doesn't exist
            flash("incorrect username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    #grabbing the session username from the db
    username = mongo.db.users.find_one({"username":session["user"]})["username"]
    return render_template("profile.html", username=username)


@app.route("/email", methods=["POST", "GET"])
def email():
    return render_template("login.html")



@app.route("/")
def home():
    return render_template("home.html") 


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)