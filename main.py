import json
import os
from pprint import pprint

import psycopg2
import pybreaker
import psycopg2.extras
import requests
from flask import Flask, request
from flask_restful import Api, Resource
from collections import OrderedDict

# Init Flask
app = Flask(__name__)
api = Api(app)

# Init db connection
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "postgres")
db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASS", "postgres")
db_port = os.getenv("DB_PORT", "5432")
validateuser_url = os.getenv("VALIDATEUSER_URL", "http://localhost:5000")

conn_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=1,
    reset_timeout=10,
)

@conn_circuit_breaker
def create_conn():
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_pass, port=db_port)
    return conn

class CompItem(Resource):

    @classmethod
    def get(cls):

        pprint(request.cookies)
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            return None, 404

        if (result.status_code != 200):
            return result.json(), 404
        
        try:
            compitemid = request.args.get('compitemid',"-1")
            conn = create_conn()
            cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
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

            print(result)
            return result
        except Exception as err:
            print(err)
            return err

    @classmethod
    def post(cls):  # completed
        try:
            
            pprint(request.cookies)
            result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
            
            if (result is None):
                    return None, 404

            if (result.status_code != 200):
                return result.json(), 404
        
            input = request.get_json();
            data_list = []
            for i in input:
                d = (i['id'], i['compid'], i['status'], i['buildid'], i['buildurl'], i['dockersha'], i['dockertag'], i['gitcommit'], i['gitrepo'], i['giturl']) # this will be changed
                data_list.append(d)

            print (data_list) 
            conn = create_conn() 
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
            return rows_inserted

        except Exception as err:
            print(err)
            conn = create_conn() 
            cursor = conn.cursor()
            cursor.execute("ROLLBACK")
            conn.commit()
            return err

    @classmethod
    def delete(cls):
        try:
            pprint(request.cookies)
            result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
            if (result is None):
                return None, 404
    
            if (result.status_code != 200):
                return result.json(), 404
        
            comp_id = request.args.get('comp_id')
            #comp_item_id = request.args.get('comp_item_id')
            conn = create_conn() 
            cursor = conn.cursor()
            sql = "select id from dm.dm_componentitem where compid = " + comp_id
            t = tuple()
            l = []
            cursor.execute(sql)
            row = cursor.fetchone()
            while row:
                print (row)
                l = list(t)
                l.append(row[0])
                t = tuple(l)
                row = cursor.fetchone()

            sql1 = "DELETE from dm.dm_compitemprops where compitemid in " + str(t)
            sql2 = "DELETE from dm.dm_componentitem where compid=" + comp_id
            rows_deleted = 0
            with conn.cursor() as cursor:
                cursor.execute(sql1)
                cursor.execute(sql2)
                rows_deleted = cursor.rowcount
            # Commit the changes to the database
            conn.commit()
            return rows_deleted
        except Exception as err:
            print(err)
            return err

    @classmethod
    def put(cls):  # not completed
        try:
            
            pprint(request.cookies)
            result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
            if (result is None):
                return None, 404
    
            if (result.status_code != 200):
                return result.json(), 404
        
            input = request.get_json();
            data_list = []
            # for i in input:
            #     d = (i['id'], i['compid'], i['status'], i['buildid'], i['buildurl'], i['dockersha'], i['dockertag'], i['gitcommit'], i['gitrepo'], i['giturl']) # this will be changed
            #     data_list.append(d)

            # print (data_list)
            conn = create_conn() 
            cursor = conn.cursor()
            # # execute the INSERT statement
            # records_list_template = ','.join(['%s'] * len(data_list))
            # sql = 'INSERT INTO dm.dm_componentitem(id, compid, status, buildid, buildurl, dockersha, dockertag, gitcommit, gitrepo, giturl) \
            #     VALUES {}'.format(records_list_template)
            cursor.execute(sql, data_list)
            # commit the changes to the database
            rows_inserted = cursor.rowcount
            # Commit the changes to the database
            conn.commit()
            return rows_inserted

        except Exception as err:
            print(err)
            conn = create_conn() 
            cursor = conn.cursor()
            cursor.execute("ROLLBACK")
            conn.commit()
            return err 
        
##
# Actually setup the Api resource routing here
##
api.add_resource(CompItem, '/msapi/compitem')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
