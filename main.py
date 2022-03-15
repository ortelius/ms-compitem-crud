# Copyright (c) 2021 Linux Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import socket
from collections import OrderedDict
from time import sleep
from typing import List, Optional

import psycopg2
import psycopg2.extras
import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.exc import InterfaceError, OperationalError, StatementError

# Init Globals
service_name = 'ortelius-ms-compitem-crud'
db_conn_retry = 3

app = FastAPI(
    title=service_name,
    description=service_name
    )

# Init db connection
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "postgres")
db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASS", "postgres")
db_port = os.getenv("DB_PORT", "5432")
validateuser_url = os.getenv('VALIDATEUSER_URL', None )

if (validateuser_url is None):
    validateuser_host = os.getenv('MS_VALIDATE_USER_SERVICE_HOST', '127.0.0.1')
    host = socket.gethostbyaddr(validateuser_host)[0]
    validateuser_url = 'http://' + host + ':' + str(os.getenv('MS_VALIDATE_USER_SERVICE_PORT', 80))

engine = create_engine("postgresql+psycopg2://" + db_user + ":" + db_pass + "@" + db_host +":"+ db_port + "/" + db_name, pool_pre_ping=True)

# health check endpoint
class StatusMsg(BaseModel):
    status: str
    service_name: Optional[str] = None
    
@app.get("/health",
         responses={
             503: {"model": StatusMsg,
                   "description": "DOWN Status for the Service",
                   "content": {
                       "application/json": {
                           "example": {"status": 'DOWN'}
                       },
                   },
                   },
             200: {"model": StatusMsg,
                   "description": "UP Status for the Service",
                   "content": {
                       "application/json": {
                           "example": {"status": 'UP', "service_name": service_name}
                       }
                   },
                   },
         }
         )
async def health(response: Response):
    try:
        with engine.connect() as connection:
            conn = connection.connection
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            if cursor.rowcount > 0:
                return {"status": 'UP', "service_name": service_name}
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": 'DOWN'}

    except Exception as err:
        print(str(err))
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": 'DOWN'}
# end health check

class CompItemModel(BaseModel):
    compid: int
    id: int
    builddate: Optional[str] = None
    buildid: Optional[str] = None
    buildurl: Optional[str] = None
    chart: Optional[str] = None
    chartnamespace: Optional[str] = None
    chartrepo: Optional[str] = None
    chartrepourl: Optional[str] = None
    chartversion: Optional[str] = None
    created: Optional[int] = None
    creatorid: Optional[int] = None
    discordchannel: Optional[str] = None
    dockerrepo: Optional[str] = None
    dockersha: Optional[str] = None
    dockertag: Optional[str] = None
    gitcommit: Optional[str] = None
    gitrepo: Optional[str] = None
    gittag: Optional[str] = None
    giturl: Optional[str] = None
    hipchatchannel: Optional[str] = None
    kind: Optional[str] = None
    modified: Optional[int] = None
    modifierid: Optional[int] = None
    name: Optional[str] = None
    pagerdutybusinessurl: Optional[str] = None
    pagerdutyurl: Optional[str] = None
    predecessorid: Optional[int] = None
    repository: Optional[str] = None
    rollback: Optional[int] = None
    rollup: Optional[int] = None
    serviceowner: Optional[str] = None
    serviceowneremail: Optional[str] = None
    serviceownerid: Optional[str] = None
    serviceownerphone: Optional[str] = None 
    slackchannel: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    targetdirectory: Optional[str] = None
    xpos: Optional[int] = None
    ypos: Optional[int] = None
     
class CompItemModelList(BaseModel):
    data: List[CompItemModel]
    
class Message(BaseModel):
    detail: str
    
   
@app.get('/msapi/compitem',
        response_model=List[CompItemModel],
        responses={
             401: {"model": Message,
                   "description": "Authorization Status",
                   "content": {
                       "application/json": {
                           "example": {"detail": "Authorization failed"}
                       },
                   },
                   },
             500: {"model": Message,
                   "description": "SQL Error",
                   "content": {
                       "application/json": {
                           "example": {"detail": "SQL Error: 30x"}
                       },
                   },
                    } #,
             # 200: {
             #     "description": "List of domain ids the user belongs to.",
             #     "content": {
             #         "application/json": {
             #             "example": [1, 200, 201, 5033]
             #         }
             #     },
             # },
         }
         )
