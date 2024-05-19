import numpy as np
import io
import csv
import base64
from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3
import bcrypt
import random
import string
import math
from flask import jsonify
import matplotlib.pyplot as plt
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
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            account_type TEXT,
            password TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()


# combined table
def create_combined_table():
    connection = sqlite3.connect('database.db')
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


def create_user_submission_record_table():
    connection = sqlite3.connect('database.db')
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


# Recreate the table to ensure the schema is correct
create_user_submission_record_table()

# TO hold trimmed records


def create_user_submission_trimmed_record_table():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserSubmissionRecordTrimmed (
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
    connection = sqlite3.connect('database.db')
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


create_user_table()
create_combined_table()
create_user_submission_record_table()
create_final_feedback_data()
create_user_submission_trimmed_record_table()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_type = request.form['users']

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            connection.close()
            return render_template('register.html', error='User with this email already exists')

        hashed_password = bcrypt.hashpw(password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT INTO User (name, email, password, account_type) VALUES (?, ?, ?, ?)',
                       (name, email, hashed_password, account_type))
        connection.commit()
        connection.close()

        return redirect('/login')

    return render_template('register.html')


# Admin register
@app.route('/Adminregister', methods=['GET', 'POST'])
def adminregister():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_type = request.form['users']

        if password != confirm_password:
            return render_template('administrator.html', error='Passwords do not match')

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            connection.close()
            return render_template('administrator.html', error='User with this email already exists')

        hashed_password = bcrypt.hashpw(password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT INTO User (name, email, password, account_type) VALUES (?, ?, ?, ?)',
                       (name, email, hashed_password, account_type))
        connection.commit()
        connection.close()

        return redirect('/administrator')

    return render_template('administrator.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        account_type = request.form['users']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')) and user[3] == account_type:
            session['email'] = user[2]
            if account_type == "Administrator":
                return redirect('/administrator')
            elif account_type == "Business Analyst":
                return redirect('/userAccount')
        else:
            error_message = "Invalid credentials. Please make sure to enter the correct email, password, and account type."
            return render_template('login.html', error=error_message)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return render_template('index.html')


@app.route('/userAccount')
def dashboardBusinessAnalyst():
    if session.get('email'):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (session['email'],))
        user = cursor.fetchone()

        connection.close()
        return render_template('userAccount.html', user=user)
    return redirect('/login')


@app.route('/administrator')
def dashboardAdministrator():
    if session.get('email'):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM User WHERE email=?', (session['email'],))
        user = cursor.fetchone()
        connection.close()
        return render_template('administrator.html', user=user)

    return redirect('/login')

# Creating the combined all tiers


@app.route('/CombinedTiersForAll', methods=['GET', 'POST'])
def CombinedTiers():
    if request.method == 'POST':
        business_sector_name = request.form['business_sector_name']
        business_function_name = request.form['business_function']
        measuring_element_name = request.form['Measuring_Element']
        rating = request.form['Rating']
        subCategory_name = request.form['subCategory_name']

        # Dynamically generate the as_is_question and to_be_question
        as_is_question = f"Wrt to the 10 best companies incorporating industry 4.0 key enablers making them digitally mature and transformed, how will you best describe your {
            subCategory_name}?"
        to_be_question = f"Wrt to the 10 best companies incorporating industry 4.0 key enablers making them digitally mature and transformed, where would you want to find {
            subCategory_name} in the future?"

        MaxRating = request.form['MaxRating']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO CombinedTable (BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, AsIsQuestions, ToBeQuestions, MaxRating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (business_sector_name, business_function_name, measuring_element_name, rating, subCategory_name, as_is_question, to_be_question, MaxRating))
        connection.commit()
        connection.close()

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
        connection = sqlite3.connect('database.db')
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


# Route to delete a record from CombinedTable


@app.route('/delete_combined_data', methods=['POST'])
def delete_combined_data():
    if request.method == 'POST':
        # Get the ID of the record to delete from the form
        delete_record_id = request.form['record_id']
        try:
            # Delete the record from the database
            connection = sqlite3.connect('database.db')
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
# delete user record


