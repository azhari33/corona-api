from http import HTTPStatus

from bs4 import BeautifulSoup
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

# api module
from api import Api

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/summary")
def summary_data():
    """Summary all data by case
    :return: dict
    """
    _data = Api()
    return JSONResponse({
        'status': HTTPStatus.OK,
        'data': _data.fetch_summary_data()},
        status_code=HTTPStatus.OK)


@app.get("/")
def default_data():
    """Default data display by country
    :return: dict
    """
    _data = Api()
    return JSONResponse({
        'status': HTTPStatus.OK,
        'data': _data.fetch_current_data()},
        status_code=HTTPStatus.OK)


@app.get("/now")
def current_data():
    """Get current data based on current date
    :return: dict
    """
    _data = Api()
    return JSONResponse({
        'status': HTTPStatus.OK,
        'data': _data.fetch_current_data()},
        status_code=HTTPStatus.OK)


@app.get("/yesterday")
def yesterday_data():
    """Get all yesterday data
    :return: dict
    """
    _data = Api()
    return JSONResponse({
        'status': HTTPStatus.OK,
        'data': _data.fetch_yesterday_data()},
        status_code=HTTPStatus.OK)
