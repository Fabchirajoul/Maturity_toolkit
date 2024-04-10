from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3
import bcrypt
import random
import string
import math
from flask import jsonify
import matplotlib.pyplot as plt
import base64
import csv
import io
import numpy as np

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
            Questions TEXT,
            Answers TEXT,
            RateAnswer INTEGER,
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
            QuestionsUser TEXT,
            AnswersUserAsIs TEXT,
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
        CREATE TABLE IF NOT EXISTS UserSubmittedFeddback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            UniqueCodeUser TEXT,
            name TEXT,
            BusinessFunction TEXT, 
            MeasuringEltUser TEXT,
            RatingUser INTEGER,
            SUbCategoryUser TEXT,
            QuestionsUser TEXT,
            AnswersUserAsIs TEXT,
            AnswersUserToBe TEXT,   
            MaxRatingUser INTEGER DEFAULT 5,
            ExpectedCumSum INTEGER,
            UserCumSumAsIs INTEGER,
            UserCumSumToBe INTEGER,
            OtherCompanies INTEGER,
            MaturityAsIs INTEGER,
            PercentMaturityAsIs INTEGER,
            MaturityToBe INTEGER,
            PercentMaturityToBe INTEGER,
            GrowthRate INTEGER
            Duration INTEGER
            FeedbackAsIs TEXT,
            FeedbackTobe TEXT 
            
        )
    ''')
    connection.commit()
    connection.close()


def create_affinity_relationship_table():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserSubmissionAffinity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            UniqueCodeUser TEXT,
            BusinessFunction TEXT,  
            MeasuringEltUser TEXT,
            FOREIGN KEY (UniqueCodeUser) REFERENCES UserSubmissionRecord(UniqueCodeUser)
        )
    ''')
    connection.commit()
    connection.close()

create_affinity_relationship_table()


create_user_table()
create_combined_table()
create_user_submission_record_table()
create_final_feedback_data()
create_affinity_relationship_table()


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
        SubCategoryQuestion = request.form['SubCategoryQuestion']
        QuestionAnswer = request.form['QuestionAnswer']
        AnswerRating = request.form['AnswerRating']
        MaxRating = request.form['MaxRating']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO CombinedTable (BusinessSector,BusinessFunction,MeasuringElt,Rating,SUbCategory,Questions,Answers,RateAnswer,MaxRating)
            VALUES (?,?,?,?,?,?,?,?,?)
        ''', (business_sector_name, business_function_name, measuring_element_name, rating, subCategory_name, SubCategoryQuestion, QuestionAnswer, AnswerRating, MaxRating))
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
        oldSubCategoryQuestion = request.form['oldSubCategoryQuestion']
        oldQuestionAnswer = request.form['oldQuestionAnswer']
        oldAnswerRating = request.form['oldAnswerRating']
        oldMaxRating = request.form['oldMaxRating']

        # Extract new values from the form
        newbusiness_sector_name = request.form['newbusiness_sector_name']
        newbusiness_function = request.form['newbusiness_function']
        newmeasuring_element_name = request.form['newMeasuring_Element']
        newrating = request.form['newRating']  # Corrected parameter name
        newsubCategory_name = request.form['newsubCategory_name']
        newSubCategoryQuestion = request.form['newSubCategoryQuestion']
        newQuestionAnswer = request.form['newQuestionAnswer']
        newAnswerRating = request.form['newAnswerRating']
        newMaxRating = request.form['newMaxRating']

        # Connect to the database
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        # Execute the SQL update query
        cursor.execute('''
            UPDATE CombinedTable 
            SET  BusinessSector=?, BusinessFunction=?, MeasuringElt=?, Rating=?, SUbCategory=?, Questions=?, Answers=?, RateAnswer=?, MaxRating=?
            WHERE BusinessSector=? AND BusinessFunction=? AND MeasuringElt=? AND Rating=? AND SUbCategory=? AND Questions=? AND Answers=? AND RateAnswer=? AND MaxRating=?
        ''', (newbusiness_sector_name, newbusiness_function, newmeasuring_element_name, newrating, newsubCategory_name, newSubCategoryQuestion,
              newQuestionAnswer, newAnswerRating, newMaxRating, oldbusiness_sector_name, oldbusiness_function, oldmeasuring_element_name,
              oldrating, oldsubCategory_name, oldSubCategoryQuestion, oldQuestionAnswer, oldAnswerRating, oldMaxRating))

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
        SELECT id, BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, Questions, Answers, RateAnswer, MaxRating
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
    return render_template('admininstrator.html')

# Process uploaded CSV file and insert into database


def process_csv(csv_file):
    connection = sqlite3.connect('database.db')

    cursor = connection.cursor()

    # Convert file object to text mode
    csv_text = csv_file.stream.read().decode("utf-8")
    csv_data = csv.reader(csv_text.splitlines())

    next(csv_data)  # Skip header row if present
    for row in csv_data:
        cursor.execute('''
            INSERT INTO CombinedTable (id, BusinessSector, BusinessFunction, MeasuringElt, Rating, SUbCategory, Questions, Answers, RateAnswer, MaxRating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', row)

    connection.commit()
    connection.close()


# Define a function to generate random 12-letter words


def generate_random_text():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(24))


