import os
from collections import OrderedDict
from http import HTTPStatus

import psycopg2
import psycopg2.extras
import pybreaker
import requests
import sqlalchemy.pool as pool
from flask import Flask, request, send_from_directory
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from webargs import fields, validate
from webargs.flaskparser import abort, parser


#pylint: disable=unused-argument
@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    abort(HTTPStatus.BAD_REQUEST, errors=err.messages)


# Init Flask
app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


# swagger config
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "ortelius-ms-compitem-crud"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

# Init db connection
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "postgres")
db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASS", "postgres")
db_port = os.getenv("DB_PORT", "5432")
validateuser_url = os.getenv("VALIDATEUSER_URL", "http://localhost:5000")

# connection pool config
conn_pool_size = int(os.getenv("POOL_SIZE", "3"))
conn_pool_max_overflow = int(os.getenv("POOL_MAX_OVERFLOW", "2"))
conn_pool_timeout = float(os.getenv("POOL_TIMEOUT", "30.0"))
conn_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=1,
    reset_timeout=10
)


@conn_circuit_breaker
def create_conn():
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_pass, port=db_port)
    return conn


# connection pool init
mypool = pool.QueuePool(create_conn, max_overflow=conn_pool_max_overflow, pool_size=conn_pool_size, timeout=conn_pool_timeout)

# health check endpoint


class HealthCheck(Resource):
    def get(self):
        try:
            conn = mypool.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            conn.close()
            if cursor.rowcount > 0:
                return ({"status": 'UP', "service_name": 'ortelius-ms-dep-pkg-cud'}), HTTPStatus.OK
            return ({"status": 'DOWN'}), HTTPStatus.SERVICE_UNAVAILABLE

        except Exception as err:
            print(err)
            return ({"status": 'DOWN'}), HTTPStatus.SERVICE_UNAVAILABLE


api.add_resource(HealthCheck, '/health')
# end health check


class CompItem(Resource):

    def get(self):

        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            return None, HTTPStatus.UNAUTHORIZED

        if (result.status_code != HTTPStatus.OK):
            return result.json(), HTTPStatus.UNAUTHORIZED

        query_args_validations = {
            "compitemid": fields.Int(required=True, validate=validate.Range(min=1))
        }

        parser.parse(query_args_validations, request, location="query")

        try:
            compitemid = request.args.get('compitemid', "-1")
            conn = mypool.connect()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            sql = """select compid, id, name, rollup, rollback, repositoryid, target, xpos, ypos,
                     kind, buildid, buildurl, chart, operator, builddate, dockersha, gitcommit,
                     gitrepo, gittag, giturl, chartversion, chartnamespace, dockertag, chartrepo,
                     chartrepourl, serviceowner, serviceowneremail, serviceownerphone, 
                     slackchannel, discordchannel, hipchatchannel, pagerdutyurl, pagerdutybusinessurl
                     from dm.dm_componentitem where id = %s"""

            params = (compitemid,)
            cursor.execute(sql, params)
            result = cursor.fetchall()
            if (not result):
                result = [OrderedDict([('compid', -1), ('id', compitemid), ('name', None), ('rollup', None), ('rollback', None), ('repositoryid', None),
                                       ('target', None), ('xpos', None), ('ypos', None),  ('kind', None), ('buildid', None), ('buildurl', None),
                                       ('chart', None), ('operator', None), ('builddate', None), ('dockersha', None), ('gitcommit', None),
                                       ('gitrepo', None), ('gittag', None), ('giturl', None), ('chartversion', None), ('chartnamespace', None), ('dockertag', None), ('chartrepo', None),
                                       ('chartrepourl', None), ('serviceowner', None), ('serviceowneremail', None), ('serviceownerphone', None),
                                       ('slackchannel', None), ('discordchannel', None), ('hipchatchannel', None), ('pagerdutyurl', None), ('pagerdutybusinessurl', None)])]
            cursor.close()
            conn.close()
            return result
        except Exception as err:
            print(err)
            conn.rollback()
            return ({"message": str(err)}), HTTPStatus.INTERNAL_SERVER_ERROR

