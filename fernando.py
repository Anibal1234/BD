###################
##    Base de Dados
##     2022/2023
###################

import flask 
import psycopg2
import logging
from datetime import datetime,timedelta
import jwt

app = flask.Flask(__name__)

app.config['SECRET_KEY']= 'JustDemonstrating'

#########
## STATUS
#########
StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

@app.route('/')
def landing_page():
    return 'Hello, Flask!'

############
##  REGISTER
############

@app.route('/user/reg', methods=['POST'])
def register():

    logger = logging.getLogger('logger')
    logger.info('POST /user')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /user - payload: {payload}')

    # Validate every argument
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'address', 'gender']
    for field in required_fields:
        if field not in payload:
            response = {'status': StatusCodes['api_error'], 'results': f'{field} value not in payload'}
            return flask.jsonify(response)

    premium = False

    try:
        # Retrieve the maximum app_users_id from the consumer table
        cur.execute('SELECT MAX(app_users_id) FROM consumer')
        max_app_users_id = cur.fetchone()[0]
        if max_app_users_id is None:
            app_users_id = 0
        else:
            app_users_id = max_app_users_id + 1

        statement = '''INSERT INTO consumer (premium, app_users_id, app_users_first_name, app_users_last_name,
                                             app_users_email, app_users_username, app_users_password,
                                             app_users_address, app_users_gender)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''

        values = (premium, app_users_id, payload['first_name'], payload['last_name'], payload['email'],
                  payload['username'], payload['password'], payload['address'], payload['gender'])

        cur.execute(statement, values)

        # Commit the transaction
        conn.commit()

        response = {'status': StatusCodes['success'], 'results': app_users_id}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # An error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

#########
##  LOGIN
#########

@app.route('/user/login', methods=['POST'])
def login():
    logger = logging.getLogger('logger')
    logger.info("/POST/user")

    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if "username" not in payload:
        result = {"error": "Missing Username"}
        return flask.jsonify(result)
    if "password" not in payload:
        result = {"error": "Missing password"}
        return flask.jsonify(result)

    logger.info(f'content: {payload}')

    username = payload["username"]
    password = payload["password"]

    try:
        # Check if the username and password exist in the consumer table
        cur.execute(
            "SELECT COUNT(*) FROM consumer WHERE (app_users_username = %s AND app_users_password = %s)",
            (username, password,))
        rows = cur.fetchall()
        if rows[0][0] > 0:
            conn.commit()
            token = jwt.encode({'user': username, 'exp': datetime.utcnow() + timedelta(seconds=3000)},
                               app.config['SECRET_KEY'])
            result = {"authToken": token}
            return flask.jsonify(result)

        # Check if the username and password exist in the administrator table
        cur.execute(
            "SELECT COUNT(*) FROM administrator WHERE (app_users_username = %s AND app_users_password = %s)",
            (username, password,))
        rows = cur.fetchall()
        if rows[0][0] > 0:
            conn.commit()
            token = jwt.encode({'user': username, 'exp': datetime.utcnow() + timedelta(seconds=3000)},
                               app.config['SECRET_KEY'])
            result = {"authToken": token}
            return flask.jsonify(result)

        # Check if the username and password exist in the artist table
        cur.execute(
            "SELECT COUNT(*) FROM artist WHERE (app_users_username = %s AND app_users_password = %s)",
            (username, password,))
        rows = cur.fetchall()
        if rows[0][0] > 0:
            conn.commit()
            token = jwt.encode({'user': username, 'exp': datetime.utcnow() + timedelta(seconds=3000)},
                               app.config['SECRET_KEY'])
            result = {"authToken": token}
            return flask.jsonify(result)

        # If none of the tables contain a matching user, return an error response
        result = {"error": "AuthError"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {"error": str(error)}

    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(result)


########################
##   DATABASE CONNECTION
########################

def db_connection():
    db = psycopg2.connect(
        user='postgres',
        password='password',
        host='localhost',
        port='5432',
        database='projetoBD2023'
    )

    return db
#########
##   MAIN
#########

if __name__ == '__main__':
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 5000
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')
    #app.run()