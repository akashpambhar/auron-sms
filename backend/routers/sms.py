from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import SessionLocal
from utils import PaginationParams

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
        messages = []

        try:
            query = text(
                """
                DECLARE @command varchar(MAX)
                CREATE TABLE #TempResults (
                    ToAddress varchar(MAX),
                    Body varchar(MAX),
                    StatusID int
                )

                SELECT @command = 'IF (''?'' LIKE ''au%'' OR ''?'' LIKE ''ar%'') AND ''?'' NOT LIKE ''auron_sms''
                BEGIN 
                    USE ? 
                    DECLARE @table_name varchar(MAX)
                    
                    IF (LOWER(LEFT(''?'', 2)) = ''ar'')
                        SET @table_name = ''ArchMessages''
                    ELSE
                        SET @table_name = ''Messages''

                    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = @table_name AND COLUMN_NAME = ''OriginalID'')
                        BEGIN
                            DECLARE @sql_query1 NVARCHAR(MAX)
                            SELECT @sql_query1 = ''INSERT INTO #TempResults (ToAddress, Body, StatusID) '' +
                                ''select ToAddress, Body, StatusID '' +
                                ''from '' + @table_name + '' a '' +
                                ''inner join '' + @table_name + ''_Sms '' + '' b '' +
                                ''on a.OriginalID=b.MessageID ''
                            EXEC sp_executesql @sql_query1
                        END
                    ELSE
                        BEGIN
                            DECLARE @sql_query2 NVARCHAR(MAX)
                            SELECT @sql_query2 = ''INSERT INTO #TempResults (ToAddress, Body, StatusID) '' +
                                ''select ToAddress, Body, StatusID '' +
                                ''from '' + @table_name + '' a '' +
                                ''inner join '' + @table_name + ''_Sms'' + '' b '' +
                                ''on a.id=b.MessageID ''
                            EXEC sp_executesql @sql_query2
                        END
                END'

                EXEC sp_MSforeachdb @command
 
                SELECT * FROM #TempResults
                ORDER BY """ + pagination.sort_by + " " + pagination.sort_order + """
                OFFSET """ + str((pagination.page - 1) * pagination.page_size) + """ ROWS
                FETCH NEXT """ + str(pagination.page_size) + """ ROWS ONLY
                 
                DROP TABLE #TempResults
                """
            )
            results = db.execute(query).fetchall()
            cureent_msg = [
                {
                    "ToAddress": result[0],
                    # "senttime": result[1],
                    "Body": result[1],
                    "StatusID": result[2],
                }
                for result in results
            ]
            if cureent_msg is not None:
                messages = messages + cureent_msg
        except Exception as e:
            print(e)

        return messages
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing SQL query: {str(e)}"
        )