# Not implemented fully.  SQL query is not complete
    def post(self):

        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            return None, HTTPStatus.UNAUTHORIZED

        if (result.status_code != HTTPStatus.OK):
            return result.json(), HTTPStatus.UNAUTHORIZED

        try:
            data = request.get_json()
            data_list = []
            for col in data:
                row = (col['id'], col['compid'], col['status'], col['buildid'], col['buildurl'], col['dockersha'], col['dockertag'], col['gitcommit'], col['gitrepo'], col['giturl'])  # this will be changed
                data_list.append(row)

            conn = mypool.connect()
            cursor = conn.cursor()
            # execute the INSERT statement
            records_list_template = ','.join(['%s'] * len(data_list))
            sql = 'INSERT INTO dm.dm_componentitem(id, compid, status, buildid, buildurl, dockersha, dockertag, gitcommit, gitrepo, giturl) \
                VALUES {}'.format(records_list_template)
            cursor.execute(sql, data_list)
            # commit the changes to the database
            rows_inserted = cursor.rowcount
            # Commit the changes to the database
            conn.commit()
            conn.close()
            if rows_inserted > 0:
                return ({"message": 'components updated succesfully'}), HTTPStatus.CREATED

            return ({"message": 'components not updated'}), HTTPStatus.OK

        except Exception as err:
            print(err)
            conn.rollback()
            return ({"message": str(err)}), HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self):

        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            return None, HTTPStatus.UNAUTHORIZED

        if (result.status_code != HTTPStatus.OK):
            return result.json(), HTTPStatus.UNAUTHORIZED

        query_args_validations = {
            "compid": fields.Int(required=True, validate=validate.Range(min=1))
        }

        parser.parse(query_args_validations, request, location="query")

        try:
            compid = request.args.get('compid', "-1")
            conn = create_conn()
            cursor = conn.cursor()

            sql1 = "DELETE from dm.dm_compitemprops where compitemid in (select id from dm.dm_componentitem where compid = " + str(compid) + ")"
            sql2 = "DELETE from dm.dm_componentitem where compid=" + compid
            rows_deleted = 0
            cursor.execute(sql1)
            cursor.execute(sql2)
            rows_deleted = cursor.rowcount
            # Commit the changes to the database
            conn.commit()
            if rows_deleted > 0:
                return ({"message": 'components updated succesfully'}), HTTPStatus.OK

            return ({"message": 'components not updated'}), HTTPStatus.OK

        except Exception as err:
            print(err)
            conn.rollback()
            return ({"message": str(err)}), HTTPStatus.INTERNAL_SERVER_ERROR

# Not implemented fully.  SQL query is not complete
    def put(self):  # not completed

        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            return None, HTTPStatus.UNAUTHORIZED

        if (result.status_code != HTTPStatus.OK):
            return result.json(), HTTPStatus.UNAUTHORIZED

        try:
            conn = mypool.connect()
            cursor = conn.cursor()

            data = request.get_json()
            data_list = []
            for col in data:
                row = (col['id'], col['compid'], col['status'], col['buildid'], col['buildurl'], col['dockersha'], col['dockertag'], col['gitcommit'], col['gitrepo'], col['giturl'])  # this will be changed
                data_list.append(row)

            # print (data_list)
            conn = create_conn()
            cursor = conn.cursor()
            # # execute the INSERT statement
            records_list_template = ','.join(['%s'] * len(data_list))
            sql = 'INSERT INTO dm.dm_componentitem(id, compid, status, buildid, buildurl, dockersha, dockertag, gitcommit, gitrepo, giturl) VALUES {}'.format(records_list_template)
            cursor.execute(sql, data_list)
            # commit the changes to the database
            rows_inserted = cursor.rowcount
            # Commit the changes to the database
            conn.commit()
            if rows_inserted > 0:
                return ({"message": 'components updated succesfully'}), HTTPStatus.CREATED

            return ({"message": 'components not updated'}), HTTPStatus.OK

        except Exception as err:
            print(err)
            conn.rollback()
            return ({"message": str(err)}), HTTPStatus.INTERNAL_SERVER_ERROR


##
# Actually setup the Api resource routing here
##
api.add_resource(CompItem, '/msapi/compitem')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
