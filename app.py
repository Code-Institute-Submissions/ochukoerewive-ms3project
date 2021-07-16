import os
from flask import Flask, flash, render_template, url_for, redirect, request, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/base")
def base():
    return render_template("base.html")

@app.route("/")
def index():
    if "username" in session:
        return "You are loggedd in as" + session["username"]

    return render_template("index.html")

@app.route("/login")
def login():
    return ""

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        users = mongo.db.users
        existing_user = users.find_one({"name" : request.form["username"]})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form["pass"].encode("utf-8"), bcrypt.gensalt())
            users.insert({"name" : request.form["username"], "password" : hashpass })
            session["username"] = request.form["username"]
            return redirect(url_for("index"))

        return "That username already exists"
    
    return render_template("register.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)