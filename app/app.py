from flask import *
from flask_mail import *
from random import *
from helpers import *
import sqlite3


app = Flask(__name__)
app.secret_key = "super secret key"
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'kulchytskischool@gmail.com'
app.config['MAIL_PASSWORD'] = 'Abcd2ef@'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
mail = Mail(app)
otp = randint(000000, 999999)

app.config["TEMPLATES_AUTO_RELOAD"] = True


# homepage
@app.route("/", methods=["GET"])
def homepage():
    return render_template("homepage.html")


# grades page
@app.route("/grades")
def grades():
    return apology("TODO")

# profile page


@app.route("/profile")
def profile():
    return apology("TODO")


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        print("  ")
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # opening db
        con = sqlite3.connect('users.db')
        cursorObj = con.cursor()

        # getting username and stuff
        session["year"] = request.form.get("class")
        session["username"] = request.form.get("username")
        cursorObj.execute("SELECT username FROM users")
        usernames = cursorObj.fetchall()
        # print(usernames)
        for user in usernames:
            if user[0] == session["username"]:
                return apology("User with this username already exists!")
        # checking passwords for similarity
        if request.form.get("password") != request.form.get("password1"):
            return apology("Passowrds don't match")
        session["password"] = request.form.get("password")

        # getting name
        session["first_name"] = request.form.get("first_name")
        session["last_name"] = request.form.get("last_name")

        # checking if email already used
        session["email"] = request.form.get("email")
        emails = cursorObj.execute(
            "SELECT email FROM users")
        rows = cursorObj.fetchall()
        for row in rows:
            if(session["email"] == row[0]):
                return apology("User with this email already exists!")
        # sending validation code
        msg = Message('OTP', sender='kulchytskischool@gmail.com',
                      recipients=[session["email"]])
        msg.body = str(otp)
        mail.send(msg)
    return render_template("/validate.html", code=otp, username=request.form.get("username"))


# validating email
@app.route('/validate', methods=["GET", "POST"])
def validate():
    if request.method == "POST":
        user_otp = request.form['code']
        if otp == int(user_otp):
            flash("Your account is succesfully registered!")

            con = sqlite3.connect('users.db')
            cursorObj = con.cursor()
            entities = (session["password"], session["username"], session["first_name"],
                        session["last_name"], session["email"], 0, session["year"])
            cursorObj.execute(
                "INSERT INTO users(password, username, first_name, last_name, email, level, year) VALUES(?, ?, ?, ?, ?, ?, ?)", entities)
            con.commit()

            # getting user's id
            print(session["username"])
            cursorObj.execute(
                "SELECT user_id FROM users WHERE username = ?", (session["username"],))
            user_id = cursorObj.fetchall()
            print(user_id)
            session["user_id"] = user_id
        else:
            session.clear()
            flash("Something went wrong!")
    return redirect("/")
