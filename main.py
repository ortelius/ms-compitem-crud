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

# pylint: disable=E0401,E0611
# pyright: reportMissingImports=false,reportMissingModuleSource=false

import logging
import os
import socket
from time import sleep
from typing import Optional

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel  # pylint: disable=E0611
from sqlalchemy import create_engine
from sqlalchemy.exc import InterfaceError, OperationalError

# Init Globals
SERVICE_NAME = "ortelius-ms-compitem-crud"
DB_CONN_RETRY = 3

app = FastAPI(title=SERVICE_NAME, description=SERVICE_NAME)

# Init db connection
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "postgres")
db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASS", "postgres")
db_port = os.getenv("DB_PORT", "5432")
validateuser_url = os.getenv("VALIDATEUSER_URL", "")

if len(validateuser_url) == 0:
    validateuser_host = os.getenv("MS_VALIDATE_USER_SERVICE_HOST", "127.0.0.1")
    host = socket.gethostbyaddr(validateuser_host)[0]
    validateuser_url = "http://" + host + ":" + str(os.getenv("MS_VALIDATE_USER_SERVICE_PORT", "80"))

engine = create_engine("postgresql+psycopg2://" + db_user + ":" + db_pass + "@" + db_host + ":" + db_port + "/" + db_name, pool_pre_ping=True)


# health check endpoint
class StatusMsg(BaseModel):
    status: str = ""
    service_name: str = ""


@app.get("/health")
async def health(response: Response) -> StatusMsg:
    """
    This health check end point used by Kubernetes
    """
    try:
        with engine.connect() as connection:
            conn = connection.connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            if cursor.rowcount > 0:
                return StatusMsg(status="UP", service_name=SERVICE_NAME)
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return StatusMsg(status="DOWN", service_name=SERVICE_NAME)

    except Exception as err:
        print(str(err))
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return StatusMsg(status="DOWN", service_name=SERVICE_NAME)


# end health check


class CompItemModel(BaseModel):
    compid: int = 0
    id: int = 0
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


