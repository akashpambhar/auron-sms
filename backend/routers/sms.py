import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import SessionLocal
from utils import PaginationParams
from typing import Optional
import random
import xlsxwriter
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/sms", tags=["sms"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def get_all_sms(
    pagination: PaginationParams.PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    random_number = str(random.randint(1, 10000000))

    try:
        messages = {
            "items": [],
            "total": 0,
            "paginator": pagination
        }

        query = text(
            """
DECLARE @command NVARCHAR(MAX)

CREATE TABLE #TempResults_""" + random_number + """ (
    ToAddress NVARCHAR(32),
    Body NVARCHAR(MAX),
    StatusID NVARCHAR(32),
	SentTime DATETIME2(7),
    TotalCount BIGINT
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
                ''INSERT INTO #TempResults_""" + random_number + """ (ToAddress, Body, StatusID, SentTime) '' +
                ''SELECT ToAddress, Body, StatusID, SentTime '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a '' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.OriginalID = b.MessageID '' +''WHERE a.SentTime BETWEEN DATEADD(HOUR, -1, GETDATE()) AND GETDATE();''

            EXEC sp_executesql @sql_query
        END
    ELSE
        BEGIN
            SET @sql_query = 
                ''INSERT INTO #TempResults_""" + random_number + """ (ToAddress, Body, StatusID, SentTime) '' +
                ''SELECT ToAddress, Body, StatusID, SentTime '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a '' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.id = b.MessageID '' + ''WHERE a.SentTime BETWEEN DATEADD(HOUR, -1, GETDATE()) AND GETDATE();''

            EXEC sp_executesql @sql_query
        END
END'

EXEC sp_MSforeachdb @command

DECLARE @TotalCount BIGINT;
SET @TotalCount = (SELECT COUNT(*) FROM #TempResults_""" + random_number + """);

SELECT *, @TotalCount As TotalCount FROM #TempResults_""" + random_number + """
ORDER BY """
+ pagination.sort_by
+ " "
+ pagination.sort_order
+ """
OFFSET """
+ str((pagination.page - 1) * pagination.page_size)
+ """ ROWS
FETCH NEXT """
+ str(pagination.page_size)
+ """ ROWS ONLY
    
DROP TABLE #TempResults_""" + random_number + """
        """
        )

        print(query)
        results = db.execute(query).fetchall()

        print(results)

        messages["items"] = [
            {
                "ToAddress": result[0],
                "Body": result[1],
                "StatusID": result[2],
                "SentTime": result[3],
            }
            for result in results
        ]

        messages["total"] = results[0][5]
       
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing SQL query: {str(e)}"
        )


@router.get("/phone/{mobile_number}")
async def get_all_sms_by_phone_number(
    mobile_number: str, 
    pagination: PaginationParams.PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    print(mobile_number)
    random_number = str(random.randint(1, 10000000))
    try:
        messages = {
            "items": [],
            "total": 0,
            "paginator": pagination
        }

        query = text(
            """
DECLARE @command NVARCHAR(MAX)

CREATE TABLE #TempResults_""" + random_number + """ (
    ToAddress NVARCHAR(32),
    Body NVARCHAR(MAX),
    StatusID NVARCHAR(32),
    SentTime DATETIME2(7),
    TotalCount BIGINT
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
                ''INSERT INTO #TempResults_""" + random_number + """ (ToAddress, SentTime, Body, StatusID) '' +
                ''SELECT ToAddress, SentTime, Body, StatusID '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a '' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.OriginalID = b.MessageID '' +
                ''WHERE b.ToAddress LIKE ''''"""+"""%"""+mobile_number+"""%"""+"""'''';''

            EXEC sp_executesql @sql_query
        END
    ELSE
        BEGIN
            SET @sql_query = 
                ''INSERT INTO #TempResults_""" + random_number + """ (ToAddress, SentTime, Body, StatusID) '' +
                ''SELECT ToAddress, SentTime, Body, StatusID '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a '' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.id = b.MessageID '' +
                ''WHERE b.ToAddress LIKE ''''"""+"""%"""+mobile_number+"""%"""+"""'''';''

            EXEC sp_executesql @sql_query
        END
END'

EXEC sp_MSforeachdb @command

DECLARE @TotalCount BIGINT;
SET @TotalCount = (SELECT COUNT(*) FROM #TempResults_""" + random_number + """);

SELECT *, @TotalCount As TotalCount FROM #TempResults_""" + random_number + """
ORDER BY """
+ pagination.sort_by
+ " "
+ pagination.sort_order
+ """
OFFSET """
+ str((pagination.page - 1) * pagination.page_size)
+ """ ROWS
FETCH NEXT """
+ str(pagination.page_size)
+ """ ROWS ONLY

DROP TABLE #TempResults_""" + random_number + """
            """
        )

        results = db.execute(query).fetchall()
        messages["items"] = [
            {
                "ToAddress": result[0],
                "Body": result[1],
                "StatusID": result[2],
                "SentTime": result[3],
            }
            for result in results
        ]

        messages["total"] = results[0][5]
        
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing SQL query: {str(e)}"
        )


@router.get("/file/excel")
async def get_excel_file(
    pagination: PaginationParams.PaginationParams = Depends(),
    db: Session = Depends(get_db),
    mobileNumber: Optional[str] = Query(None),
):
    if(mobileNumber is not None):
        sms_list = await get_all_sms_by_phone_number(mobile_number=mobileNumber, pagination=pagination, db=db)
    else:
        sms_list = await get_all_sms(pagination=pagination, db=db)
    
    file_name = create_excel_file(sms_list["items"])

    file_path = os.getcwd() + "\\excel\\" + file_name

    return FileResponse(path=file_path, filename=file_name, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def create_excel_file(sms_list):
    random_number = str(random.randint(1, 10000000))
    file_name = random_number + "_excel.xlsx"

    workbook = xlsxwriter.Workbook(os.getcwd() + "/excel/" + file_name)
    worksheet = workbook.add_worksheet()

    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss.000'})
    
    row = 0

    worksheet.write(row, 0, "ToAddress")
    worksheet.write(row, 1, "Body")
    worksheet.write(row, 2, "StatusID")
    worksheet.write(row, 3, "SentTime")

    row += 1

    for sms in sms_list :
        worksheet.write(row, 0, sms["ToAddress"])
        worksheet.write(row, 1, sms["Body"])
        worksheet.write(row, 2, sms["StatusID"])
        sent_time = datetime.datetime.strptime(str(sms["SentTime"]), '%Y-%m-%d %H:%M:%S.%f')
        worksheet.write(row, 3, sent_time, date_format)
        row += 1
        
    workbook.close()

    return file_name