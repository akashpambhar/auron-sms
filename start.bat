@echo off
cd backend
call env\Scripts\activate
uvicorn main:app --reload
