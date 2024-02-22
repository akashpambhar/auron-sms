import re
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from pymemcache.client import base
from database3 import get_db
import random
import xlsxwriter
from fastapi.responses import FileResponse
from pyreportjasper import PyReportJasper
import os
from routers import auth
from typing import Annotated
from schemas import UserSchema, RoleSchema
import json

router = APIRouter(prefix="/d3/sms", tags=["sms3"])

mc = base.Client((os.getenv("MC_SERVER"), 11211))

def cache_get_all_sms(
    db: Session = next(get_db())
):
    random_number = str(random.randint(1, 10000000))

    try:
        query = text(
            """
DECLARE @command NVARCHAR(MAX)

CREATE TABLE #TempResults_""" + random_number + """ (
    MessageID int,
    ToAddress NVARCHAR(32),
    Body NVARCHAR(MAX),
    StatusID NVARCHAR(32),
	SentTime DATETIME2(7)
)

SELECT @command = '
DECLARE @currentDB NVARCHAR(MAX);
DECLARE @table_name NVARCHAR(MAX);
DECLARE @sql_query NVARCHAR(MAX);

SET @currentDB = ''?''; -- Store the current database name

IF (@currentDB LIKE ''au%'' OR @currentDB LIKE ''ar%'') AND @currentDB NOT LIKE ''auron_sms'' AND @currentDB NOT LIKE ''Auintegration'' AND @currentDB NOT LIKE ''AuSmsServer-gw8'' AND @currentDB NOT LIKE ''ArchAuSmsServer-gw8'' 
BEGIN 
USE [?]
    IF (LOWER(LEFT(@currentDB, 2)) = ''ar'')
        SET @table_name = ''ArchMessages''
    ELSE
        SET @table_name = ''Messages''

    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = @table_name AND COLUMN_NAME = ''OriginalID'')
        BEGIN
            SET @sql_query = 
                ''INSERT INTO #TempResults_""" + random_number + """ (MessageID, ToAddress, Body, StatusID, SentTime) '' +
                ''SELECT MessageID, ToAddress, Body, StatusID, SentTime '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a WITH (NOLOCK)'' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.OriginalID = b.MessageID '' + ''WHERE a.SentTime BETWEEN DATEADD(HOUR, -5, GETDATE()) AND GETDATE();''

            EXEC sp_executesql @sql_query
        END
    ELSE
        BEGIN
            SET @sql_query = 
                ''INSERT INTO #TempResults_""" + random_number + """ (MessageID, ToAddress, Body, StatusID, SentTime) '' +
                ''SELECT MessageID, ToAddress, Body, StatusID, SentTime '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a WITH (NOLOCK)'' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.id = b.MessageID '' + ''WHERE a.SentTime BETWEEN DATEADD(HOUR, -5, GETDATE()) AND GETDATE();''

            EXEC sp_executesql @sql_query
        END
END'

EXEC sp_MSforeachdb @command

SELECT TOP 2000 * FROM #TempResults_""" + random_number + """
    
DROP TABLE #TempResults_""" + random_number + """
        """
        )
        
        results = db.execute(query).fetchall()
        json_messages = json.dumps(set_db_result_to_json(results, RoleSchema.Role(role_id=1, role_name='admin')), default=str)
        mc.set("message_list3", json_messages)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing SQL query: {str(e)}"
        )

def set_db_result_to_json(results, current_active_user):
    messages = {
        "items": []
    }

    if results != []:
        if(current_active_user.role_id == 1):
            messages["items"] = [
                {
                    "MessageID": result[0],
                    "ToAddress": result[1],
                    "Body": result[2],
                    "StatusID": result[3],
                    "SentTime": result[4]
                }
                for result in results
            ]   
        else :
            messages["items"] = [
                {
                    "MessageID": result[0],
                    "ToAddress": result[1],
                    "Body": re.sub(r"\d", "*", result[2]),
                    "StatusID": result[3],
                    "SentTime": result[4]
                }
                for result in results
            ]

    return messages


def set_cached_result_to_json(results, current_active_user):
    messages = {
        "items": []
    }

    if results != []:
        if(current_active_user.role_id == 1):
            messages["items"] = [
                {
                    "MessageID": result["MessageID"],
                    "ToAddress": result["ToAddress"],
                    "Body": result["Body"],
                    "StatusID": result["StatusID"],
                    "SentTime": result["SentTime"]
                }
                for result in results
            ]
        else :
            messages["items"] = [
                {
                    "MessageID": result["MessageID"],
                    "ToAddress": result["ToAddress"],
                    "Body": re.sub(r"\d", "*", result["Body"]),
                    "StatusID": result["StatusID"],
                    "SentTime": result["SentTime"]
                }
                for result in results
            ]

    return messages


cache_get_all_sms()

@router.get("")
def get_all_sms(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_and_normal_user)],
):
    messages = mc.get("message_list3")
    messages = json.loads(messages)
    messages = set_cached_result_to_json(messages["items"], current_user)
    return messages


