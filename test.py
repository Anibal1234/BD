import flask 
import psycopg2
import logging

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}


def db_connection():
    db = psycopg2.connect(
        user='aulaspl',
        password='aulaspl',
        host='localhost',
        port='5432',
        database='projetoBD2023'
    )

    return db


@app.route('/')
def landing_page():
    return 'Hello, Flask!'


@app.route('/label',methods=['GET'])
def get_artists():
    logger.info('GET /label')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT label_id, nome FROM label')
        rows = cur.fetchall()

        logger.debug('GET /label - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'label_id': int(row[0]), 'nome': row[1]}
            Results.append(content)
        
        
        response = {'status' : StatusCodes['success'], 'results' : Results}

  #formatted_response = {
    #'status': response['status'],
   # 'results': response['results'][0] if response['results'] else None
#}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /label - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    
    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/addsong',methods = ['POST'])
def add_song():
    logger.info('POST /addsong')
    payload = flask.request.get_json()

    conn= db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /addsong - payload: {payload}')

    if 'ismn' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'ismn value not in payload'}
        return flask.jsonify(response)
    
    statement = 'INSERT INTO song VALUES(%s, %s, %s, %s, %s, %s)'
    values = (payload['ismn'], payload['genre'], payload['title'], payload['release_date'], payload['duration'], payload['artist_app_users_id'])

    try:
        cur.execute(statement, values)

        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted dep {payload["ismn"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /addsong - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

@app.route('/consumer/', methods=['POST'])
def add_consumer():
    logger.info('POST /consumer')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /consumer - payload: {payload}')

    # validate every argument, e.g.,:
    required_fields = ['premium', 'app_users_id', 'app_users_first_name', 
                       'app_users_last_name', 'app_users_email', 'app_users_username', 'app_users_password', 
                       'app_users_address', 'app_users_gender']
    for field in required_fields:
        if field not in payload:
            response = {'status': StatusCodes['api_error'], 'results': f'{field} value not in payload'}
            return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = '''INSERT INTO consumer (premium, app_users_id, app_users_first_name, 
                                         app_users_last_name, app_users_email, app_users_username, app_users_password, 
                                         app_users_address, app_users_gender)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    values = (payload['premium'], payload['app_users_id'],  payload['app_users_first_name'], payload['app_users_last_name'], payload['app_users_email'], 
              payload['app_users_username'], payload['app_users_password'], payload['app_users_address'], 
              payload['app_users_gender'])

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted consumer {payload["app_users_id"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /consumer - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

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