import sqlite3
import bcrypt
from flask import Flask, request, render_template, redirect, session, url_for, jsonify
import csv
import numpy as np
import io
import base64
import random
import string
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend

app = Flask(__name__)
app.secret_key = 'secret_key'


class User:
    def __init__(self, email, password, name, account_type):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.account_type = account_type

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


def create_user_table():
    try:
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                account_type TEXT,
                password TEXT NOT NULL,
                userPhoto BLOB
            )
        ''')
        connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating the User table: {e}")
    finally:
        connection.close()


def create_combined_table():
    try:
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CombinedTable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                BusinessSector TEXT,
                BusinessFunction TEXT,
                MeasuringElt TEXT,
                Rating INTEGER,
                SUbCategory TEXT,
                AsIsQuestions TEXT,
                ToBeQuestions TEXT,
                MaxRating INTEGER

            )
        ''')
        connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating the CombinedTable: {e}")
    finally:
        connection.close()


def create_trimmed_table():
    try:
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ArrangingTheDataInProperOrder (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                BusinessSector TEXT,
                BusinessFunction TEXT,
                MeasuringElt TEXT,
                Rating INTEGER,
                SUbCategory TEXT,
                AsIsQuestions TEXT,
                ToBeQuestions TEXT,
                MaxRating INTEGER,
                AnswerRating TEXT,
                AnswerRatingValue INTEGER
            )
        ''')
        connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating the ArrangingTheDataInProperOrder table: {e}")
    finally:
        connection.close()


# Create tables
create_user_table()
create_combined_table()
create_trimmed_table()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_type = request.form['users']
        user_photo = request.files['User_photo']

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            connection.close()
            return render_template('register.html', error='User with this email already exists')

        hashed_password = bcrypt.hashpw(password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Read the photo data and convert it to binary
        user_photo_data = user_photo.read()

        cursor.execute('INSERT INTO User (name, email, password, account_type, userPhoto) VALUES (?, ?, ?, ?, ?)',
                       (name, email, hashed_password, account_type, user_photo_data))
        connection.commit()
        connection.close()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        account_type = request.form['users']

        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')) and user[3] == account_type:
            session['email'] = user[2]
            if account_type == "Administrator":
                return redirect('/administrator')
            elif account_type == "Business Manager":
                return redirect('/BusinessManager')
            elif account_type == "Business Analyst":
                return redirect('/userAccount')
        else:
            error_message = "Invalid credentials. Please make sure to enter the correct email, password, and account type."
            return render_template('login.html', error=error_message)

    return render_template('login.html')


# Administrator
@app.route('/administrator')
def dashboardAdministrator():
    if session.get('email'):
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (session['email'],))
        user = cursor.fetchone()
        connection.close()
        return render_template('administrator.html', user=user)

    return redirect('/login')


# Displaying the elements in the database on the admin side of the panel
@app.route('/view_combined_data', methods=['GET', 'POST'])
def view_combined_data():
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, AsIsQuestions, ToBeQuestions, MaxRating
        FROM CombinedTable
    ''')
    combined_data = cursor.fetchall()

    # Normalize the BusinessFunction column
    normalize_business_function()

    cursor.execute('SELECT DISTINCT BusinessFunction FROM ArrangingTheDataInProperOrder')
    unique_business_functions = cursor.fetchall()
    print("These are the unique business functions: ", unique_business_functions)

    connection.close()

    return render_template('administrator.html', combined_data=combined_data, unique_business_functions=unique_business_functions)


