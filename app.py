from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3
import bcrypt
import random
import string
import base64
import csv

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
            UserName TEXT,
            MeasuringEltUser TEXT,
            RatingUser INTEGER,
            SUbCategoryUser TEXT,
            QuestionsUser TEXT,
            AnswersUser TEXT,
            UniqueCodeForUser TEXT,
            MaxRatingUser INTEGER DEFAULT 5
        )
    ''')
    connection.commit()
    connection.close()


create_user_table()
create_combined_table()
create_user_submission_record_table()


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
            INSERT INTO CombinedTable (BusinessSector,MeasuringElt,Rating,SUbCategory,Questions,Answers,RateAnswer,MaxRating)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (business_sector_name, measuring_element_name, rating, subCategory_name, SubCategoryQuestion, QuestionAnswer, AnswerRating, MaxRating))
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
        oldmeasuring_element_name = request.form['oldMeasuring_Element']
        oldrating = request.form['oldRating']
        oldsubCategory_name = request.form['oldsubCategory_name']
        oldSubCategoryQuestion = request.form['oldSubCategoryQuestion']
        oldQuestionAnswer = request.form['oldQuestionAnswer']
        oldAnswerRating = request.form['oldAnswerRating']
        oldMaxRating = request.form['oldMaxRating']

        # Extract new values from the form
        newbusiness_sector_name = request.form['newbusiness_sector_name']
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
            SET  BusinessSector=?, MeasuringElt=?, Rating=?, SUbCategory=?, Questions=?, Answers=?, RateAnswer=?, MaxRating=?
            WHERE BusinessSector=? AND MeasuringElt=? AND Rating=? AND SUbCategory=? AND Questions=? AND Answers=? AND RateAnswer=? AND MaxRating=?
        ''', (newbusiness_sector_name, newmeasuring_element_name, newrating, newsubCategory_name, newSubCategoryQuestion,
              newQuestionAnswer, newAnswerRating, newMaxRating, oldbusiness_sector_name, oldmeasuring_element_name,
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
        SELECT id, BusinessSector, MeasuringElt, Rating, SUbCategory, Questions, Answers, RateAnswer, MaxRating
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
    return render_template('upload.html')

# Process uploaded CSV file and insert into database


def process_csv(csv_file):
    connection = sqlite3.connect('database.db')
    print("Connection established successfully for csv")  # Debugging
    cursor = connection.cursor()

    # Convert file object to text mode
    csv_text = csv_file.stream.read().decode("utf-8")
    csv_data = csv.reader(csv_text.splitlines())

    next(csv_data)  # Skip header row if present
    for row in csv_data:
        cursor.execute('''
            INSERT INTO CombinedTable (id, BusinessSector, MeasuringElt, Rating, SUbCategory, Questions, Answers, RateAnswer, MaxRating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', row)

    connection.commit()
    connection.close()

# Define a function to generate random 12-letter words
def generate_random_text():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(24))


@app.route('/select_business_sector_user', methods=['GET', 'POST'])
def select_business_sector():
    # Corrected this line
    selected_sector = request.form['business_sector_user']
    if selected_sector:
        # Fetch data from CombinedTable based on selected business sector
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(
            "SELECT MeasuringElt, Rating, SubCategory, Questions FROM CombinedTable WHERE BusinessSector=?", (selected_sector,))
        sector_data = cursor.fetchall()
        connection.close()

                    # Generate random text
        random_text = generate_random_text()
        return render_template('userAccount.html', data=sector_data,random_text=random_text)
    else:
        # Redirect back to administrator page
        return redirect('/userSubmissionDataIntoTable')
    



@app.route('/userSubmissionDataIntoTable', methods=['GET', 'POST'])
def CombinedTiersForUser():
    if request.method == 'POST':
        submissionUserName = request.form['userSubmissionName']
        measuring_element_name_user = request.form.getlist('Measuring_element_user[]')
        Rating_User_MElt= request.form.getlist('Rting_User[]')
        subCategory_name_user = request.form.getlist('sub_category_for_user[]')
        SubCategoryQuestion_user = request.form.getlist('questions_user[]')
        QuestionAnswer_user = request.form.getlist('UserAnswerRating[]')

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        for i in range(len(measuring_element_name_user)):
            cursor.execute('''
                INSERT INTO UserSubmissionRecord (UserName, MeasuringEltUser, RatingUser, SUbCategoryUser, QuestionsUser, AnswersUser, MaxRatingUser)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (submissionUserName, measuring_element_name_user[i], Rating_User_MElt[i], subCategory_name_user[i], SubCategoryQuestion_user[i], QuestionAnswer_user[i], 5))

        connection.commit()
        connection.close()

        return redirect('/userSubmissionDataIntoTable')

    return render_template('userAccount.html')






if __name__ == '__main__':
    app.run(debug=True)
