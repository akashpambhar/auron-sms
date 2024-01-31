from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import SessionLocal
from utils import PaginationParams
from typing import Optional

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
    print(pagination)
    try:
        messages = {
            "items": [],
            "total": 0,
            "paginator": pagination
        }

        query = text(
            """
DECLARE @command NVARCHAR(MAX)

CREATE TABLE #TempResults_OneDay (
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
                ''INSERT INTO #TempResults_OneDay (ToAddress, Body, StatusID, SentTime) '' +
                ''SELECT ToAddress, Body, StatusID, SentTime '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a '' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.OriginalID = b.MessageID '' +''where a.SentTime BETWEEN DATEADD(DAY, -1, GETDATE()) AND GETDATE();''

            EXEC sp_executesql @sql_query
        END
    ELSE
        BEGIN
            SET @sql_query = 
                ''INSERT INTO #TempResults_OneDay (ToAddress, Body, StatusID, SentTime) '' +
                ''SELECT ToAddress, Body, StatusID, SentTime '' +
                ''FROM '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + '' a '' +
                ''INNER JOIN '' + QUOTENAME(@currentDB) + ''.dbo.'' + @table_name + ''_Sms b '' +
                ''ON a.id = b.MessageID '' + ''where a.SentTime BETWEEN DATEADD(DAY, -1, GETDATE()) AND GETDATE();''

            EXEC sp_executesql @sql_query
        END
END'

EXEC sp_MSforeachdb @command

DECLARE @TotalCount BIGINT;
SET @TotalCount = (SELECT COUNT(*) FROM #TempResults_OneDay);

SELECT *, @TotalCount As TotalCount FROM #TempResults_OneDay
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
    
DROP TABLE #TempResults_OneDay
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


@router.get("/phone/{mobile_number}")
async def get_all_sms_by_phone_number(
    mobile_number: str, 
    pagination: PaginationParams.PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    print(mobile_number)
    try:
        messages = {
            "items": [],
            "total": 0,
            "paginator": pagination
        }

        query = text(
            """
DECLARE @command NVARCHAR(MAX)

CREATE TABLE #TempResults (
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
                ''INSERT INTO #TempResults (ToAddress, SentTime, Body, StatusID) '' +
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
                ''INSERT INTO #TempResults (ToAddress, SentTime, Body, StatusID) '' +
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
SET @TotalCount = (SELECT COUNT(*) FROM #TempResults);

SELECT *, @TotalCount As TotalCount FROM #TempResults
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

DROP TABLE #TempResults
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





