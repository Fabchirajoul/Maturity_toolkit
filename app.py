import sqlite3
import bcrypt
from flask import Flask, request, render_template, redirect, session, url_for, jsonify
import csv
import numpy as np
import io
import base64
import random
import string
import numpy as np
import base64
import math
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import time




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
        connection.close()


def create_combined_table():
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
        connection.close()

def create_forgot_password_table():
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ForgotPassword (
                email TEXT UNIQUE NOT NULL

            )
        ''')
        connection.commit()
        connection.close()


def create_trimmed_table():
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
        connection.close()


def create_answer_rating_table():
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS AnswerRatings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                BusinessFunction TEXT,
                RatingName TEXT,
                RatingDescription,
                AnswerRatingValue INTEGER
            )
        ''')
        connection.commit()
        connection.close()

def create_user_submission_record_table():
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserSubmissionRecord (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            UniqueCodeUser TEXT,
            BusinessFunction TEXT,
            MeasuringEltUser TEXT,
            RatingUser INTEGER,
            SUbCategoryUser TEXT,
            AsIsQuestionsUser TEXT,
            AnswersUserAsIs TEXT,
            ToBeQuestionsUser TEXT,
            AnswersUserToBe TEXT,
            MaxRatingUser INTEGER DEFAULT 5,
            ExpectedCumSum INTEGER,
            UserCumSumAsIs INTEGER,
            UserCumSumToBe INTEGER
        )
    ''')
    connection.commit()
    connection.close()

def create_final_feedback_data():
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserSubmittedFeedback (
            UniqueCodeUser TEXT,
            BusinessFunction TEXT,  
            MeasuringEltUser TEXT,
            RatingUser INTEGER,
            SUbCategoryUser TEXT,
            AnswersUserAsIs TEXT,
            AnswersUserToBe TEXT,   
            MaxRatingUser INTEGER DEFAULT 5,
            ExpectedCumSum INTEGER,
            UserCumSumAsIs INTEGER,
            UserCumSumToBe INTEGER,
            PercentageAsIs INTEGER,
            PercentageToBe INTEGER,
            FeedbackAsIs TEXT,
            FeedbackToBe TEXT,
            GrowthRate INTEGER,
            Duration INTEGER
                   
        )
    ''')
    connection.commit()
    connection.close()

# Create tables
create_user_table()
create_combined_table()
create_trimmed_table()
create_answer_rating_table()
create_user_submission_record_table()
create_final_feedback_data()
create_forgot_password_table()


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




@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    Password_error = None  # Initialize Password_error

    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['newpassword']
        confirm_new_password = request.form['confnewpassword']

        if new_password != confirm_new_password:
            Password_error = 'Passwords do not match'
            return render_template('administrator.html', Password_error=Password_error)

        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()

        # Check if the email exists in the database
        cursor.execute('SELECT * FROM User WHERE email=?', (email,))
        user = cursor.fetchone()

        if user:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('UPDATE User SET password=? WHERE email=?', (hashed_password, email))
            connection.commit()
            connection.close()
            Password_error = "Password updated successfully"
            time.sleep(5)
        else:
            Password_error = "Email does not exist"
            time.sleep(5)
            connection.close()

    return render_template('administrator.html', Password_error=Password_error)


@app.route('/requestPasswordChange', methods=['GET', 'POST'])
def PasswordChange():
    if request.method == 'POST':
        emailReset = request.form['password_reset']  

        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()

        # Check if the email exists in the database
        cursor.execute('SELECT * FROM User WHERE email=?', (emailReset,))
        user = cursor.fetchone()

        if user:
            cursor.execute('''
                INSERT INTO ForgotPassword (email)
                VALUES (?)
            ''', (emailReset,))
            connection.commit()
            connection.close()
            requestMessage = "Your request has been received. Wait for an administrator to email your new password credentials."
        else:
            requestMessage = "Email does not exist"
            connection.close()

        # Adding a delay
        import time
        time.sleep(5)

        return redirect(url_for('PasswordChange', requestMessage=requestMessage))

    requestMessage = request.args.get('requestMessage')
    return render_template('ForgotPassword.html', requestMessage=requestMessage)











   































# BusinessManager
@app.route('/BusinessManager')
def dashboardBusinessManager():
    business_functions_data={}
    if session.get('email'):
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (session['email'],))
        user = cursor.fetchone()
        connection.close()
        return render_template('manager.html', user=user, business_data=business_functions_data)

    return redirect('/login')

