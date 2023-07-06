import logging
import os
import time
from functools import wraps

import bcrypt
import jwt
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from User import User

load_dotenv()

secret_key = os.getenv('SECRET_KEY')
app = Flask(__name__)
app.secret_key = secret_key


def get_db():
    if 'db' not in g:
        logging.debug('Connecting to the database')
        g.db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
    return g.db


@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        logging.debug('Closing connection to the database')
        g.db.close()


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM NguoiDung WHERE idUser = %s"
    params = (user_id,)
    cursor.execute(query, params)

    user_data = cursor.fetchone()

    cursor.close()

    if user_data:
        user = User(*user_data).to_dict()
        return user
    else:
        return None


def generate_token(user_id):
    # 7 days = 7 * 24 * 60 * 60
    expiration_time = time.time() + (7 * 24 * 60 * 60)

    payload = {
        'user_id': user_id,
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

        user_id = decoded_token.get("user_id")
        user = get_user_by_id(user_id)

        if user is None:
            return jsonify({'message': 'User does not exist'}), 401

        request.decoded_token = decoded_token
        request.user = user

        return f(*args, **kwargs)

    return decorated


@app.route('/auth-service', methods=['GET'])
def home():
    return jsonify({'message': 'Auth Service is Working!'})


@app.route('/auth-service/generate-password', methods=['POST'])
def api_register():
    data = request.get_json()
    password = data['Password']
    hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

    response = {
        'hashed_password': hashed_password.decode('utf-8'),
    }

    return jsonify(response)


@app.route('/auth-service/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data['UserName']
    password = data['Password']

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"SELECT * FROM NguoiDung WHERE UserName='{username}'"
    )
    user = cursor.fetchone()

    if user:
        hashed_password = user[2].encode('utf-8')
        user_id = user[0]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            token = generate_token(user_id)
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


@app.route('/auth-service/me')
@authenticate_token
def protected_route():
    user = request.user
    return jsonify(user)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)
