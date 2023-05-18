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
        host='127.0.0.1',
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