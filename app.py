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

@app.route("/")
def index():
    if "username" in session:
        return "You are loggedd in as" + session["username"]

    return render_template("base.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.products.users.find_one({"username": request.form.get("username")})

        if existing_user:
            flash("user already exist")
            return redirect(url_for('base.html'))
        
        else:
            form = {
                "username": request.form.get("username"),
                "password": request.form.get("password")
            }
            mongo.db.products.users.insert_one(form)
            flash("You have registered successfully")
            return redirect(url_for('register'))
    return render_template("register.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)