@app.get("/msapi/compitem")
async def get_compitem(request: Request, compitemid: int, comptype: Optional[str] = "") -> list[CompItemModel]:
    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies, timeout=5)
        if result is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")

        if result.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    compitem_list = []
    try:
        # Retry logic for failed query
        no_of_retry = DB_CONN_RETRY
        attempt = 1
        while True:
            try:
                with engine.connect() as connection:
                    conn = connection.connection
                    cursor = conn.cursor()

                    sqlstmt = """select a.compid, a.id, a.name, a.rollup, a.rollback, dm.fulldomain(r.domainid, r.name) "repository", target "targetdirectory", a.xpos, a.ypos,
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

                    params = (
                        str(compitemid),
                        str(compitemid),
                    )
                    cursor.execute(sqlstmt, params)
                    rows = cursor.fetchall()
                    if not rows:
                        cim = CompItemModel(compid=-1, id=compitemid)

                        if comptype == "rf_database":
                            cim.rollup = 1
                            cim.rollback = 0
                        elif comptype == "rb_database":
                            cim.rollup = 0
                            cim.rollback = 1
                        else:
                            cim.rollup = 0
                            cim.rollback = 0
                        compitem_list.append(cim)
                    else:
                        for row in rows:
                            cim = CompItemModel(compid=row[0], id=row[1])
                            cim.name = row[2]
                            cim.rollup = row[3]
                            cim.rollback = row[4]
                            cim.repository = row[5]
                            cim.targetdirectory = row[6]
                            cim.xpos = row[7]
                            cim.ypos = row[8]
                            cim.kind = row[9]
                            cim.buildid = row[10]
                            cim.buildurl = row[11]
                            cim.chart = row[12]
                            cim.builddate = row[13]
                            cim.dockerrepo = row[14]
                            cim.dockersha = row[15]
                            cim.gitcommit = row[16]
                            cim.gitrepo = row[17]
                            cim.gittag = row[18]
                            cim.giturl = row[19]
                            cim.chartversion = row[20]
                            cim.chartnamespace = row[21]
                            cim.dockertag = row[22]
                            cim.chartrepo = row[23]
                            cim.chartrepourl = row[24]
                            cim.serviceownerid = row[25]
                            cim.serviceowner = row[26]
                            cim.serviceowneremail = row[27]
                            cim.serviceownerphone = row[28]
                            cim.slackchannel = row[29]
                            cim.discordchannel = row[30]
                            cim.hipchatchannel = row[31]
                            cim.pagerdutyurl = row[32]
                            cim.pagerdutybusinessurl = row[33]
                            compitem_list.append(cim)
                    cursor.close()
                    conn.close()
                return compitem_list

            except (InterfaceError, OperationalError) as ex:
                if attempt < no_of_retry:
                    sleep_for = 0.2
                    logging.error("Database connection error: %s - sleeping for %d seconds and will retry (attempt #%d of %d)", ex, sleep_for, attempt, no_of_retry)
                    # 200ms of sleep time in cons. retry calls
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


@app.post("/msapi/compitem")
async def create_compitem(response: Response, request: Request, compitem_list: list[CompItemModel]):
    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies, timeout=5)
        if result is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")

        if result.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    try:
        data_list = []
        for col in compitem_list:
            row = (col.id, col.compid, col.status, col.buildid, col.buildurl, col.dockersha, col.dockertag, col.gitcommit, col.gitrepo, col.giturl)  # this will be changed
            data_list.append(row)

        sqlstmt = "INSERT INTO dm.dm_componentitem(id, compid, status, buildid, buildurl, dockersha, dockertag, gitcommit, gitrepo, giturl) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # Retry logic for failed query
        no_of_retry = DB_CONN_RETRY
        attempt = 1
        while True:
            try:
                with engine.connect() as connection:
                    conn = connection.connection
                    cursor = conn.cursor()
                    cursor.execute(sqlstmt, data_list)
                    # commit the changes to the database
                    rows_inserted = cursor.rowcount
                    # Commit the changes to the database
                    conn.commit()
                    conn.close()

                    if rows_inserted > 0:
                        response.status_code = status.HTTP_201_CREATED
                        return {"message": "components created succesfully"}

                    response.status_code = status.HTTP_200_OK
                    return {"message": "components not created"}

            except (InterfaceError, OperationalError) as ex:
                if attempt < no_of_retry:
                    sleep_for = 0.2
                    logging.error("Database connection error: %s - sleeping for %d seconds and will retry (attempt #%d of %d)", ex, sleep_for, attempt, no_of_retry)
                    # 200ms of sleep time in cons. retry calls
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


@app.delete("/msapi/compitem")
async def delete_compitem(request: Request, compid: int):
    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies, timeout=5)
        if result is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")

        if result.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    try:
        # Retry logic for failed query
        no_of_retry = DB_CONN_RETRY
        attempt = 1
        while True:
            try:
                with engine.connect() as connection:
                    conn = connection.connection
                    cursor = conn.cursor()

                    sql1 = "DELETE from dm.dm_compitemprops where compitemid in (select id from dm.dm_componentitem where compid = %s)"
                    sql2 = "DELETE from dm.dm_componentitem where compid=%s"
                    params = tuple([compid])
                    cursor.execute(sql1, params)
                    cursor.execute(sql2, params)
                    # Commit the changes to the database
                    conn.commit()

                # response.status_code = status.HTTP_200_OK
                return {"message": "component deleted succesfully"}

            except (InterfaceError, OperationalError) as ex:
                sleep_for = 0.2
                if attempt < no_of_retry:
                    logging.error("Database connection error: %s - sleeping for %d seconds and will retry (attempt #%d of %d)", ex, sleep_for, attempt, no_of_retry)
                    # 200ms of sleep time in cons. retry calls
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


@app.put("/msapi/compitem")
async def update_compitem(request: Request, compitem_list: list[CompItemModel]):
    try:
        result = requests.get(validateuser_url + "/msapi/validateuser", cookies=request.cookies, timeout=5)
        if result is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")

        if result.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed status_code=" + str(result.status_code))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed:" + str(err)) from None

    try:
        data_list = []
        for col in compitem_list:
            row = (col.compid, col.status, col.buildid, col.buildurl, col.dockersha, col.dockertag, col.gitcommit, col.gitrepo, col.giturl, col.id)  # this will be changed
            data_list.append(row)

        # Retry logic for failed query
        no_of_retry = DB_CONN_RETRY
        attempt = 1
        while True:
            try:
                with engine.connect() as connection:
                    conn = connection.connection
                    cursor = conn.cursor()
                    # # execute the INSERT statement
                    # records_list_template = ','.join(['%s'] * len(data_list))
                    sqlstmt = "UPDATE dm.dm_componentitem set compid=%s, status=%s, buildid=%s, buildurl=%s, dockersha=%s, dockertag=%s, gitcommit=%s, gitrepo=%s, giturl=%s \
                    WHERE id = %s"
                    cursor.executemany(sqlstmt, data_list)
                    # commit the changes to the database
                    rows_inserted = cursor.rowcount
                    # Commit the changes to the database
                    conn.commit()

                if rows_inserted > 0:
                    return {"message": "components updated succesfully"}

                return {"message": "components not updated"}

            except (InterfaceError, OperationalError) as ex:
                if attempt < no_of_retry:
                    sleep_for = 0.2
                    logging.error("Database connection error: %s - sleeping for %d seconds and will retry (attempt #%d of %d)", ex, sleep_for, attempt, no_of_retry)
                    # 200ms of sleep time in cons. retry calls
                    sleep(sleep_for)
                    attempt += 1
                    continue
                else:
                    raise

    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from None


if __name__ == "__main__":
    uvicorn.run(app, port=5001)