@app.route('/delete_user_data', methods=['POST'])
def delete_user_record_data():
    if request.method == 'POST':
        # Get the ID of the record to delete from the form
        delete_record_user_id = request.form['user_record_id']
        try:
            # Delete the record from the database
            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute('''
                DELETE FROM User
                WHERE name = ?
            ''', (delete_record_user_id,))
            connection.commit()
            connection.close()

            # Redirect back to the page displaying combined data
            return redirect('/view_combined_data')
        except Exception as e:

            return "Error occurred during deletion: " + str(e)
    else:
        return "Method Not Allowed"


# Displaying the elements in the databse on the admin side of the panel
@app.route('/view_combined_data', methods=['GET', 'POST'])
def view_combined_data():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, AsIsQuestions, ToBeQuestions, MaxRating
        FROM CombinedTable
    ''')
    combined_data = cursor.fetchall()
    connection.close()

    return render_template('administrator.html', combined_data=combined_data)

# Route to display all user account


@app.route('/view_all_user', methods=['GET', 'POST'])
def view_user_account():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT name, email, account_type
        FROM User
    ''')
    all_data = cursor.fetchall()
    connection.close()

    return render_template('administrator.html', all_data=all_data)


# uploading csv file to database
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            # Process CSV file and insert into database
            process_csv(file)
            # Redirect to view data
            return redirect(url_for('view_combined_data'))
    return render_template('administrator.html')


def process_csv(csv_file):
    connection = sqlite3.connect('database.db')
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
        as_is_question = f"Wrt to the 10 best companies incorporating industry 4.0 key enablers making them digitally mature and transformed, how will you best describe your {
            sub_category}?"
        to_be_question = f"Wrt to the 10 best companies incorporating industry 4.0 key enablers making them digitally mature and transformed, where would you want to find {
            sub_category} in the future?"

        cursor.execute('''
            INSERT INTO CombinedTable (id, BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, AsIsQuestions, ToBeQuestions, MaxRating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id, business_sector, business_function, measuring_elt, rating, sub_category, as_is_question, to_be_question, max_rating))

    connection.commit()
    connection.close()


def generate_random_text():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(12))


# Function to get unique records of the business sector when they are selected
@app.route('/select_business_sector_user', methods=['GET', 'POST'])
def select_business_sector():
    business_functions_data = {}  # Initialize business_functions_data
    error_message_user_business_sector = None
    sector_data = []
    random_text = None  # Initialize random_text to None

    if request.method == 'POST':
        selected_sector = request.form.get('business_sector_user', None)

        if selected_sector:
            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute('''
                SELECT BusinessFunction, MeasuringElt, Rating, SUbCategory, AsIsQuestions, ToBeQuestions, MaxRating
                FROM CombinedTable
                WHERE BusinessSector=?
            ''', (selected_sector,))
            sector_data = cursor.fetchall()
            connection.close()

            # Generate random text
            random_text = generate_random_text()
        else:
            error_message_user_business_sector = "Please select a business sector"

    return render_template('userAccount.html', sector_data=sector_data, business_sectors=get_unique_business_sectors(), BusinessError=error_message_user_business_sector, random_text=random_text, business_data=business_functions_data)


def get_unique_business_sectors():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT BusinessSector FROM CombinedTable')
    business_sectors = cursor.fetchall()
    connection.close()
    return business_sectors


# Submitting answers into the database
@app.route('/userSubmissionDataIntoTable', methods=['GET', 'POST'])
def CombinedTiersForUser():
    error_display_asistobe = None  # Initialize error_display_asistobe

    if request.method == 'POST':
        UserSubmittedUniqueCode = request.form['Unique_code_from_User']
        business_function_name_user = request.form.getlist(
            'business_function_user[]')
        measuring_element_name_user = request.form.getlist(
            'Measuring_element_user[]')
        rating_user = request.form.getlist('Rting_User[]')
        sub_category_name_user = request.form.getlist(
            'sub_category_for_user[]')
        as_is_questions_user = request.form.getlist('questions_user[]')
        answers_user_as_is = request.form.getlist('UserAnswerRatingAsIs[]')
        to_be_questions_user = request.form.getlist('UserAnswerRatingToBe[]')

        if not answers_user_as_is or not to_be_questions_user:
            error_display_asistobe = "An error occurred. Please make sure to select an answer for every question before submitting your answers."
            print("Error message:", error_display_asistobe)
        else:
            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()

            for i in range(len(measuring_element_name_user)):
                rating_user_val = float(rating_user[i])
                user_answer_rating_as_is = float(answers_user_as_is[i])
                user_answer_rating_to_be = float(to_be_questions_user[i])
                max_rating_user = 5

                expected_cum_sum = rating_user_val * max_rating_user
                user_cum_sum_as_is = rating_user_val * user_answer_rating_as_is
                user_cum_sum_to_be = rating_user_val * user_answer_rating_to_be

                cursor.execute('''
                        INSERT INTO UserSubmissionRecord (
                            UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser, 
                            AsIsQuestionsUser, AnswersUserAsIs, ToBeQuestionsUser, AnswersUserToBe, 
                            MaxRatingUser, ExpectedCumSum, UserCumSumAsIs, UserCumSumToBe)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (UserSubmittedUniqueCode, business_function_name_user[i], measuring_element_name_user[i], rating_user_val,
                          sub_category_name_user[i], as_is_questions_user[i], user_answer_rating_as_is,
                          to_be_questions_user[i], user_answer_rating_to_be, max_rating_user,
                          expected_cum_sum, user_cum_sum_as_is, user_cum_sum_to_be))

            connection.commit()
            connection.close()

            # Normalize the BusinessFunction column
            normalize_business_function()
            feedback_function()

            # Redirect to the user account page
            return redirect('/select_business_sector_user')

    return render_template('userAccount.html', error_display_asistobe=error_display_asistobe)


