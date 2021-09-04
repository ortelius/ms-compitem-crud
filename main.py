import os
from collections import OrderedDict

import uvicorn
import psycopg2
import psycopg2.extras
import requests
from sqlalchemy import create_engine
from fastapi import FastAPI, Query, Request, Response, HTTPException, status
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import List, Optional

# Init Globals
service_name = 'ortelius-ms-compitem-crud'

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
validateuser_url = os.getenv("VALIDATEUSER_URL", "http://localhost:5000")

engine = create_engine("postgresql+psycopg2://" + db_user + ":" + db_pass + "@" + db_host +":"+ db_port + "/" + db_name)

#adding custom details
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=service_name,
        version="",
        description=service_name,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": ""
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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
    repositoryid: Optional[int] = None
    target: Optional[str] = None
    name: Optional[str] = None
    summary: Optional[str] = None
    predecessorid: Optional[int] = None
    xpos: Optional[int] = None
    ypos: Optional[int] = None
    creatorid: Optional[int] = None
    created: Optional[int] = None
    modifierid: Optional[int] = None
    modified: Optional[int] = None
    status: str
    rollup: Optional[int] = None
    rollback: Optional[int] = None
    kind: Optional[str] = None
    buildid: Optional[str] = None
    buildurl: Optional[str] = None
    chart: Optional[str] = None
    operator: Optional[str] = None
    builddate: Optional[str] = None
    dockersha: Optional[str] = None
    gitcommit: Optional[str] = None
    gitrepo: Optional[str] = None
    gittag: Optional[str] = None
    giturl: Optional[str] = None
    dockerrepo: Optional[str] = None
    chartversion: Optional[str] = None
    chartnamespace: Optional[str] = None
    dockertag: Optional[str] = None
    chartrepo: Optional[str] = None
    chartrepourl: Optional[str] = None
    serviceowner: Optional[str] = None
    serviceowneremail: Optional[str] = None
    serviceownerphone: Optional[str] = None 
    slackchannel: Optional[str] = None
    discordchannel: Optional[str] = None
    hipchatchannel: Optional[str] = None
    pagerdutyurl: Optional[str] = None
    pagerdutybusinessurl: Optional[str] = None
     
class CompItemModelList(BaseModel):
    data: List[CompItemModel]
    
class Message(BaseModel):
    detail: str
    
   
@app.get('/msapi/compitem',
        response_model=CompItemModel,
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
async def get_compitem(request: Request, compitemid:int):
    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")
    
        if (result.status_code != status.HTTP_200_OK):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    try:
        with engine.connect() as connection:
            conn = connection.connection
            authorized = False      # init to not authorized
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            sql = """select compid, id, name, rollup, rollback, repositoryid, target, xpos, ypos,
                        kind, buildid, buildurl, chart, operator, builddate, dockersha, gitcommit,
                        gitrepo, gittag, giturl, chartversion, chartnamespace, dockertag, chartrepo,
                        chartrepourl, serviceowner, serviceowneremail, serviceownerphone, 
                        slackchannel, discordchannel, hipchatchannel, pagerdutyurl, pagerdutybusinessurl
                        from dm.dm_componentitem where id = %s"""
    
            params = (str(compitemid),)
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
        return result[0]
    
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
        
        with engine.connect() as connection:
            conn = connection.connection
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
            response.status_code = status.HTTP_201_CREATED
            return {"message": 'components created succesfully'}
        
        response.status_code = status.HTTP_200_OK
        return {"message": 'components not created'}

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
async def delete_compitem(compid: int):

    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
        if (result is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")
    
        if (result.status_code != status.HTTP_200_OK):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

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
async def update_compitem(compitemList: List[CompItemModel]):

    # try:
    #     result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies)
    #     if (result is None):
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")
    #
    #     if (result.status_code != status.HTTP_200_OK):
    #             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    # except Exception as err:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    try:
        data_list = []
        for col in compitemList:
            row = (col.compid, col.status, col.buildid, col.buildurl, col.dockersha, col.dockertag, col.gitcommit, col.gitrepo, col.giturl, col.id)  # this will be changed
            data_list.append(row)

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

    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from None
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
