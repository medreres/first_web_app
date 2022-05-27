from flask import *
from flask_mail import *
from random import *
from helpers import apology
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import datetime


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


# contacts
@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


# timetable
@app.route("/timetable")
def timetable():
    return render_template("timetable.html")


# grades page
@app.route("/grades", methods=["GET", "POST"])
def grades():
    con = sqlite3.connect('grades.db')
    cursorObj = con.cursor()
    if request.method == "GET":
        if session["level"] == 0:
            # math+, ukrainian, history, PE, informatics, english, history_ukraine
            cursorObj.execute(
                "SELECT * FROM grades WHERE student_id = ?", (session["user_id"],))
            grades = cursorObj.fetchall()
            math = []
            ukrainian = []
            history = []
            informatics = []
            english = []
            history_ukraine = []
            for grade in grades:
                if grade[5] == "MATH":
                    math.append(grade)
                elif grade[5] == "UKRAINIAN":
                    ukrainian.append(grade)
                elif grade[5] == "HISTORY":
                    history.append(grade)
                elif grade[5] == "INFORMATICS":
                    informatics.append(grade)
                elif grade[5] == "ENGLISH":
                    english.append(grade)
                elif grade[5] == "HISTORY_UKRAINE":
                    history_ukraine.append(grade)
            return render_template("grades.html", math=math, ukrainian=ukrainian,
                                   history=history, informatics=informatics, english=english,
                                   history_ukraine=history_ukraine)
        else:
            cursorObj.execute(
                "SELECT * FROM grades WHERE teacher_id = ?", (session["user_id"],))
            grades = cursorObj.fetchall()
            return render_template("grades.html", grades=grades)
    else:
        subject = request.form.get("subject")
        print(subject)
        if subject is None:
            return apology("Subject hasn't been chosen")
        grade = request.form.get("grade")
        student_id = request.form.get("student_id")
        date = datetime.datetime.now()
        entities = (session["user_id"], int(student_id), int(
            grade), date.strftime('%Y-%m-%d %H:%M:%S'), subject)
        print(entities)
        cursorObj.execute(
            "INSERT INTO grades (teacher_id, student_id, grade, date, subject) VALUES (?,?,?,?,?)", entities)
        con.commit()
        return redirect("/grades")


# profile page
@app.route("/profile")
def profile():
    status = "Error"
    if session["level"] == 0:
        status = "Student"
    elif session["level"] == 1:
        status = "Teacher"
    elif session["level"] == 2:
        status = "Admin"
    return render_template("profile.html", status=status)


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        login = request.form.get("username")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        # entering database
        con = sqlite3.connect('users.db')
        cursorObj = con.cursor()
        cursorObj.execute(
            "SELECT * FROM users WHERE username = ?", (login,))
        user = cursorObj.fetchone()
        if user is None:
            cursorObj.execute(
                "SELECT * FROM users WHERE email = ?", (login,))
            user = cursorObj.fetchone()
        if user is None:
            return apology("User isn't found!")
        if not check_password_hash(user[1], password):
            return apology("Wrong password")
        session["user_id"] = user[0]
        session["year"] = user[7]
        session["username"] = user[3]
        session["first_name"] = user[2]
        session["last_name"] = user[4]
        session["email"] = user[5]
        session["level"] = user[6]
        flash(f"Hello, {user[2]}!")
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash("Logged out!")
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
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)
        session["password"] = hashed_password
        print(f"Hashed password to db {hashed_password}")

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
            cursorObj.execute(
                "SELECT * FROM users WHERE username = ?", (session["username"],))
            user = cursorObj.fetchone()
            print(user)
            session.clear()
            session["user_id"] = user[0]
            session["year"] = user[7]
            session["username"] = user[3]
            session["first_name"] = user[2]
            session["last_name"] = user[4]
            session["email"] = user[5]
            session["level"] = user[6]
        else:
            session.clear()
            flash("Something went wrong!")
    return redirect("/")
