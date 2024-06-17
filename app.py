from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__, static_url_path='/static')

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="deekshitha2602",  # Replace with your actual password
        database="banking_system"
    )

def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, current_balance FROM customers")
    customers = cursor.fetchall()
    conn.close()
    return customers

@app.route('/')
def homepage():
    return render_template('myindex.html')

@app.route('/transfer-money')
def transfer_money_page():
    return render_template('transfer.html')

@app.route('/view-customers')
def view_customers():
    customers = get_customers()
    return render_template('index.html', customers=customers)

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    from_email = data['fromEmail']
    to_email = data['toEmail']
    amount = float(data['amount'])

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT current_balance FROM customers WHERE email = %s", (from_email,))
    from_balance = cursor.fetchone()
    if from_balance is None:
        return jsonify({'message': 'Invalid email address for sender.'}), 400

    cursor.execute("SELECT current_balance FROM customers WHERE email = %s", (to_email,))
    to_balance = cursor.fetchone()
    if to_balance is None:
        return jsonify({'message': 'Invalid email address for recipient.'}), 400

    if from_balance[0] < amount:
        return jsonify({'message': 'Insufficient balance.'}), 400

    new_from_balance = from_balance[0] - amount
    new_to_balance = to_balance[0] + amount

    cursor.execute("UPDATE customers SET current_balance = %s WHERE email = %s", (new_from_balance, from_email))
    cursor.execute("UPDATE customers SET current_balance = %s WHERE email = %s", (new_to_balance, to_email))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': f'{amount} has been transferred from {from_email} to {to_email}.'})

if __name__ == '__main__':
    app.run(debug=True)
