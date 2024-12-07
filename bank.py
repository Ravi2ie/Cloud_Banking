from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import pooling
from datetime import datetime
import secrets
secret_key = secrets.token_hex(24)  # Generates a 24-byte (48-character) random string

app = Flask(__name__)
app.secret_key = secret_key  # Necessary for session management and flash messages

# MySQL database configuration
# db_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': '',
#     'database': 'cloudbank_db'
# }

db_config = {
    'host': 'cloudbankdb.c9sqqcwmk2di.ap-south-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Cloudbank123',
    'database': 'cloudbank_db'
}


# cnxpool = mysql.connector.pooling.MySQLConnectionPool(
#     pool_name="mypool",
#     pool_size=5,
#     host="cloudbankdb.c9sqqcwmk2di.ap-south-1.rds.amazonaws.com",
#     user="admin",
#     password="Cloudbank123",
#     database="cloudbank_db",
#     ssl_ca="ap-south-1-bundle.pem"  # Path to the downloaded certificate
# )

# Create MySQL connection pool
# cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",
#                                                       pool_size=5,
#                                                       **db_config)

# Helper function to get a database connection from the pool
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    return None

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get user input
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        aadhar = request.form['aadhar']
        address = request.form['address']
        pan_card = request.form['pan_card']
        account_type = request.form['account_type']  # Get account type from user input

        # Check if user already exists
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            flash("User already exists. Please log in.", 'error')
            return redirect(url_for('login'))

        # Validate phone and aadhar number
        if len(phone) != 10 or len(aadhar) != 12:
            flash("Invalid phone or Aadhar number", 'error')
            return redirect(url_for('register'))

        # Insert new user into database
        cursor.execute(""" 
            INSERT INTO users (full_name, email, password, phone, address, aadhar_number, pan_card) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, email, password, phone, address, aadhar, pan_card))
        conn.commit()

        # Get the newly created user's ID
        user_id = cursor.lastrowid

        # Insert a new account for the user with an initial balance of zero
        cursor.execute("""
            INSERT INTO accounts (user_id, account_type, balance, account_status, opened_at, full_name) 
            VALUES (%s, %s, %s, %s, NOW(), %s)
        """, (user_id, account_type, 0, 'active', username))
        conn.commit()

        # Create session for the user
        session['user'] = {'aadhar': aadhar, 'username': username, 'email': email}
        flash("Registration successful!", 'success')

        # Redirect to confirmation page
        return redirect(url_for('confirm'))

    return render_template('register.html')

@app.route('/update', methods=['GET', 'POST'])
def update():
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Retrieve user_id using the email from session
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (session['user']['email'],))
        user_data = cursor.fetchone()

        if user_data:
            user_id = user_data['user_id']

            if request.method == 'POST':
                name = request.form['name']
                email = request.form['email']
                phone = request.form['phone']
                address = request.form['address']

                try:
                    # Update user information in the users table
                    cursor.execute("""UPDATE users SET full_name = %s, email = %s, phone = %s, address = %s WHERE user_id = %s""",
                                   (name, email, phone, address, user_id))

                    # Update the full name in the accounts table
                    cursor.execute("""UPDATE accounts SET full_name = %s WHERE user_id = %s""", (name, user_id))

                    conn.commit()  # Commit the changes
                    flash('Profile updated successfully!', 'success')  # Flash success message

                except Exception as e:
                    conn.rollback()  # Rollback in case of error
                    flash('An error occurred while updating your profile. Please try again.', 'danger')

                # Instead of redirecting, render the update page with success message
                return render_template('update.html', user={'full_name': name, 'email': email, 'phone': phone, 'address': address})

            # GET request - Retrieve the user information for the form
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()

            return render_template('update.html', user=user)

        else:
            flash('User not found.', 'danger')
            return redirect(url_for('login'))

    return redirect(url_for('login'))


@app.route('/about')
def about():
    return render_template('about.html')

# Route for the Contact Us page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route for Services Offered page
@app.route('/services')
def services():
    return render_template('services.html')


# Confirm route
@app.route('/confirm')
def confirm():
    if 'user' in session:
        return render_template('confirm.html', user=session['user'])
    else:
        flash("You must be logged in to view this page.", 'error')
        return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check user credentials in the database
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            session['user'] = {'aadhar': user[6],'username': user[1], 'email': user[2]}  # Store user info in session
            flash("Login successful!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Account dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' in session and 'username' in session['user']:
        return render_template('dashboard.html', username=session['user']['username'])
    else:
        flash("You must be logged in to view this page.", 'error')
        return redirect(url_for('login'))

@app.route('/balance')
def balance():
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("user : ",session['user'])
        cursor.execute("SELECT balance FROM accounts WHERE full_name = %s", (session['user']['username'],))
        
        balance = cursor.fetchone()[0]
        return render_template('balance.html', balance=balance)
    else:
        flash("You must be logged in to view this page.", 'error')
        return redirect(url_for('login'))
    
# Transaction route
@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user' not in session:
        flash("You must be logged in to perform transactions.", 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        recipient = request.form['recipient']
        amount = float(request.form['amount'])  # Convert amount to float

        # Handle transaction in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Get the current balance of the logged-in user
            cursor.execute("SELECT account_id, balance FROM accounts WHERE full_name = %s", (session['user']['username'],))
            user_account = cursor.fetchone()

            if user_account is None:
                flash("Account not found.", 'error')
                return redirect(url_for('dashboard'))

            account_id = user_account[0]  # Get user's account ID
            current_balance = user_account[1]  # Get current balance

            # Check if there are sufficient funds for the transaction
            if current_balance < amount:
                flash("Insufficient balance to complete the transaction.", 'error')
                return redirect(url_for('transfer'))

            # Get recipient's account ID
            cursor.execute("SELECT account_id FROM accounts WHERE full_name = %s", (recipient,))
            recipient_account = cursor.fetchone()

            if recipient_account is None:
                flash("Recipient account not found.", 'error')
                return redirect(url_for('transfer'))

            recipient_account_id = recipient_account[0]  # Get recipient's account ID

            # Transaction logic: deduct from user's account, add to recipient's account
            cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, account_id))
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, recipient_account_id))

            cursor.execute("SELECT user_id FROM users WHERE email = %s", (session['user']['email'],))
            user_id = cursor.fetchone()[0]
            description = f"Transfer to {recipient}"
            # Log the transaction in the account_statements table
            cursor.execute("""
                INSERT INTO account_statements (user_id, transaction_type, transaction_amount, transaction_date, description, from_account_id, to_account_id)
                VALUES (%s, 'transfer', %s, NOW(), %s, %s, %s)
                """, (user_id, amount, description, account_id, recipient_account_id))


            conn.commit()
            flash("Transaction successful!", 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Transaction failed: {err}", 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('transfer.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user' not in session:
        flash("You must be logged in to view this page.", 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount = float(request.form['amount'])  # Convert amount to float
        password = request.form['password']

        # Check user's password
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password FROM users WHERE email = %s", (session['user']['email'],))
        user = cursor.fetchone()

        if user and user[1] == password:  # Compare entered password
            # Get the user's account ID
            cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user[0],))
            account_id = cursor.fetchone()[0]

            # Update account balance
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, account_id))

            # Log the deposit transaction in the account_statements table
            cursor.execute("""
                INSERT INTO account_statements (user_id, transaction_type, transaction_amount, transaction_date, description, from_account_id, to_account_id)
                VALUES (%s, 'deposit', %s, NOW(), 'Deposit', %s, NULL)
            """, (user[0], amount, account_id))

            conn.commit()
            flash("Deposit successful!", 'success')
        else:
            flash("Incorrect password. Deposit failed.", 'error')

        cursor.close()
        conn.close()

    return render_template('deposit.html')

@app.route('/statement')
def statement():
    if 'user' not in session:
        flash("You must be logged in to view your transaction statements.", 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Fetch results as dictionary for easier access

    try:
        # Fetch all transaction statements related to the logged-in user
        # Fetch user_id (ensure the query returned a result)
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (session['user']['email'],))
        print(session['user']['email'],session['user'])
        user_data = cursor.fetchone()
        print(user_data)
        if user_data:
            user_id = user_data["user_id"]  # Extract user_id
            print(user_id)
        else:
            print("User not found for email:", session['user']['email'])
            # Handle the case where the user is not found (e.g., return an error, raise an exception, etc.)

        
        cursor.execute("""
            SELECT transaction_type, transaction_amount, transaction_date, description, from_account_id, to_account_id
            FROM account_statements 
            WHERE user_id = %s
            ORDER BY transaction_date DESC
        """, (user_id,))

        # Fetch all the statements and store them in 'statements'
        statements = cursor.fetchall()

        if not statements:
            flash("No transaction records found.", 'info')

    except mysql.connector.Error as err:
        flash(f"Error fetching transaction statements: {err}", 'error')
        statements = []

    finally:
        cursor.close()
        conn.close()

    # Render the 'statement.html' template with the fetched transaction statements
    return render_template('statement.html', statements=statements)


# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