@router.get("/phone/{mobile_number}")
async def get_all_sms_by_phone_number(
    mobile_number: str, db: Session = Depends(get_db)
):
    print(mobile_number)
    try:
        messages = []

        try:
            query = text(
                """
                DECLARE @command varchar(MAX)
                CREATE TABLE #TempResults (
                    ToAddress varchar(MAX),
                    Body varchar(MAX),
                    StatusID int
                )

                SELECT @command = 'IF (''?'' LIKE ''au%'' OR ''?'' LIKE ''ar%'') AND ''?'' NOT LIKE ''auron_sms''
                BEGIN 
                    USE ? 
                    DECLARE @table_name varchar(MAX)
                    
                    IF (LOWER(LEFT(''?'', 2)) = ''ar'')
                        SET @table_name = ''ArchMessages''
                    ELSE
                        SET @table_name = ''Messages''

                    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = @table_name AND COLUMN_NAME = ''OriginalID'')
                        BEGIN
                            DECLARE @sql_query1 NVARCHAR(MAX)
                            SELECT @sql_query1 = ''INSERT INTO #TempResults (ToAddress, Body, StatusID) '' +
                                ''select ToAddress, Body, StatusID '' +
                                ''from '' + @table_name + '' a '' +
                                ''inner join '' + @table_name + ''_Sms '' + '' b '' +
                                ''on a.OriginalID=b.MessageID where ToAddress = """
                + mobile_number
                + """ ''
                            EXEC sp_executesql @sql_query1
                        END
                    ELSE
                        BEGIN
                            DECLARE @sql_query2 NVARCHAR(MAX)
                            SELECT @sql_query2 = ''INSERT INTO #TempResults (ToAddress, Body, StatusID) '' +
                                ''select ToAddress, Body, StatusID '' +
                                ''from '' + @table_name + '' a '' +
                                ''inner join '' + @table_name + ''_Sms'' + '' b '' +
                                ''on a.id=b.MessageID where ToAddress = """
                + mobile_number
                + """ ''
                            EXEC sp_executesql @sql_query2
                        END
                END'

                EXEC sp_MSforeachdb @command
 
                SELECT * FROM #TempResults

                DROP TABLE #TempResults
                """
            )
            results = db.execute(query).fetchall()
            cureent_msg = [
                {
                    "ToAddress": result[0],
                    # "senttime": result[1],
                    "Body": result[1],
                    "StatusID": result[2],
                }
                for result in results
            ]
            if cureent_msg is not None:
                messages = messages + cureent_msg
        except Exception as e:
            print(e)
            # query = text(
            #     f"select ToAddress,senttime, Body,StatusID  from [{all_dbs[i]}].dbo.{table_name} a,[{all_dbs[i]}].dbo.{table_name}_Sms b where a.id=b.MessageID and  ToAddress like :mobile_number order by SentTime desc"
            # )
            # results = db.execute(
            #     query, {"mobile_number": f"%{mobile_number}%"}
            # ).fetchall()
            # cureent_msg = [
            #     {
            #         "ToAddress": result[0],
            #         "senttime": result[1],
            #         "Body": result[2],
            #         "StatusID": result[3],
            #     }
            #     for result in results
            # ]
            # if cureent_msg is not None:
            #     messages = messages + cureent_msg
            # print(all_dbs[i])
            # pass

        return messages
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing SQL query: {str(e)}"
        )


# select ToAddress, Body, StatusID
# from @dbname.dbo.@table_name a, @dbname.dbo.@table_name_Sms b
# where a.id=b.MessageID and  ToAddress like :mobile_number;

# DECLARE @dbname varchar(MAX) = '';
# DECLARE @table_name varchar(MAX) = '';
# DECLARE @rn INT = 1;

# WHILE @dbname IS NOT NULL
# BEGIN
#     SET @dbname = (SELECT name FROM (SELECT name, ROW_NUMBER() OVER (ORDER BY name) rn
#         FROM sys.databases WHERE ((name LIKE 'au%' OR name LIKE 'ar%') AND name <> 'auintegration')) t WHERE rn = @rn);

#     IF @dbname <> '' AND @dbname IS NOT NULL
#         BEGIN
#             IF (LOWER(LEFT(@dbname, 2)) = 'ar')
#                 SET @table_name = 'ArchMessages'
#             ELSE
#                 SET @table_name = 'Messages'

#             DECLARE @SQL NVARCHAR(MAX);
#             SET @SQL = N'USE ' + QUOTENAME(@dbname);
#             PRINT(@SQL);
#             EXECUTE(@SQL);

#             IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = QUOTENAME(@table_name) AND COLUMN_NAME = 'OriginalID')
#                 BEGIN
#                     DECLARE @sql_query1 NVARCHAR(MAX);
#                     SELECT @sql_query1 = 'select ToAddress, Body, StatusID ' +
#                         'from ' + QUOTENAME(@dbname) + '.dbo.' + QUOTENAME(@table_name) + ' a, ' + QUOTENAME(@dbname) + '.dbo.' + QUOTENAME(@table_name + '_Sms') + ' b ' +
#                         'where a.OriginalID=b.MessageID and  ToAddress like 123456789'
#                     EXEC sp_executesql @sql_query1;
#                 END
#             ELSE
#                 BEGIN
#                     DECLARE @sql_query2 NVARCHAR(MAX);
#                     SELECT @sql_query2 = 'select ToAddress, Body, StatusID ' +
#                         'from ' + QUOTENAME(@dbname) + '.dbo.' + QUOTENAME(@table_name) + ' a, ' + QUOTENAME(@dbname) + '.dbo.' + QUOTENAME(@table_name + '_Sms') + ' b ' +
#                         'where a.OriginalID=b.MessageID and  ToAddress like 123456789'
#                     EXEC sp_executesql @sql_query2;
#                 END
#         END
#     SET @rn = @rn + 1;
# END;
