from flask import *
from pyrebase import pyrebase
import os

Config = {
  'apiKey': "AIzaSyCDelmIoa9SEt-qGOpnN3shq72aOha-MYk",
  'authDomain': "kuse-website1.firebaseapp.com",
  'databaseURL': "https://kuse-website1.firebaseio.com",
  'projectId': "kuse-website1",
  'storageBucket': "kuse-website1.appspot.com",
  'messagingSenderId': "763982214471",
  'appId': "1:763982214471:web:4887eb91ac8d1502260862",
  'measurementId': "G-CJ06QNVMSV"
}

app = Flask(__name__)
firebase = pyrebase.initialize_app(Config)
db = firebase.database()
storage = firebase.storage()
auth = firebase.auth()
person = {"is_logged_in": False, "fname": "","sname": "", "email": "", "uid": ""}

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    # If POST, user attempts to log in
    if request.method == 'POST':
        try:
            # Collect the user data and sign in with firebase
            user = auth.sign_in_with_email_and_password(request.form['email'], request.form['password'])
            data = db.child("users").get() # Get a list of all users

            # Change global user dictionary
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["fname"] = data.val()[person["uid"]]["fname"]
            person["sname"] = data.val()[person["uid"]]["sname"]

            #Redirect to home page on successful login
            return render_template('apply.html', name=person["fname"])
        except:
            # if unsuccessful, render the login page again with an error
            return render_template('index.html', us="Login unsuccessful")

    # If GET, then we direct to login or application page, depending on login status
    else:
        if person["is_logged_in"] == True:
            return render_template('apply.html', name=person["fname"])
        else:
            return render_template('index.html')

@app.route("/logout")
def logout():
    # Logout button redirects to home page
    global person
    person = {"is_logged_in": False, "fname": "","sname": "", "email": "", "uid": ""}
    return redirect(url_for('login'))

# -------- Signup ---------------------------------------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # If signup form is filled instead
    if request.method == "POST":
        fname = request.form["fname"]
        sname = request.form["sname"]
        email = request.form["email"]
        password = request.form["password"]
        try:
            # Create User and Login
            auth.create_user_with_email_and_password(email, password)
            user = auth.sign_in_with_email_and_password(email, password)

            # Change global user dictionary
            global person
            person["is_logged_in"] = True
            person["fname"] = fname
            person["sname"] = sname
            person["email"] = user["email"]
            person["uid"] = user["localId"]

            # Store new customer's data
            db.child("users").child(person["uid"]).set({"fname": fname, "sname": sname, "email":email})

            # GET page from '/'
            return redirect(url_for('login'))
        except:
            return render_template('index.html', us_signup="Signup unsuccessful \n User may already exist")

# -------- Apply ---------------------------------------------------------- #
@app.route('/apply', methods=['GET','POST'])
def apply():
    if request.method == "POST":
        db.child("users").child(person["uid"]).update(request.form) # Upload form data to database
        storage.child(f'resumes/{person["sname"]}_{person["uid"]}.pdf').put(request.files['resume']) # Upload resume to storage

        # Redirect to the thank you page
        return render_template('thankyou.html', name=person["fname"])

# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run()