async def get_compitem(request: Request, compitemid:int, comptype: Optional[str] = ''):
    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")
    
        if (result.status_code != status.HTTP_200_OK):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    try:
        #Retry logic for failed query
        no_of_retry = db_conn_retry
        attempt = 1;
        while True:
            try:
                with engine.connect() as connection:
                    conn = connection.connection
                    authorized = False      # init to not authorized
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

                    sql = """select a.compid, a.id, a.name, a.rollup, a.rollback, fulldomain(r.domainid, r.name) "repository", target "targetdirectory", a.xpos, a.ypos,
                                kind, buildid, buildurl, chart, builddate, dockerrepo, dockersha, gitcommit,
                                gitrepo, gittag, giturl, chartversion, chartnamespace, dockertag, chartrepo,
                                chartrepourl, c.id "serviceownerid", c.realname "serviceowner", c.email "serviceowneremail", c.phone "serviceownerphone", 
                                slackchannel, discordchannel, hipchatchannel, pagerdutyurl, pagerdutybusinessurl
                                from dm.dm_componentitem a, dm.dm_component b, dm.dm_user c, dm.dm_repository r 
                                where a.compid = b.id and b.ownerid = c.id and a.repositoryid = r.id and a.id = %s
                            union
                                select a.compid, a.id, a.name, a.rollup, a.rollback, null, target "targetdirectory", a.xpos, a.ypos,
                                kind, buildid, buildurl, chart, builddate, dockerrepo, dockersha, gitcommit,
                                gitrepo, gittag, giturl, chartversion, chartnamespace, dockertag, chartrepo,
                                chartrepourl, c.id "serviceownerid", c.realname "serviceowner", c.email "serviceowneremail", c.phone "serviceownerphone", 
                                slackchannel, discordchannel, hipchatchannel, pagerdutyurl, pagerdutybusinessurl
                                from dm.dm_componentitem a, dm.dm_component b, dm.dm_user c
                                where a.compid = b.id and b.ownerid = c.id and a.repositoryid is null and a.id = %s"""
            
                    params = (str(compitemid),str(compitemid),)
                    cursor.execute(sql, params)
                    result = cursor.fetchall()
                    if (not result):
                        if (comptype == 'rf_database'):
                            result = [OrderedDict([('compid', -1), ('id', compitemid), ('name', None), 
                                        ('serviceownerid', None), ('serviceowner', None), ('serviceowneremail', None), ('serviceownerphone', None),
                                        ('slackchannel', None), ('discordchannel', None), ('hipchatchannel', None), ('pagerdutyurl', None), ('pagerdutybusinessurl', None),
                                        ('rollup', 1), ('rollback', 0), ('repository', None), 
                                        ('targetdirectory', None), ('xpos', None), ('ypos', None),  ('kind', None), ('builddate', None), ('buildid', None), ('buildurl', None),
                                        ('chartrepo', None), ('chartrepourl', None), ('chart', None), ('chartversion', None), ('chartnamespace', None), 
                                        ('dockerrepo', None), ('dockertag', None), ('dockersha', None), 
                                        ('gitcommit', None), ('gitrepo', None), ('gittag', None), ('giturl', None)])]
                        elif (comptype == 'rb_database'):
                            result = [OrderedDict([('compid', -1), ('id', compitemid), ('name', None), 
                                        ('serviceownerid', None), ('serviceowner', None), ('serviceowneremail', None), ('serviceownerphone', None),
                                        ('slackchannel', None), ('discordchannel', None), ('hipchatchannel', None), ('pagerdutyurl', None), ('pagerdutybusinessurl', None),
                                        ('rollup', 0), ('rollback', 1), ('repository', None), 
                                        ('targetdirectory', None), ('xpos', None), ('ypos', None),  ('kind', None), ('builddate', None), ('buildid', None), ('buildurl', None),
                                        ('chartrepo', None), ('chartrepourl', None), ('chart', None), ('chartversion', None), ('chartnamespace', None), 
                                        ('dockerrepo', None), ('dockertag', None), ('dockersha', None), 
                                        ('gitcommit', None), ('gitrepo', None), ('gittag', None), ('giturl', None)])]
                        else:
                            result = [OrderedDict([('compid', -1), ('id', compitemid), ('name', None), 
                                        ('serviceownerid', None), ('serviceowner', None), ('serviceowneremail', None), ('serviceownerphone', None),
                                        ('slackchannel', None), ('discordchannel', None), ('hipchatchannel', None), ('pagerdutyurl', None), ('pagerdutybusinessurl', None),
                                        ('rollup', 0), ('rollback', 0), ('repository', None), 
                                        ('targetdirectory', None), ('xpos', None), ('ypos', None),  ('kind', None), ('builddate', None), ('buildid', None), ('buildurl', None),
                                        ('chartrepo', None), ('chartrepourl', None), ('chart', None), ('chartversion', None), ('chartnamespace', None), 
                                        ('dockerrepo', None), ('dockertag', None), ('dockersha', None), 
                                        ('gitcommit', None), ('gitrepo', None), ('gittag', None), ('giturl', None)])]
                    cursor.close()
                    conn.close()
                return result
            
            except (InterfaceError, OperationalError) as ex:
                if attempt < no_of_retry:
                    sleep_for = 0.2
                    logging.error(
                        "Database connection error: {} - sleeping for {}s"
                        " and will retry (attempt #{} of {})".format(
                            ex, sleep_for, attempt, no_of_retry
                        )
                    )
                    #200ms of sleep time in cons. retry calls 
                    sleep(sleep_for) 
                    attempt += 1
                    continue
                else:
                    raise
                    
    except HTTPException:
        raise
    except Exception as err:
        print(err)
        # conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from None