# Uploading CSV file to database
def normalize_business_function():
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()

    # Clear existing data in ArrangingTheDataInProperOrder table to prevent duplication
    cursor.execute('DELETE FROM ArrangingTheDataInProperOrder')

    cursor.execute('''
        WITH RECURSIVE split(id, BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, AsIsQuestions, ToBeQuestions, MaxRating, value, rest) AS (
            SELECT
                id,
                BusinessSector,
                BusinessFunction,
                MeasuringElt,
                Rating,
                SUbCategory,
                AsIsQuestions,
                ToBeQuestions,
                MaxRating,
                TRIM(SUBSTR(BusinessFunction || ',', 1, INSTR(BusinessFunction || ',', ',') - 1)),
                TRIM(SUBSTR(BusinessFunction || ',', INSTR(BusinessFunction || ',', ',') + 1))
            FROM CombinedTable
            UNION ALL
            SELECT
                id,
                BusinessSector,
                BusinessFunction,
                MeasuringElt,
                Rating,
                SUbCategory,
                AsIsQuestions,
                ToBeQuestions,
                MaxRating,
                TRIM(SUBSTR(rest, 1, INSTR(rest, ',') - 1)),
                TRIM(SUBSTR(rest, INSTR(rest, ',') + 1))
            FROM split
            WHERE rest != ''
        )
        INSERT INTO ArrangingTheDataInProperOrder (
            BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, 
            AsIsQuestions, ToBeQuestions, MaxRating
        )
        SELECT
            BusinessSector, value, MeasuringElt, Rating, SUbCategory, 
            AsIsQuestions, ToBeQuestions, MaxRating
        FROM split
        WHERE value IS NOT NULL AND value != ''
    ''')

    connection.commit()
    connection.close()


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    unique_business_functions = []
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            # Process CSV file and insert into database
            process_csv(file)

            # Normalize the BusinessFunction column
            normalize_business_function()

            # Fetch unique business functions
            connection = sqlite3.connect('DigitalMaturityDatabase.db')
            cursor = connection.cursor()
            cursor.execute('SELECT DISTINCT BusinessFunction FROM ArrangingTheDataInProperOrder')
            unique_business_functions = cursor.fetchall()
            connection.close()

            # Redirect to view data
            return redirect(url_for('view_combined_data'))

    # Fetch unique business functions for GET request
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT BusinessFunction FROM ArrangingTheDataInProperOrder')
    unique_business_functions = cursor.fetchall()
    connection.close()

    return render_template('administrator.html', unique_business_functions=unique_business_functions)



