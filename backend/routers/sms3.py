import re
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
# from pymemcache.client import base
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
from utils.Utils import get_list_from_env

router = APIRouter(prefix="/d3/sms", tags=["sms3"])

# mc = base.Client((os.getenv("MC_SERVER"), 11211))

def cache_get_all_sms(
    db: Session = next(get_db())
):
    # if mc.get("message_list3") is not None:
    #     return
    try:
        query = text("EXEC dbo.GetAllMessages :dbname")
        
        results = db.execute(query, {"dbname": os.getenv('LIVE_DB_SERVER3')}).fetchall()

        json_messages = json.dumps(set_db_result_to_json(results, RoleSchema.Role(role_id=1, role_name='admin')), default=str)
        # mc.set("message_list3", json_messages)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing SQL query: {str(e)}"
        )

def mask_otp_in_body(body_text):
    if 'otp' in body_text.lower() or 'verification code' in body_text.lower() or 'apple pay' in body_text.lower() or 'مز التحقق' in body_text.lower() :
        body_text = re.sub(r'\b\d{4}\b|\b\d{6}\b', lambda x: '*' * len(x.group()), body_text, flags=re.IGNORECASE)
    return body_text

def set_db_result_to_json(results, current_active_user):
    count = {
        "total" : 0,
        "received" : 0,
        "sent" : 0
    }

    messages = {
        "items": [],
        "status": count
    }

    if results != []:
        if(current_active_user.role_id == 1):
            for result in results:
                messages["items"].append(
                {
                    "MessageID": result[0],
                    "ToAddress": result[1],
                    "Body": result[2],
                    "StatusID": result[3],
                    "SentTime": result[4]
                })

                if 'received' in result[3].lower() :
                    count["received"] = count["received"] + 1
                else :
                    count["sent"] = count["sent"] + 1
                
        else :
            for result in results:
                messages["items"].append(
                {
                    "MessageID": result[0],
                    "ToAddress": result[1],
                    "Body": mask_otp_in_body(result[2]),
                    "StatusID": result[3],
                    "SentTime": result[4]
                })

                if 'received' in result[3].lower() :
                    count["received"] = count["received"] + 1
                else :
                    count["sent"] = count["sent"] + 1

    count["total"] = count["received"] + count["sent"]

    messages["status"] = count

    return messages

@router.get("")
def get_all_sms(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_and_normal_user)],
    db: Session = Depends(get_db)
):
    try:
        query = text("EXEC dbo.GetAllMessages :dbname")
        
        results = db.execute(query, {"dbname": os.getenv('LIVE_DB_SERVER3')}).fetchall()

        messages = set_db_result_to_json(results, current_user)
        # mc.set("message_list3", json_messages)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing SQL query: {str(e)}"
        )
    return messages

databases = get_list_from_env('ARCHIVE_DB_LIST_SERVER3')

def run_query(db_con, db_name, mobile_number, start_date, end_date):
    query = text("EXEC dbo.GetMessagesByMobileNumber :dbName, :mobileNumber, :startDate, :endDate;")
    results = db_con.execute(query, {"dbName": db_name, "mobileNumber": mobile_number, 'startDate': start_date, 'endDate': end_date}).fetchall()

    return results

@router.get("/phone")
def get_all_sms_by_phone_number(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_and_normal_user)],
    mobile_number: str = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    try:
        results = []

        print(databases)

        for db_name in databases:
            db_results = run_query(db, db_name, mobile_number, start_date, end_date)
            results.extend(db_results)

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

    file_path = os.path.join(os.getcwd(), "excel", file_name)

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

