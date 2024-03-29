from flask import Flask, request, render_template, redirect, session
import sqlite3
import bcrypt
import base64

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
            id INTEGER PRIMARY KEY,
            BusinessSector TEXT,
            MeasuringElt TEXT NOT NULL,
            Rating INTEGER,
            SUbCategory TEXT NOT NULL,
            Questions TEXT NOT NULL,
            Answers TEXT NOT NULL,
            RateAnswer TEXT NOT NULL,
            MaxRating INTEGER
        )
    ''')
    connection.commit()
    connection.close()


create_user_table()
create_combined_table()


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

# inserting other properties except the business sector 
@app.route('/CombinedTiersForAllWithoutBusinessSector', methods=['GET', 'POST'])
def CombinedTiersWithoutBusinessSector():
    if request.method == 'POST':
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
            INSERT INTO CombinedTable (MeasuringElt,Rating,SUbCategory,Questions,Answers,RateAnswer,MaxRating)
            VALUES (?,?,?,?,?,?,?)
        ''', (measuring_element_name, rating, subCategory_name, SubCategoryQuestion, QuestionAnswer, AnswerRating, MaxRating))
        connection.commit()
        connection.close()

        return redirect('/CombinedTiersForAll')

    return render_template('administrator.html')



# Updating the combined tiers
@app.route('/UpdateCombinedTiersForAllWithoutBusinessSector', methods=['GET', 'POST'])
def UpdateCombinedTiersWithoutBusinessSector():
    if request.method == 'POST':
        # Extract old values from the form
        # oldbusiness_sector_name = request.form['oldbusiness_sector_name']
        oldmeasuring_element_name = request.form['oldMeasuring_Element']
        oldrating = request.form['oldRating']
        oldsubCategory_name = request.form['oldsubCategory_name']
        oldSubCategoryQuestion = request.form['oldSubCategoryQuestion']
        oldQuestionAnswer = request.form['oldQuestionAnswer']
        oldAnswerRating = request.form['oldAnswerRating']
        oldMaxRating = request.form['oldMaxRating']

        # Extract new values from the form
        # newbusiness_sector_name = request.form['newbusiness_sector_name']
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
            SET  MeasuringElt=?, Rating=?, SUbCategory=?, Questions=?, Answers=?, RateAnswer=?, MaxRating=?
            WHERE MeasuringElt=? AND Rating=? AND SUbCategory=? AND Questions=? AND Answers=? AND RateAnswer=? AND MaxRating=?
        ''', (newmeasuring_element_name, newrating, newsubCategory_name, newSubCategoryQuestion,
              newQuestionAnswer, newAnswerRating, newMaxRating, oldmeasuring_element_name,
              oldrating, oldsubCategory_name, oldSubCategoryQuestion, oldQuestionAnswer, oldAnswerRating, oldMaxRating))

        # Commit changes and close connection
        connection.commit()
        connection.close()

        # Redirect back to administrator page
        return redirect('/administrator')
    
    return render_template('administrator.html')









if __name__ == '__main__':
    app.run(debug=True)
