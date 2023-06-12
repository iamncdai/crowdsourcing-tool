from flask import Flask, request, jsonify, g
import mysql.connector
import bcrypt
import jwt
from functools import wraps
import logging
import time

secret_key = 'secret_key@18120113'
app = Flask(__name__)
app.secret_key = secret_key


def get_db():
    if 'db' not in g:
        logging.debug('Connecting to the database')
        g.db = mysql.connector.connect(
            host='db',
            user='root',
            password='18120113',
            database='crowdsourcing-tool'
        )
    return g.db


@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        logging.debug('Closing connection to the database')
        g.db.close()


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def check_username(username):
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM users WHERE username = %s"
    params = (username,)
    cursor.execute(query, params)

    user = cursor.fetchone()

    cursor.close()

    if user:
        return True
    else:
        return False


def generate_token(username):
    # 7 days = 7 * 24 * 60 * 60
    expiration_time = time.time() + (7 * 24 * 60 * 60)

    payload = {
        'username': username,
        'exp': expiration_time
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def decode_token(token):
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        expiration_time = decoded_token.get('exp')

        if expiration_time is None:
            return None

        if time.time() > expiration_time:
            return None

        return decoded_token

    except jwt.InvalidTokenError:
        return None


def authenticate_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Missing token'}), 401

        token = token.split()[1] if len(token.split()) == 2 else token

        decoded_token = decode_token(token)

        if decoded_token is None:
            return jsonify({'message': 'Invalid token'}), 401

        username = decoded_token.get("username")

        if not check_username(username):
            return jsonify({'message': 'User does not exist'}), 401

        request.decoded_token = decoded_token

        return f(*args, **kwargs)

    return decorated


@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    fullName = data['fullName']

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"SELECT * FROM users WHERE username='{username}'"
    )
    existing_user = cursor.fetchone()

    if existing_user:
        response = {
            'status': 'error',
            'message': 'Username already exists'
        }
    else:
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO users (username, password, fullName) VALUES (%s, %s, %s)",
            (username, hashed_password, fullName)
        )
        db.commit()

        response = {
            'status': 'success',
            'message': 'Registration successful',
            'token': generate_token(username)
        }

    cursor.close()

    return jsonify(response)


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"SELECT * FROM users WHERE username='{username}'"
    )
    user = cursor.fetchone()

    if user:
        hashed_password = user[2].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            token = generate_token(username)
            response = {
                'status': 'success',
                'message': 'Login successful',
                'token': token
            }
        else:
            response = {
                'status': 'error',
                'message': 'Invalid username or password'
            }
    else:
        response = {
            'status': 'error',
            'message': 'Invalid username or password'
        }

    cursor.close()

    return jsonify(response)


def get_user(username):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE username = %s"
    params = (username,)
    cursor.execute(query, params)

    user = cursor.fetchone()

    cursor.close()

    if user:
        return user
    else:
        return None


@app.route('/api/auth/me')
@authenticate_token
def protected_route():
    username = request.decoded_token.get('username')
    return jsonify({'message': 'Hi, ' + username})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