def process_csv(csv_file):
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()

    # Convert file object to text mode
    csv_text = csv_file.stream.read().decode("utf-8")
    csv_data = csv.reader(csv_text.splitlines())

    next(csv_data)  # Skip header row if present
    for row in csv_data:
        if len(row) != 9:
            raise ValueError("CSV file must have exactly 9 columns")

        id, business_sector, business_function, measuring_elt, rating, sub_category, AsIsQuestions, ToBeQuestions, max_rating = row

        # Dynamically generate the as_is_question and to_be_question
        as_is_question = f"Wrt to the 10 best companies incorporating industry 4.0 key enablers making them digitally mature and transformed, how will you best describe your {sub_category}?"
        to_be_question = f"Wrt to the 10 best companies incorporating industry 4.0 key enablers making them digitally mature and transformed, where would you want to find {sub_category} in the future?"

        cursor.execute('''
            INSERT INTO CombinedTable (id, BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, AsIsQuestions, ToBeQuestions, MaxRating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id, business_sector, business_function, measuring_elt, rating, sub_category, as_is_question, to_be_question, max_rating))

    connection.commit()
    connection.close()


@app.route('/delete_combined_data', methods=['POST'])
def delete_combined_data():
    if request.method == 'POST':
        # Get the ID of the record to delete from the form
        delete_record_id = request.form['record_id']
        try:
            # Delete the record from the database
            connection = sqlite3.connect('DigitalMaturityDatabase.db')
            cursor = connection.cursor()
            cursor.execute('''
                DELETE FROM CombinedTable
                WHERE id = ?
            ''', (delete_record_id,))
            connection.commit()
            connection.close()

            # Redirect back to the page displaying combined data
            return redirect('/view_combined_data')
        except Exception as e:
            return "Error occurred during deletion: " + str(e)
    else:
        return "Method Not Allowed"


# Adding individual data into database
@app.route('/CombinedTiersForAll', methods=['GET', 'POST'])
def CombinedTiers():
    if request.method == 'POST':
        business_sector_name = request.form['business_sector_name']
        business_function_name = request.form['business_function']
        measuring_element_name = request.form['Measuring_Element']
        rating = request.form['Rating']
        subCategory_name = request.form['subCategory_name']

        # Dynamically generate the as_is_question and to_be_question
        as_is_question = f"Wrt to the 10 best companies incorporating industry 4.0 key enablers making them digitally mature and transformed, how will you best describe your {subCategory_name}?"
        to_be_question = f"Wrt to the 10 best companies incorporating industry 4.0 key enablers making them digitally mature and transformed, where would you want to find {subCategory_name} in the future?"

        MaxRating = request.form['MaxRating']

        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO CombinedTable (BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, AsIsQuestions, ToBeQuestions, MaxRating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (business_sector_name, business_function_name, measuring_element_name, rating, subCategory_name, as_is_question, to_be_question, MaxRating))
        connection.commit()
        connection.close()

        # Normalize the BusinessFunction column
        normalize_business_function()

        return redirect('/CombinedTiersForAll')

    return render_template('administrator.html')


# Updating the combined tiers
@app.route('/UpdateCombinedTiersForAll', methods=['GET', 'POST'])
def UpdateCombinedTiers():
    if request.method == 'POST':
        # Extract old values from the form
        oldbusiness_sector_name = request.form['oldbusiness_sector_name']
        oldbusiness_function = request.form['oldbusiness_function']
        oldmeasuring_element_name = request.form['oldMeasuring_Element']
        oldrating = request.form['oldRating']
        oldsubCategory_name = request.form['oldsubCategory_name']
        oldMaxRating = request.form['oldMaxRating']

        # Extract new values from the form
        newbusiness_sector_name = request.form['newbusiness_sector_name']
        newbusiness_function = request.form['newbusiness_function']
        newmeasuring_element_name = request.form['newMeasuring_Element']
        newrating = request.form['newRating']
        newsubCategory_name = request.form['newsubCategory_name']
        newMaxRating = request.form['newMaxRating']

        # Connect to the database
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()

        # Execute the SQL update query
        cursor.execute('''
            UPDATE CombinedTable 
            SET BusinessSector=?, BusinessFunction=?, MeasuringElt=?, Rating=?, SUbCategory=?, MaxRating=?
            WHERE BusinessSector=? AND BusinessFunction=? AND MeasuringElt=? AND Rating=? AND SUbCategory=? AND MaxRating=?
        ''', (newbusiness_sector_name, newbusiness_function, newmeasuring_element_name, newrating, newsubCategory_name, newMaxRating,
              oldbusiness_sector_name, oldbusiness_function, oldmeasuring_element_name, oldrating, oldsubCategory_name, oldMaxRating))

        # Commit changes and close connection
        connection.commit()
        connection.close()

        # Redirect back to administrator page
        return redirect('/administrator')

    return render_template('administrator.html')


# Rate the different business functions 
@app.route('/answerRatingForTheBusinessFunctions', methods=['GET', 'POST'])
def update_business_function_answer_rating():
    if request.method == 'POST':
        # Extract values from the form
        ratings = request.form.getlist('rating[]')
        business_functions = request.form.getlist('business_function[]')

        # Connect to the database
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()

        for i in range(len(business_functions)):
            # For each business function, update the AnswerRating and AnswerRatingValue
            cursor.execute('''
                UPDATE ArrangingTheDataInProperOrder 
                SET AnswerRating = ?, AnswerRatingValue = ?
                WHERE BusinessFunction = ?
            ''', ('BASIC', ratings[i], business_functions[i]))

        # Commit changes and close connection
        connection.commit()
        connection.close()

        # Redirect back to administrator page
        return redirect('/administrator')

    return render_template('administrator.html')


# Business_Manager_account 


























if __name__ == '__main__':
    app.run(debug=True)