def normalize_business_function():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('''
        WITH RECURSIVE split(id, UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser, AsIsQuestionsUser, AnswersUserAsIs, ToBeQuestionsUser, AnswersUserToBe, MaxRatingUser, ExpectedCumSum, UserCumSumAsIs, UserCumSumToBe, value, rest) AS (
            SELECT
                id,
                UniqueCodeUser,
                BusinessFunction,
                MeasuringEltUser,
                RatingUser,
                SUbCategoryUser,
                AsIsQuestionsUser,
                AnswersUserAsIs,
                ToBeQuestionsUser,
                AnswersUserToBe,
                MaxRatingUser,
                ExpectedCumSum,
                UserCumSumAsIs,
                UserCumSumToBe,
                TRIM(SUBSTR(BusinessFunction || ',', 1, INSTR(BusinessFunction || ',', ',') - 1)),
                TRIM(SUBSTR(BusinessFunction || ',', INSTR(BusinessFunction || ',', ',') + 1))
            FROM UserSubmissionRecord
            UNION ALL
            SELECT
                id,
                UniqueCodeUser,
                BusinessFunction,
                MeasuringEltUser,
                RatingUser,
                SUbCategoryUser,
                AsIsQuestionsUser,
                AnswersUserAsIs,
                ToBeQuestionsUser,
                AnswersUserToBe,
                MaxRatingUser,
                ExpectedCumSum,
                UserCumSumAsIs,
                UserCumSumToBe,
                TRIM(SUBSTR(rest, 1, INSTR(rest, ',') - 1)),
                TRIM(SUBSTR(rest, INSTR(rest, ',') + 1))
            FROM split
            WHERE rest != ''
        )
        INSERT INTO UserSubmissionRecordTrimmed (
            UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser, 
            AsIsQuestionsUser, AnswersUserAsIs, ToBeQuestionsUser, AnswersUserToBe, 
            MaxRatingUser, ExpectedCumSum, UserCumSumAsIs, UserCumSumToBe
        )
        SELECT 
            UniqueCodeUser,
            value AS BusinessFunction,
            MeasuringEltUser,
            RatingUser,
            SUbCategoryUser,
            AsIsQuestionsUser,
            AnswersUserAsIs,
            ToBeQuestionsUser,
            AnswersUserToBe,
            MaxRatingUser,
            ExpectedCumSum,
            UserCumSumAsIs,
            UserCumSumToBe
        FROM split
        WHERE value != '';
    ''')

    connection.commit()
    connection.close()