# Business analysts 
@app.route('/userAccount')
def dashboardBusinessbusinessAnalysts():
    if session.get('email'):
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (session['email'],))
        user = cursor.fetchone()
        connection.close()
        return render_template('userAccount.html', user=user)

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



@app.route('/ratingAnswersBusinessFunctions', methods=['GET', 'POST'])
def answerratingforbusinesssector():
    if request.method == 'POST':
        business_sector_name = request.form['rating_business_sector_name']
        business_name_business_sector = request.form['rating_name_business_sector']
        description_name_business_sector = request.form['rating_description_business_sector']
        rating_value_business_sector = request.form['rating_value_business_sector']

        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO AnswerRatings (BusinessFunction, RatingName, RatingDescription, AnswerRatingValue)
            VALUES (?, ?, ?, ?)
        ''', (business_sector_name, business_name_business_sector, description_name_business_sector, rating_value_business_sector))
        connection.commit()
        connection.close()

        # Normalize the BusinessFunction column
        normalize_business_function()

        return redirect('/CombinedTiersForAll')

    return render_template('administrator.html')

# Updating the combined tiers
@app.route('/updateratingAnswersBusinessFunctions', methods=['GET', 'POST'])
def Updateanswerrating():
    if request.method == 'POST':
        # Extract values from the form
        business_sector_name = request.form['rating_business_sector_name']
        business_name_business_sector = request.form['rating_name_business_sector']
        description_name_business_sector = request.form['newrating_description_business_sector']
        rating_value_business_sector = request.form['newrating_value_business_sector']

        # Connect to the database
        connection = sqlite3.connect('DigitalMaturityDatabase.db')
        cursor = connection.cursor()

        # Execute the SQL update query
        cursor.execute('''
            UPDATE AnswerRatings 
            SET RatingDescription=?, AnswerRatingValue=?
            WHERE BusinessFunction=? AND RatingName=?
        ''', (description_name_business_sector, rating_value_business_sector, business_sector_name, business_name_business_sector))

        # Commit changes and close connection
        connection.commit()
        connection.close()

        # Redirect back to administrator page
        return redirect('/administrator')

    return render_template('administrator.html')







# Business_Manager_account 

def add_random_characters(word, num_chars=12):
    def generate_random_string(length):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(length))
    
    return word + generate_random_string(num_chars)

@app.route('/add_random_characters', methods=['GET', 'POST'])
def add_random_characters_route():
    business_functions_data = {}  # Ensure this is a dictionary
    modified_word = None
    if request.method == 'POST':
        word = request.form['word']
        modified_word = add_random_characters(word)
    return render_template('manager.html', modified_word=modified_word, business_data=business_functions_data)



def get_unique_business_sectors():
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT BusinessSector FROM ArrangingTheDataInProperOrder')
    business_sectors = cursor.fetchall()
    connection.close()
    return business_sectors

def get_the_different_answer_rating_for_sector(selected_sector):
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()
    cursor.execute('SELECT RatingName, RatingDescription, AnswerRatingValue FROM AnswerRatings WHERE BusinessFunction=?', (selected_sector,))
    business_sectors_rating = cursor.fetchall()
    connection.close()
    return business_sectors_rating


def get_answer_rating_column_names():
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()
    cursor.execute('PRAGMA table_info(AnswerRatings)')
    columns = cursor.fetchall()
    connection.close()
    return [col[1] for col in columns]





@app.route('/select_business_sector_user', methods=['GET', 'POST'])
def select_business_sector():
    business_sectors = get_unique_business_sectors()
    sector_data = []
    user_photo_base64 = None
    user = None
    error_message_user_business_sector = ""
    business_sector_rating = []

    if request.method == 'POST':
        selected_sector = request.form.get('business_sector_user', None)

        if selected_sector:
            connection = sqlite3.connect('DigitalMaturityDatabase.db')
            cursor = connection.cursor()
            cursor.execute('''
                SELECT DISTINCT BusinessFunction
                FROM ArrangingTheDataInProperOrder
                WHERE BusinessSector=?
            ''', (selected_sector,))
            sector_data = cursor.fetchall()
            connection.close()

            business_sector_rating = get_the_different_answer_rating_for_sector(selected_sector)
            session['business_sector_rating'] = business_sector_rating  # Store in session
            # print("These are the answer ratings: ", business_sector_rating)

            return render_template('BusinessFunction.html', user=user, user_photo_base64=user_photo_base64,
                                   sector_data=sector_data, business_sectors=business_sectors,
                                   BusinessError=error_message_user_business_sector, business_sector_rating=business_sector_rating)

        else:
            error_message_user_business_sector = "Please select a business sector"

    return render_template('userAccount.html', user=user, user_photo_base64=user_photo_base64,
                           sector_data=sector_data, business_sectors=business_sectors,
                           BusinessError=error_message_user_business_sector, business_sector_rating=business_sector_rating)







@app.route('/select_business_function_in_business_function_html_page', methods=['GET', 'POST'])
def select_business_function():
    business_function_selected_data = []
    business_sector_rating = []
    answer_rating_columns = []
    user_photo_base64 = None
    user = None
    SectorError = ""

    if request.method == 'POST':
        selected_business_function = request.form.get('business_function_user', None)

        if selected_business_function:
            connection = sqlite3.connect('DigitalMaturityDatabase.db')
            cursor = connection.cursor()
            cursor.execute('''
                SELECT MeasuringElt, Rating, SUbCategory, AsIsQuestions, ToBeQuestions, MaxRating
                FROM ArrangingTheDataInProperOrder
                WHERE BusinessFunction=?
            ''', (selected_business_function,))
            business_function_selected_data = cursor.fetchall()
            connection.close()

            answer_rating_columns = get_answer_rating_column_names()
            business_sector_rating = session.get('business_sector_rating', [])
            session['selected_business_function'] = selected_business_function  # Store selected business function in session

            

            return render_template('AsIsandToBeQuestionandAnswer.html', user=user, user_photo_base64=user_photo_base64,
                                   business_function_selected_data=business_function_selected_data,
                                   SectorError=SectorError, business_sector_rating=business_sector_rating,
                                   answer_rating_columns=answer_rating_columns)
        else:
            SectorError = "You did not select a business function. Now you have to start all over again"

    return render_template('BusinessFunction.html', user=user, user_photo_base64=user_photo_base64,
                           SectorError=SectorError, business_function_selected_data=business_function_selected_data,
                           business_sector_rating=business_sector_rating, answer_rating_columns=answer_rating_columns)



@app.route('/userSubmissionDataIntoTable', methods=['GET', 'POST'])
def CombinedTiersForUser():
    error_display_asistobe = None  # Initialize error_display_asistobe

    if request.method == 'POST':
        UserSubmittedUniqueCode = request.form['Unique_code_from_User']
        measuring_element_name_user = request.form.getlist('Measuring_element_user[]')
        rating_user = request.form.getlist('Rting_User[]')
        sub_category_name_user = request.form.getlist('sub_category_for_user[]')
        as_is_questions_user = request.form.getlist('as_is_questions_user[]')
        answers_user_as_is = request.form.getlist('UserAnswerRatingAsIs[]')
        to_be_questions_user = request.form.getlist('to_be_questions_user[]')
        answers_user_to_be = request.form.getlist('UserAnswerRatingToBe[]')

        selected_business_function = session.get('selected_business_function', None)  # Get selected business function from session

        if not answers_user_as_is or not answers_user_to_be:
            error_display_asistobe = "An error occurred. Please make sure to select an answer for every question before submitting your answers."
            print("Error message:", error_display_asistobe)
        else:
            connection = sqlite3.connect('DigitalMaturityDatabase.db')
            cursor = connection.cursor()

            # Get max rating value from AnswerRatings table
            cursor.execute('SELECT MAX(AnswerRatingValue) FROM AnswerRatings')
            max_rating_user = cursor.fetchone()[0]

            for i in range(len(measuring_element_name_user)):
                rating_user_val = float(rating_user[i])
                user_answer_rating_as_is = float(answers_user_as_is[i])
                user_answer_rating_to_be = float(answers_user_to_be[i])

                expected_cum_sum = rating_user_val * max_rating_user
                user_cum_sum_as_is = rating_user_val * user_answer_rating_as_is
                user_cum_sum_to_be = rating_user_val * user_answer_rating_to_be

                cursor.execute('''
                    INSERT INTO UserSubmissionRecord (
                        UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser, 
                        AsIsQuestionsUser, AnswersUserAsIs, ToBeQuestionsUser, AnswersUserToBe, 
                        MaxRatingUser, ExpectedCumSum, UserCumSumAsIs, UserCumSumToBe)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (UserSubmittedUniqueCode, selected_business_function, measuring_element_name_user[i], rating_user_val,
                      sub_category_name_user[i], as_is_questions_user[i], user_answer_rating_as_is,
                      to_be_questions_user[i], user_answer_rating_to_be, max_rating_user,
                      expected_cum_sum, user_cum_sum_as_is, user_cum_sum_to_be))

            connection.commit()
            connection.close()

            feedback_function()

            # Redirect to the user account page
            return redirect('/select_business_sector_user')

    return render_template('BusinessFunction.html', error_display_asistobe=error_display_asistobe)






