@router.get("/phone/{mobile_number}")
def get_all_sms_by_phone_number(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_and_normal_user)],
    mobile_number: str,
    db: Session = Depends(get_db)
):
    random_number = str(random.randint(1, 10000000))
    try:
        query = text(
            """
DECLARE @command NVARCHAR(MAX)

CREATE TABLE #TempResults_""" + random_number + """ (
    MessageID int,
    ToAddress NVARCHAR(32),
    Body NVARCHAR(MAX),
    StatusID NVARCHAR(32),
    SentTime DATETIME2(7)
)

SELECT @command = '
DECLARE @currentDB NVARCHAR(MAX);
DECLARE @table_name NVARCHAR(MAX);
DECLARE @sql_query NVARCHAR(MAX);

SET @currentDB = ''?''; -- Store the current database name

IF (@currentDB LIKE ''au%'' OR @currentDB LIKE ''ar%'') AND @currentDB NOT LIKE ''auron_sms'' AND @currentDB NOT LIKE ''Auintegration'' AND @currentDB NOT LIKE ''AuSmsServer-gw8'' AND @currentDB NOT LIKE ''ArchAuSmsServer-gw8'' 
BEGIN 
    USE [?]
    IF (LOWER(LEFT(@currentDB, 2)) = ''ar'')
        SET @table_name = ''ArchMessages''
    ELSE
        SET @table_name = ''Messages''

    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = @table_name AND COLUMN_NAME = ''OriginalID'')
        BEGIN
            SET @sql_query = 
                ''INSERT INTO #TempResults_""" + random_number + """ (MessageID, ToAddress, SentTime, Body, StatusID) '' +
                ''SELECT MessageID, ToAddress, SentTime, Body, StatusID '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a WITH (NOLOCK)'' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.OriginalID = b.MessageID '' +
                ''WHERE b.ToAddress LIKE ''''"""+"""%"""+mobile_number+"""%"""+"""'''';''

            EXEC sp_executesql @sql_query
        END
    ELSE
        BEGIN
            SET @sql_query = 
                ''INSERT INTO #TempResults_""" + random_number + """ (MessageID, ToAddress, SentTime, Body, StatusID) '' +
                ''SELECT MessageID, ToAddress, SentTime, Body, StatusID '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a WITH (NOLOCK)'' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.id = b.MessageID '' +
                ''WHERE b.ToAddress LIKE ''''"""+"""%"""+mobile_number+"""%"""+"""'''';''

            EXEC sp_executesql @sql_query
        END
END'

EXEC sp_MSforeachdb @command

SELECT * FROM #TempResults_""" + random_number + """

DROP TABLE #TempResults_""" + random_number + """
            """
        )

        results = db.execute(query).fetchall()
        return set_db_result_to_json(results, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing SQL query: {str(e)}"
        )


@router.post("/file/excel")
def get_excel_file(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_and_normal_user)],
    sms_list: list[dict],
):
    file_name = create_excel_file(sms_list)

    file_path = os.getcwd() + "\\excel\\" + file_name

    return FileResponse(path=file_path, filename=file_name, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def create_excel_file(sms_list):
    random_number = str(random.randint(1, 10000000))
    file_name = random_number + "_excel.xlsx"

    workbook = xlsxwriter.Workbook(os.getcwd() + "/excel/" + file_name)
    worksheet = workbook.add_worksheet()

    row = 0

    worksheet.write(row, 0, "MessageID")
    worksheet.write(row, 1, "ToAddress")
    worksheet.write(row, 2, "Body")
    worksheet.write(row, 3, "StatusID")
    worksheet.write(row, 4, "SentTime")

    row += 1

    for sms in sms_list :
        worksheet.write(row, 0, sms["MessageID"])
        worksheet.write(row, 1, sms["ToAddress"])
        worksheet.write(row, 2, sms["Body"])
        worksheet.write(row, 3, sms["StatusID"])
        worksheet.write(row, 4, sms["SentTime"])
        row += 1
        
    workbook.close()

    return file_name


@router.post("/file/pdf")
def export_pdf(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_and_normal_user)],
    content: dict
):
    obj = {
        "MessageID": str(content["MessageID"]),
        "ToAddress": content["ToAddress"],
        "Body": content["Body"],
        "StatusID": content["StatusID"],
        "SentTime": content["SentTime"]
    }

    CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
    PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
    REPORTS_DIR = os.path.join(PARENT_DIR, 'reports')

    random_number = str(random.randint(1, 10000000))
    file_name = random_number + "_sms_report.pdf"
    
    input_file = os.path.join(REPORTS_DIR, 'auron-pdf.jrxml')
    output_file = os.path.join(REPORTS_DIR, file_name)

    pyreportjasper = PyReportJasper()
    pyreportjasper.config(
        input_file,
        output_file,
        output_formats=["pdf"],
        parameters=obj
    )
    pyreportjasper.process_report()
    return FileResponse(output_file, filename=file_name, media_type="application/pdf")

