from flask import Flask, request, render_template, redirect, session
import sqlite3
import bcrypt

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


def create_mining_sector_table():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MiningSector (
            id INTEGER PRIMARY KEY,
            BusinessSector TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

# Creating table for measuring element and rating


def create_measuring_element_and_rating_table():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MeasuringRating (
            id INTEGER PRIMARY KEY,
            MeasuringElement TEXT NOT NULL,
            Rating INTEGER,
            MiningSectorID INTEGER,
            FOREIGN KEY (MiningSectorID) REFERENCES MiningSector(id)
        )
    ''')
    connection.commit()
    connection.close()


def create_subCategory_Questions_Answers_AnswerRating_MaxRating():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subCatQstnAnsRAnsMaxR (
            id INTEGER PRIMARY KEY,
            SUbCategory TEXT NOT NULL,
            Questions TEXT NOT NULL,
            Answers TEXT NOT NULL,
            RateAnswer TEXT NOT NULL,
            MaxRating INTEGER,
            MeasuringRatingID INTEGER,
            FOREIGN KEY (MeasuringRatingID) REFERENCES MeasuringRating(id)
        )
    ''')
    connection.commit()
    connection.close()


create_user_table()
create_mining_sector_table()
create_measuring_element_and_rating_table()
create_subCategory_Questions_Answers_AnswerRating_MaxRating()


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
        print("User fetched:", user)  # Add this line for debugging

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

# Creating the business sector


@app.route('/BSector', methods=['GET', 'POST'])
def businessSector():
    if request.method == 'POST':
        business_sector_name = request.form['business_sector_name']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO MiningSector (BusinessSector)
            VALUES (?)
        ''', (business_sector_name,))
        connection.commit()
        connection.close()

        return redirect('/BSector')

    return render_template('administrator.html')

# Updating the business sector


@app.route('/UpdateBSector', methods=['GET', 'POST'])
def UpdatebusinessSector():
    if request.method == 'POST':
        business_sector_name = request.form['business_sector_name']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE MiningSector SET BusinessSector = ? WHERE id = 1
        ''', (business_sector_name,))
        connection.commit()
        connection.close()

        return redirect('/administrator')

    return render_template('administrator.html')


# creating measuring element and rating
@app.route('/MeasuringElementandRating', methods=['GET', 'POST'])
def MeasureElementRating():
    message = None
    message_display = False  # Initialize message_display
    if request.method == 'POST':
        measuring_element_name = request.form['Measuring_Element']
        rating = request.form['Rating']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO MeasuringRating (Measuring, Rating)
            VALUES (?,?)
        ''', (measuring_element_name, rating))

        connection.commit()
        connection.close()

        message = "Successfully Created Measuring Element and its Rating"
        message_display = True  # Set message_display to True after the form submission

    return render_template('administrator.html', message=message, message_display=message_display)


# updating measuring element and its rating
# updating measuring element and its rating
@app.route('/UpdateMeasuringElementandRating', methods=['POST'])
def UpdateMeasureElementRating():
    if request.method == 'POST':
        old_measuring_element = request.form['old_measuring_element']
        old_rating = request.form['old_rating']
        new_measuring_element = request.form['new_measuring_element']
        new_rating = request.form['new_rating']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE MeasuringRating 
            SET Measuring = ?, Rating = ? 
            WHERE Measuring = ? AND Rating = ?
        ''', (new_measuring_element, new_rating, old_measuring_element, old_rating))

        connection.commit()
        connection.close()

    return redirect('/administrator')

# to be used in the datalist

# @app.route('/Update_Measuring_Element')
# def update_measuring_element():
#     connection = sqlite3.connect('database.db')
#     cursor = connection.cursor()
#     cursor.execute('SELECT Measuring, Rating FROM MeasuringRating')
#     data = cursor.fetchall()
#     connection.close()
#     return render_template('administrator.html', data=data)

# Creating the combined 4 tiers


@app.route('/CombinedTiers', methods=['GET', 'POST'])
def SubCatQSTNAnsAnsRMaxR():
    if request.method == 'POST':
        subCategory_name = request.form['subCategory_name']
        SubCategoryQuestion = request.form['SubCategoryQuestion']
        QuestionAnswer = request.form['QuestionAnswer']
        AnswerRating = request.form['AnswerRating']
        MaxRating = request.form['MaxRating']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO subCatQstnAnsRAnsMaxR (SUbCategory,Questions,Answers,RateAnswer,MaxRating)
            VALUES (?,?,?,?,?)
        ''', (subCategory_name, SubCategoryQuestion, QuestionAnswer, AnswerRating, MaxRating))
        connection.commit()
        connection.close()

        return redirect('/CombinedTiers')

    return render_template('administrator.html')

# Updating the combined 4 tiers


@app.route('/UpdateCombinedTiers', methods=['GET', 'POST'])
def UpdateSubCatQSTNAnsAnsRMaxR():
    if request.method == 'POST':
        oldsubCategory_name = request.form['oldsubCategory_name']
        oldSubCategoryQuestion = request.form['oldSubCategoryQuestion']
        oldQuestionAnswer = request.form['oldQuestionAnswer']
        oldAnswerRating = request.form['oldAnswerRating']
        oldMaxRating = request.form['oldMaxRating']

        newsubCategory_name = request.form['newsubCategory_name']
        newSubCategoryQuestion = request.form['newSubCategoryQuestion']
        newQuestionAnswer = request.form['newQuestionAnswer']
        newAnswerRating = request.form['newAnswerRating']
        newMaxRating = request.form['newMaxRating']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
    UPDATE subCatQstnAnsRAnsMaxR 
    SET  SUbCategory=?, Questions=?, Answers=?, RateAnswer=?, MaxRating=?
    WHERE SUbCategory=? AND Questions=? AND Answers=? AND RateAnswer=? AND MaxRating=?
''', (newsubCategory_name, newSubCategoryQuestion, newQuestionAnswer, newAnswerRating, newMaxRating, oldsubCategory_name, oldSubCategoryQuestion, oldQuestionAnswer, oldAnswerRating, oldMaxRating))

        connection.commit()
        connection.close()

    return redirect('/administrator')

# Selecting the records from the database


@app.route('/combinedDataForSector', methods=['GET'])
def get_data():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Execute the SQL query
    cursor.execute('''
        SELECT 
            MiningSector.BusinessSector, 
            MeasuringRating.MeasuringElement, 
            MeasuringRating.Rating, 
            subCatQstnAnsRAnsMaxR.SUbCategory, 
            subCatQstnAnsRAnsMaxR.Questions, 
            subCatQstnAnsRAnsMaxR.Answers, 
            subCatQstnAnsRAnsMaxR.RateAnswer, 
            subCatQstnAnsRAnsMaxR.MaxRating 
        FROM 
            MiningSector
        JOIN 
            MeasuringRating ON MiningSector.id = MeasuringRating.MiningSectorID
        JOIN 
            subCatQstnAnsRAnsMaxR ON MeasuringRating.id = subCatQstnAnsRAnsMaxR.MeasuringRatingID
    ''')

    # Fetch all rows
    data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return render_template('administrator.html', data=data)



if __name__ == '__main__':
    app.run(debug=True)
