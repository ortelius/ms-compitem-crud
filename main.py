import os

import psycopg2
from flask import Flask, request
from flask_restful import Api, Resource

# Init Flask
app = Flask(__name__)
api = Api(app)

# Init db connection
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "postgres")
db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASS", "postgres")
db_port = os.getenv("DB_PORT", "5432")

conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_pass, port=db_port)

class CompItem(Resource):  
    @classmethod
    def get(cls):  # completed
        try: 
            comp_id = request.args.get('comp_id')
            cursor = conn.cursor()
            sql = "select * from dm.dm_componentitem where compid = " + comp_id
            result = []
            cursor.execute(sql)
            row = cursor.fetchone()
            while row:
                # new items needs to be added here
                cols = {}
                cols['id'] = row[0]
                cols['compid'] = row[1]
                cols['buildid'] = row[17]
                cols['buildurl'] = row[18]
                cols['dockersha'] = row[22]
                cols['dockertag'] = row[30]
                cols['gitcommit'] = row[23]
                cols['gitrepo'] = row[24]
                cols['giturl'] = row[26]

                result.append(cols)
                row = cursor.fetchone()

            return result
        except Exception as err:
            print(err)
            return err
 

    def post(cls):  # completed
        try: 
            input = request.get_json();
            data_list = []
            for i in input:
                d = (i['id'], i['compid'], i['status'], i['buildid'], i['buildurl'], i['dockersha'], i['dockertag'], i['gitcommit'], i['gitrepo'], i['giturl']) # this will be changed
                data_list.append(d)

            print (data_list) 
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
            return rows_inserted;

        except Exception as err:
            print(err)
            cursor = conn.cursor()
            cursor.execute("ROLLBACK")
            conn.commit() 



    def delete(cls):  # completed but an issue of props table
        try:
            comp_id = request.args.get('comp_id')
            cursor = conn.cursor()
            sql = "DELETE from dm.dm_componentitem where compid=" + comp_id
            print (sql)
            cursor.execute(sql)
            rows_deleted = cursor.rowcount
            # Commit the changes to the database
            conn.commit()
            return rows_deleted
        except Exception as err:
            print(err)
            cursor = conn.cursor()
            cursor.execute("ROLLBACK")
            conn.commit() 
    
    def put(cls):  # not completed 
        input = request.get_json();
        print (input)        
        return "hello put" 
##
# Actually setup the Api resource routing here
##
api.add_resource(CompItem, '/msapi/compitem')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)