def feedback_function():
    connection = sqlite3.connect('DigitalMaturityDatabase.db')
    cursor = connection.cursor()

    # Select distinct UniqueCodeUser and BusinessFunction from UserSubmissionRecordTrimmed
    cursor.execute('''
        SELECT DISTINCT UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser, 
                        AnswersUserAsIs, AnswersUserToBe, MaxRatingUser, ExpectedCumSum, 
                        UserCumSumAsIs, UserCumSumToBe
        FROM UserSubmissionRecord
    ''')
    trimmed_records = cursor.fetchall()

    # Insert each distinct record into UserSubmittedFeedback
    for record in trimmed_records:
        (UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser,
         AnswersUserAsIs, AnswersUserToBe, MaxRatingUser, ExpectedCumSum,
         UserCumSumAsIs, UserCumSumToBe) = record

        # Calculate percentages
        percentage_as_is = round(
            (UserCumSumAsIs / ExpectedCumSum) * 100, 2) if ExpectedCumSum != 0 else 0
        percentage_to_be = round(
            (UserCumSumToBe / ExpectedCumSum) * 100, 2) if ExpectedCumSum != 0 else 0

        # Growth rate calculation
        growth_rate = round(((percentage_to_be- percentage_as_is) /
                            percentage_as_is) * 100, 2) if percentage_as_is != 0 else 0

        # Calculate the duration in years
        duration = round(math.log(UserCumSumToBe / UserCumSumAsIs) /
                         math.log(1 + growth_rate / 100), 4) if growth_rate != 0 else 0

        # Generate feedback based on percentages
        feedback_as_is = generate_feedback(percentage_as_is)
        feedback_to_be = generate_feedback(percentage_to_be)

        # Insert feedback into UserSubmittedFeedback
        cursor.execute('''
            INSERT INTO UserSubmittedFeedback (
                UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser, 
                AnswersUserAsIs, AnswersUserToBe, MaxRatingUser, ExpectedCumSum, 
                UserCumSumAsIs, UserCumSumToBe, PercentageAsIs, PercentageToBe, 
                FeedbackAsIs, FeedbackToBe, GrowthRate, Duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser,
            AnswersUserAsIs, AnswersUserToBe, MaxRatingUser, ExpectedCumSum,
            UserCumSumAsIs, UserCumSumToBe, percentage_as_is, percentage_to_be,
            feedback_as_is, feedback_to_be, growth_rate, duration
        ))

    # Commit changes to the database and close the connection
    connection.commit()
    connection.close()


def generate_feedback(percentage):
    if 0 <= percentage <= 15.5:
        return "Stage 0:, Level: Incomplete, Aspect practices are yet to be implemented or incomplete, Organisation only performs essential operations."
    elif 16 <= percentage <= 34.5:
        return "Stage 1, Level Performed, Aspect practices are fully implemented. Transition to Industry 4.0 has commenced"
    elif 35 <= percentage <= 50.5:
        return "Stage 2, level Managed, Initial implementation of Industry 4.0 technologies.No integration yet.Physical systems can be represented virtually"
    elif 51 <= percentage <= 67.5:
        return "Stage 3: Level: Established, Vertical integration from shop floor to ERP level, Standardisation of processes and operations"
    elif 68 <= percentage <= 84.5:
        return "Stage 4: Level: Predictable, Horizontal integration across the value chain.Application of Industry 4.0 technologies such Big Data and artificial intelligence.autonomous optimisation"
    elif 85 <= percentage <= 100:
        return "Stage 5: Level: Optimizing, End-to-end integration.Continuous improvement.Smart and autonomous optimisation."










@app.route('/submit_unique_code', methods=['GET', 'POST'])
def submitting_unique_code():
    error_message = None
    business_functions_data = {}
    plot_images = []
    bar_plot_images = []
    growth_rate_images = []

    if request.method == 'POST':
        unique_code = request.form['unique_code_user']

        if unique_code:
            connection = sqlite3.connect('DigitalMaturityDatabase.db')
            cursor = connection.cursor()

            cursor.execute('''
                SELECT BusinessFunction, MeasuringEltUser, ExpectedCumSum, UserCumSumAsIs, UserCumSumToBe, PercentageAsIs, PercentageToBe, FeedbackAsIs, FeedbackToBe, GrowthRate, Duration
                FROM UserSubmittedFeedback
                WHERE UniqueCodeUser = ? AND PercentageAsIs IS NOT NULL AND PercentageToBe IS NOT NULL AND FeedbackAsIs IS NOT NULL AND FeedbackToBe IS NOT NULL AND GrowthRate IS NOT NULL AND Duration IS NOT NULL  
                GROUP BY BusinessFunction, MeasuringEltUser
                ORDER BY BusinessFunction, MeasuringEltUser;
            ''', (unique_code,))
            rows = cursor.fetchall()
            connection.close()

            if not rows:
                error_message = "No records found for the provided unique code."
                return render_template('manager.html', error_message=error_message)

            for row in rows:
                business_function, measuring_elt_user, exped_sum, as_is_sum, to_be_sum, percent_maturity_as_is, percent_maturity_to_be, feedback_as_is, feedback_to_be, growth_rate, time_to_grow = row
                if business_function not in business_functions_data:
                    business_functions_data[business_function] = []
                business_functions_data[business_function].append(
                    (measuring_elt_user, exped_sum, as_is_sum, to_be_sum, percent_maturity_as_is,
                     percent_maturity_to_be, feedback_as_is, feedback_to_be, growth_rate, time_to_grow)
                )

            for business_function, data in business_functions_data.items():
                if not data:
                    continue
                labels = [item[0] for item in data]
                exped_sums = [item[1] for item in data]
                as_is_sums = [item[2] for item in data]
                to_be_sums = [item[3] for item in data]
                growth_rates = [item[8] for item in data]
                durations = [item[9] for item in data]

                if not labels or not exped_sums or not as_is_sums or not to_be_sums:
                    continue

                angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
                angles += angles[:1]

                plt.figure(figsize=(10, 10))  # Increase the size of the polar plots
                ax = plt.subplot(111, polar=True)
                ax.plot(angles, as_is_sums + [as_is_sums[0]],
                        'o-', linewidth=2, label='AS IS', color='red')
                ax.fill(angles, as_is_sums +
                        [as_is_sums[0]], alpha=0.4, color='red')
                ax.plot(angles, to_be_sums + [to_be_sums[0]],
                        'o-', linewidth=2, label='TO BE', color='blue')
                ax.fill(angles, to_be_sums +
                        [to_be_sums[0]], alpha=0.4, color='blue')
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels, color='grey', size=8)

                ax.set_title(business_function, size=10,
                             color='black', weight='bold')
                ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plot_image = base64.b64encode(buf.getvalue()).decode('utf-8')
                plot_images.append(plot_image)
                plt.close()

                # Create bar plot for each business function
                plt.figure(figsize=(10, 6))
                bar_width = 0.25
                index = np.arange(len(labels))

                plt.bar(index, exped_sums, bar_width,
                        label='Position of 10 best performing organization')
                plt.bar(index + bar_width, as_is_sums,
                        bar_width, label='Current position of your organization')
                plt.bar(index + 2 * bar_width, to_be_sums,
                        bar_width, label='Expected position of your organization')

                plt.xlabel('Measuring Element')
                plt.ylabel('Values')
                plt.title(f'{business_function}')
                plt.xticks(index + bar_width, labels, rotation=45)
                plt.legend()

                for i in range(len(labels)):
                    plt.text(i, exped_sums[i], exped_sums[i], ha='center')
                    plt.text(i + bar_width,
                             as_is_sums[i], as_is_sums[i], ha='center')
                    plt.text(i + 2 * bar_width,
                             to_be_sums[i], to_be_sums[i], ha='center')

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                bar_plot_image = base64.b64encode(
                    buf.getvalue()).decode('utf-8')
                bar_plot_images.append(bar_plot_image)
                plt.close()

                # Create growth rate curve for each business function
                for idx in range(len(labels)):
                    x_values = np.linspace(0, durations[idx], 100)
                    growth_rate = growth_rates[idx]
                    y_values = to_be_sums[idx] * np.exp(growth_rate * x_values)
                    plt.plot(x_values, y_values, label=f'{labels[idx]} Growth Curve')

                plt.xlabel('Time (Years)')
                plt.ylabel('Value')
                plt.title(f'Exponential growth curve for :{business_function}')
                plt.legend()
                plt.tight_layout()  # Adjust layout for better spacing

                # Convert plot to base64
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0)
                img_str = base64.b64encode(img_buffer.getvalue()).decode()
                growth_rate_images.append(img_str)
                plt.close()

    return render_template('manager.html', error_message=error_message,
                           plot_images=plot_images, business_data=business_functions_data,
                           bar_plot_images=bar_plot_images, growth_rate_images=growth_rate_images)


























if __name__ == '__main__':
    app.run(debug=True)