@app.route('/select_business_sector_user', methods=['GET', 'POST'])
def select_business_sector():
    erro_message_user_business_sector = None

    if request.method == 'POST':
        # Check if 'business_sector_user' exists in the form data
        if 'business_sector_user' in request.form:
            selected_sector = request.form['business_sector_user']

            if selected_sector:
                # Fetch data from CombinedTable based on selected business sector
                connection = sqlite3.connect('database.db')
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT BusinessFunction, MeasuringElt, Rating, SubCategory, Questions FROM CombinedTable WHERE BusinessSector=?", (selected_sector,))
                sector_data = cursor.fetchall()
                connection.close()

                # Generate random text
                random_text = generate_random_text()
                return render_template('userAccount.html', data=sector_data, random_text=random_text, BusinessError=erro_message_user_business_sector)
            else:
                # Handle case when no sector is selected
                erro_message_user_business_sector = "Please select a business sector"
        else:
            # Handle case when 'business_sector_user' is not in form data
            erro_message_user_business_sector = "Invalid request. Please try again after selecting a business sector."

    # Redirect back to administrator page or display error message
    return render_template('userAccount.html', BusinessError=erro_message_user_business_sector)


@app.route('/userSubmissionDataIntoTable', methods=['GET', 'POST'])
def CombinedTiersForUser():
    error_display_asistobe = None  # Initialize error_display_asistobe

    if request.method == 'POST':
        UserSubmittedUniqueCode = request.form['Unique_code_from_User']
        business_function_name_user = request.form.getlist('business_function_user[]')
        measuring_element_name_user = request.form.getlist('Measuring_element_user[]')
        Rating_User_MElt = request.form.getlist('Rting_User[]')
        subCategory_name_user = request.form.getlist('sub_category_for_user[]')
        SubCategoryQuestion_user = request.form.getlist('questions_user[]')
        QuestionAnswer_user = request.form.getlist('UserAnswerRating[]')
        QuestionAnswer_userToBe = request.form.getlist('UserAnswerRatingToBe[]')

        if not QuestionAnswer_user or not QuestionAnswer_userToBe:
            error_display_asistobe = "An error occurred. Please make sure to select an answer for every question before submitting your answers."
            print("First Error message:", error_display_asistobe)
        else:
            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()

            for i in range(len(measuring_element_name_user)):
                Rting_User = float(Rating_User_MElt[i])
                UserAnswerRatingAsIs = float(QuestionAnswer_user[i])
                UserAnswerRatingToBe = float(QuestionAnswer_userToBe[i])
                MaxRatingUser = 5

                ExpectedCumSum = Rting_User * MaxRatingUser
                UserCumSumAsIs = Rting_User * UserAnswerRatingAsIs
                UserCumSumToBe = Rting_User * UserAnswerRatingToBe

                cursor.execute('''
                        INSERT INTO UserSubmissionRecord (UniqueCodeUser, BusinessFunction, MeasuringEltUser, RatingUser, SUbCategoryUser, QuestionsUser, AnswersUserAsIs, AnswersUserToBe, MaxRatingUser, ExpectedCumSum, UserCumSumAsIs, UserCumSumToBe)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (UserSubmittedUniqueCode, business_function_name_user[i], measuring_element_name_user[i], Rting_User, subCategory_name_user[i], SubCategoryQuestion_user[i], QuestionAnswer_user[i], QuestionAnswer_userToBe[i], MaxRatingUser, ExpectedCumSum, UserCumSumAsIs, UserCumSumToBe))

                cursor.execute('''
                        INSERT INTO UserSubmissionAffinity (UniqueCodeUser, BusinessFunction, MeasuringEltUser)
                        VALUES (?, ?, ?)
                    ''', (UserSubmittedUniqueCode, business_function_name_user[i], measuring_element_name_user[i]))

            connection.commit()
            connection.close()

            return redirect('/userSubmissionDataIntoTable')

    return render_template('userAccount.html', error_display_asistobe=error_display_asistobe)




@app.route('/submit_code', methods=['POST'])
def submit_code():
    error_message = None  # Initialize error message


    # Function to fetch data from UserSubmissionAffinity table
    def fetch_user_submission_affinities_data(unique_code):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT BusinessFunction, MeasuringEltUser FROM UserSubmissionAffinity WHERE UniqueCodeUser = ?", (unique_code,))
        user_submission_affinities = cursor.fetchall()
        connection.close()

        print(user_submission_affinities)
        return user_submission_affinities

    if request.method == 'POST':
        unique_code = request.form['unique_code_user']

        # Check if the unique code exists in the UserSubmissionRecord table
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT MeasuringEltUser, SUM(ExpectedCumSum), SUM(UserCumSumAsIs), SUM(UserCumSumToBe), BusinessFunction
            FROM UserSubmissionRecord 
            WHERE UniqueCodeUser = ?
            GROUP BY MeasuringEltUser
        ''', (unique_code,))
        user_records = cursor.fetchall()

        connection.close()

        if not unique_code:
            error_message = "Please go back and insert your unique code number"

        # Extract data for plotting
        measuring_elt_user = [record[0] for record in user_records]
        sum_expected_cum_sum = [record[1] for record in user_records]
        sum_user_cum_sum = [record[2] for record in user_records]
        sum_user_cum_sum_t0_be = [record[3] for record in user_records]
        # business_function = [record[4] for record in user_records]

        # Calculate percentage values
        percentage_values = [round((new / old) * 100, 2) if old != 0 else 0
                             for new, old in zip(sum_user_cum_sum, sum_expected_cum_sum)]

        # Calculate percentage values for sum_user_cum_sum_to_be
        percentage_values_to_be = [round((user_cum_sum_to_be / expected_cum_sum) * 100, 2) if expected_cum_sum != 0 else 0
                                   for user_cum_sum_to_be, expected_cum_sum in zip(sum_user_cum_sum_t0_be,
                                                                                   sum_expected_cum_sum)]

        # Growth rate calculation
        percentage_growth_rate = [round(((new_value - old_value) / old_value) * 100, 2) if old_value != 0 else 0
                                  for old_value, new_value in zip(sum_user_cum_sum_t0_be, sum_expected_cum_sum)]

        # Calculate the duration in years
        duration_years = [round(math.log(new_value / old_value) / math.log(1 + percentage_growth_rate / 100), 4)
                          if percentage_growth_rate != 0 else 0
                          for old_value, new_value, percentage_growth_rate in
                          zip(sum_user_cum_sum_t0_be, sum_expected_cum_sum, percentage_growth_rate)]

        # Check percentage_values range and assign feedback messages accordingly
        feedback_messages = {}

        for i in range(len(user_records)):
            feedback_As_Is = None
            feedback_To_Be = None
            percentage_value = percentage_values[i]
            percentage_value_to_be = percentage_values_to_be[i]

            # Determine feedback for percentage_values
            if 0 <= percentage_value <= 15:
                feedback_As_Is = "Stage 0:, Level: Incomplete, Aspect practices are yet to be implemented or incomplete, Organisation only performs essential operations."
            elif 16 <= percentage_value <= 34:
                feedback_As_Is = "Stage 1, Level Performed, Aspect practices are fully implemented. Transition to Industry 4.0 has commenced"
            elif 34 <= percentage_value <= 50:
                feedback_As_Is = "Stage 2, level Managed, Initial implementation of Industry 4.0 technologies.No integration yet.Physical systems can be represented virtually"
            elif 51 <= percentage_value <= 67:
                feedback_As_Is = "Stage 3: Level: Established, Vertical integration from shop floor to ERP level, Standardisation of processes and operations"
            elif 68 <= percentage_value <= 84:
                feedback_As_Is = "Stage 4: Level: Predictable, Horizontal integration across the value chain.Application of Industry 4.0 technologies such Big Data and artificial intelligence.autonomous optimisation"
            elif 85 <= percentage_value <= 100:
                feedback_As_Is = "Stage 5: Level: Optimizing, End-to-end integration.Continuous improvement.Smart and autonomous optimisation."

            # Determine feedback for percentage_values_to_be
            if 0 <= percentage_value_to_be <= 16:
                feedback_To_Be = "Stage 0:\nLevel: Incomplete\nAspect practices are yet to be implemented or incomplete\nOrganisation only performs essential operations."
            elif 17 <= percentage_value_to_be <= 33:
                feedback_To_Be = "Stage 1:\nLevel Performed\nAspect practices are fully implemented.\nTransition to Industry 4.0 has commenced."
            elif 34 <= percentage_value_to_be <= 50:
                feedback_To_Be = "Stage 2:\nLevel Managed\nInitial implementation of Industry 4.0 technologies.\nNo integration yet.\nPhysical systems can be represented virtually."
            elif 51 <= percentage_value_to_be <= 67:
                feedback_To_Be = "Stage 3:\nLevel Established\nVertical integration from shop floor to ERP level.\nStandardisation of processes and operations."
            elif 68 <= percentage_value_to_be <= 84:
                feedback_To_Be = "Stage 4:\nLevel Predictable\nHorizontal integration across the value chain.\nApplication of Industry 4.0 technologies such Big Data and artificial intelligence.\nAutonomous optimisation."
            elif 85 <= percentage_value_to_be <= 100:
                feedback_To_Be = "Stage 5:\nLevel Optimizing\nEnd-to-end integration.\nContinuous improvement.\nSmart and autonomous optimisation."

            feedback_messages[user_records[i][0]] = (
                feedback_As_Is, feedback_To_Be)

        # Define the width of the bars
        bar_width = 0.3

        # Generate an array of indices for positioning the bars
        indices = np.arange(len(measuring_elt_user))

        # Plotting
        # Increase figure width to accommodate x-labels
        plt.figure(figsize=(12, 12))

        # Create the first subplot for the bar plot
        plt.subplot(2, 1, 1)

        # Plot the bars for "MATURITY LEVEL 'WITH OTHER COMPANIES'"
        plt.bar(indices - bar_width, sum_expected_cum_sum,
                width=bar_width, label='MATURITY LEVEL "WITH OTHER COMPANIES"')

        # Plot the bars for "MATURITY LEVEL 'AS IS'"
        plt.bar(indices, sum_user_cum_sum, width=bar_width,
                label='MATURITY LEVEL "AS IS"')

        # Plot the bars for "MATURITY LEVEL 'TO BE'"
        plt.bar(indices + bar_width, sum_user_cum_sum_t0_be,
                width=bar_width, label='MATURITY LEVEL "TO BE"')

        plt.xlabel('MEASURING ELEMENT')
        plt.ylabel('MATURITY LEVEL')
        plt.title(
            'GRAPHICAL REPRESENTATION OF MATURITY LEVEL FOR DIFFERENT MEASURING ELEMENTS OF A BUSINESS SECTOR')
        # Set x ticks to measuring elements
        plt.xticks(indices, measuring_elt_user, rotation=90)
        plt.legend()

        # Create the second subplot for the exponential growth curve
        plt.subplot(2, 1, 2)

        # Plot exponential growth curve for each measuring_elt_user
        for idx, measuring_elt in enumerate(measuring_elt_user):
            # Assume duration_years is available
            x_values = np.linspace(0, duration_years[idx], 100)
            # Convert percentage to decimal growth rate
            growth_rate = percentage_growth_rate[idx] / 100
            y_values = sum_user_cum_sum_t0_be[idx] * \
                np.exp(growth_rate * x_values)
            plt.plot(x_values, y_values, label=f'{measuring_elt} Growth Curve')

        plt.xlabel('Time (Years)')
        plt.ylabel('Value')
        plt.title('Exponential Growth Curves for Different Measuring Elements')
        plt.legend()
        plt.tight_layout()  # Adjust layout for better spacing

        # Convert plot to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()

        # Fetch user submission affinities data for the given unique code
        submission_affinities_data = fetch_user_submission_affinities_data(unique_code)

        # Render the template with the measuring elements data and their summed ExpectedCumSum
        return render_template('userAccount.html', user_records=user_records, percentages=percentage_values,
                               percenTobe=percentage_values_to_be, growth_rate=percentage_growth_rate,
                               duration=duration_years, plot=img_str, feedback_messages=feedback_messages, error_message=error_message, submission_affinities_data=submission_affinities_data)




if __name__ == '__main__':
    app.run(debug=True)
