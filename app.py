
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
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
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


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # taking the username from the db
    username = mongo.db.users.find_one({"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # Remove user from session cookies
    flash("You are logged out")
    session.clear()
    return redirect(url_for("login"))

# Route for home page
@app.route("/")
def home():
    return render_template("home.html")

# still working on this page
@app.route("/park", methods=["GET", "POST"])
def park():
    if request.method == "POST":
        parking = {
            "lot": request.form.get("lot"),
            "vehicle": request.form.get("vehicle"),
            "model": request.form.get("model"),
            "year": request.form.get("year"),
            "Plate-Number": request.form.get("Plate-Number"),
            "color": request.form.get("color"),
             "created_by": session["user"]
        }
        mongo.db.vehicleinfo.insert_one(parking)
        flash("Thank you for using Our Services")
        return redirect(url_for("profile" ))

    vehicleinfo = mongo.db.vehicleinfo.find()
    return render_template("park.html", vehicleinfo=vehicleinfo)
    #return render_template("park.html")


@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    tasks = mongo.db.vehicleinfo.find()
    return render_template("tasks.html", vehicleinfo=tasks)


@app.route("/edit_task/<task_id>", methods=["GET","PORT"])
def edit_task(task_id):
    tasks = mongo.db.vehicleinfo.find_one({"_id": ObjectId(task_id)})
    tasks = mongo.db.vehicleinfo.find()
    return render_template("edit_task.html", tasks=task, vehicleinfo=tasks)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)