# Not implemented fully.  SQL query is not complete

@app.post("/msapi/compitem",
         responses={
             401: {"model": Message,
                   "description": "Authorization Status",
                   "content": {
                       "application/json": {
                           "example": {"detail": "Authorization failed"}
                       },
                   },
                   },
             500: {"model": Message,
                   "description": "SQL Error",
                   "content": {
                       "application/json": {
                           "example": {"detail": "SQL Error: 30x"}
                       },
                   },
                }
         }
         )
async def create_compitem(response: Response, request: Request, compItemList: List[CompItemModel]):

    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")
    
        if (result.status_code != status.HTTP_200_OK):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    try:
        data_list = []
        for col in compItemList:
            row = (col.id, col.compid, col.status, col.buildid, col.buildurl, col.dockersha, col.dockertag, col.gitcommit, col.gitrepo, col.giturl)  # this will be changed
            data_list.append(row)
        
        records_list_template = ','.join(['%s'] * len(data_list))
        sql = 'INSERT INTO dm.dm_componentitem(id, compid, status, buildid, buildurl, dockersha, dockertag, gitcommit, gitrepo, giturl) \
                            VALUES {}'.format(records_list_template)
                            
        #Retry logic for failed query
        no_of_retry = db_conn_retry
        attempt = 1;
        while True:
            try:
                with engine.connect() as connection:
                    conn = connection.connection
                    cursor = conn.cursor()
                    cursor.execute(sql, data_list)
                    # commit the changes to the database
                    rows_inserted = cursor.rowcount
                    # Commit the changes to the database
                    conn.commit()
                    conn.close()
                    
                    if rows_inserted > 0:
                        response.status_code = status.HTTP_201_CREATED
                        return {"message": 'components created succesfully'}
                
                    response.status_code = status.HTTP_200_OK
                    return {"message": 'components not created'}
                
            except (InterfaceError, OperationalError) as ex:
                if attempt < no_of_retry:
                    sleep_for = 0.2
                    logging.error(
                        "Database connection error: {} - sleeping for {}s"
                        " and will retry (attempt #{} of {})".format(
                            ex, sleep_for, attempt, no_of_retry
                        )
                    )
                    #200ms of sleep time in cons. retry calls 
                    sleep(sleep_for) 
                    attempt += 1
                    continue
                else:
                    raise
                
    except HTTPException:
        raise
    except Exception as err:
        print(err)
        # conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from None