# I am here now


def feedback_function():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Select distinct UniqueCodeUser and BusinessFunction from UserSubmissionRecordTrimmed
    cursor.execute('''
        SELECT DISTINCT UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser, 
                        AnswersUserAsIs, AnswersUserToBe, MaxRatingUser, ExpectedCumSum, 
                        UserCumSumAsIs, UserCumSumToBe
        FROM UserSubmissionRecordTrimmed
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
        growth_rate = round(((UserCumSumToBe - ExpectedCumSum) /
                            ExpectedCumSum) * 100, 2) if ExpectedCumSum != 0 else 0

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

# Route to view feedback data


@app.route('/view_feedback', methods=['GET'])
def view_feedback():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser, 
               AnswersUserAsIs, AnswersUserToBe, MaxRatingUser, ExpectedCumSum, 
               UserCumSumAsIs, UserCumSumToBe, PercentageAsIs, PercentageToBe, 
               FeedbackAsIs, FeedbackToBe, GrowthRate, Duration
        FROM UserSubmittedFeedback
    ''')
    feedback_data = cursor.fetchall()
    connection.close()

    return render_template('userAccount.html', feedback_data=feedback_data)


@app.route('/submit_unique_code', methods=['GET', 'POST'])
def submitting_unique_code():
    error_message = None
    business_functions_data = {}  # Initialize business_functions_data
    plot_images = []

    if request.method == 'POST':
        unique_code = request.form['unique_code_user']

        if unique_code:
            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()

            cursor.execute('''
                SELECT BusinessFunction, MeasuringEltUser, PercentageAsIs, PercentageToBe, FeedbackAsIs, FeedbackToBe, GrowthRate, Duration
                FROM UserSubmittedFeedback
                WHERE UniqueCodeUser = ? AND PercentageAsIs IS NOT NULL AND PercentageToBe IS NOT NULL AND FeedbackAsIs IS NOT NULL AND FeedbackToBe IS NOT NULL AND GrowthRate IS NOT NULL AND Duration IS NOT NULL  
                GROUP BY BusinessFunction, MeasuringEltUser
                ORDER BY BusinessFunction, MeasuringEltUser;
            ''', (unique_code,))
            rows = cursor.fetchall()
            connection.close()

            for row in rows:
                business_function, measuring_elt_user, percent_maturity_as_is, percent_maturity_to_be, feedback_as_is, feedback_to_be, growth_rate, time_to_grow = row
                if business_function not in business_functions_data:
                    business_functions_data[business_function] = []
                business_functions_data[business_function].append(
                    (measuring_elt_user, percent_maturity_as_is, percent_maturity_to_be, feedback_as_is, feedback_to_be, growth_rate, time_to_grow)
                )

            for business_function, data in business_functions_data.items():
                labels = [item[0] for item in data]
                as_is = [item[1] for item in data]
                to_be = [item[2] for item in data]
                angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
                angles += angles[:1]

                plt.figure(figsize=(4, 4))
                ax = plt.subplot(111, polar=True)
                ax.plot(angles, as_is + [as_is[0]], 'o-', linewidth=2, label='AS IS', color='red')
                ax.fill(angles, as_is + [as_is[0]], alpha=0.4, color='red')
                ax.plot(angles, to_be + [to_be[0]], 'o-', linewidth=2, label='TO BE', color='blue')
                ax.fill(angles, to_be + [to_be[0]], alpha=0.4, color='blue')
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels, color='grey', size=8)

                ax.set_title(business_function, size=10, color='black', weight='bold')
                ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plot_image = base64.b64encode(buf.getvalue()).decode('utf-8')
                plot_images.append(plot_image)
                plt.close()

        if not business_functions_data:
            error_message = "No records found for the provided unique code."

    return render_template('userAccount.html', error_message=error_message, plot_images=plot_images, business_data=business_functions_data)






if __name__ == '__main__':
    feedback_function()  # Run the feedback function
    app.run(debug=True)