@app.delete("/msapi/compitem",
         responses={
             401: {"model": Message,
                   "description": "Authorization Status",
                   "content": {
                       "application/json": {
                           "example": {"detail": "Authorization failed"}
                       },
                   },
                   },
             500: {"model": Message,
                   "description": "SQL Error",
                   "content": {
                       "application/json": {
                           "example": {"detail": "SQL Error: 30x"}
                       },
                   },
                }
         }
         )
async def delete_compitem(request: Request, compid: int):

    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")
    
        if (result.status_code != status.HTTP_200_OK):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    try:
        
        #Retry logic for failed query
        no_of_retry = db_conn_retry
        attempt = 1;
        while True:
            try:
                with engine.connect() as connection:
                    conn = connection.connection
                    cursor = conn.cursor()
            
                    sql1 = "DELETE from dm.dm_compitemprops where compitemid in (select id from dm.dm_componentitem where compid = " + str(compid) + ")"
                    sql2 = "DELETE from dm.dm_componentitem where compid=" + str(compid)
                    rows_deleted = 0
                    cursor.execute(sql1)
                    cursor.execute(sql2)
                    rows_deleted = cursor.rowcount
                    # Commit the changes to the database
                    conn.commit()
            
                # response.status_code = status.HTTP_200_OK
                return {"message": 'component deleted succesfully'}
                
            except (InterfaceError, OperationalError) as ex:
                if attempt < no_of_retry:
                    logging.error(
                        "Database connection error: {} - sleeping for {}s"
                        " and will retry (attempt #{} of {})".format(
                            ex, sleep_for, attempt, no_of_retry
                        )
                    )
                    #200ms of sleep time in cons. retry calls 
                    sleep(0.2) 
                    attempt += 1
                    continue
                else:
                    raise
                
    except HTTPException:
        raise
    except Exception as err:
        print(err)
        # conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from None

@app.put("/msapi/compitem",
         responses={
             401: {"model": Message,
                   "description": "Authorization Status",
                   "content": {
                       "application/json": {
                           "example": {"detail": "Authorization failed"}
                       },
                   },
                   },
             500: {"model": Message,
                   "description": "SQL Error",
                   "content": {
                       "application/json": {
                           "example": {"detail": "SQL Error: 30x"}
                       },
                   },
                }
         }
         )
async def update_compitem(request: Request, compitemList: List[CompItemModel]):

    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")
    
        if (result.status_code != status.HTTP_200_OK):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    try:
        
        data_list = []
        for col in compitemList:
            row = (col.compid, col.status, col.buildid, col.buildurl, col.dockersha, col.dockertag, col.gitcommit, col.gitrepo, col.giturl, col.id)  # this will be changed
            data_list.append(row)
            
        #Retry logic for failed query
        no_of_retry = db_conn_retry
        attempt = 1;
        while True:
            try:
                with engine.connect() as connection:
                    conn = connection.connection
                    cursor = conn.cursor()
                    # # execute the INSERT statement
                    # records_list_template = ','.join(['%s'] * len(data_list))
                    sql = 'UPDATE dm.dm_componentitem set compid=%s, status=%s, buildid=%s, buildurl=%s, dockersha=%s, dockertag=%s, gitcommit=%s, gitrepo=%s, giturl=%s \
                    WHERE id = %s'
                    cursor.executemany(sql, data_list)
                    # commit the changes to the database
                    rows_inserted = cursor.rowcount
                    # Commit the changes to the database
                    conn.commit()
                    
                if rows_inserted > 0:
                    return {"message": 'components updated succesfully'}
        
                return {"message": 'components not updated'}
                
            except (InterfaceError, OperationalError) as ex:
                if attempt < no_of_retry:
                    sleep_for = 0.2
                    logging.error(
                        "Database connection error: {} - sleeping for {}s"
                        " and will retry (attempt #{} of {})".format(
                            ex, sleep_for, attempt, no_of_retry
                        )
                    )
                    #200ms of sleep time in cons. retry calls 
                    sleep(sleep_for) 
                    attempt += 1
                    continue
                else:
                    raise
                
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from None
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
