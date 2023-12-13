import sys
import os
import psycopg2
import backend.scrapper as scrapper
from fastapi import FastAPI, HTTPException
from loguru import logger
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SCRAPPING_START = 'Начинаем скраппинг данных'
SCRAPPING_END_SUCCESSFULLY = 'Скраппинг успешно завершен. Содержимое: {0}'
SCRAPPING_EXCEPTION = 'Возникла проблема при скраппинге данных с сайта'
LOAD_DB_START = 'Сохраняем полученные данные в БД'
DATA_LOADED_DB_SUCCESSFULLY = 'Данные успешно загружены в БД'
GET_DATA_EXCEPTION = 'Возникла проблема при получении данных из БД'

logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>")
app = FastAPI()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=os.getenv('POSTGRES_PORT')
    )

def load_data_to_db(data):
    conn_details = get_connection()

    cursor = conn_details.cursor()

    delete_sql = '''DELETE FROM performances'''
    cursor.execute(delete_sql)
    cursor.executemany("INSERT INTO performances(name, date, seats, cost) VALUES (%s, %s, %s, %s)", data)

    conn_details.commit()
    conn_details.close()

def get_data_from_db(start_date, end_date):
    conn_details = get_connection()

    cursor = conn_details.cursor()

    conditions = 'where '

    if start_date is None and end_date is None:
        conditions += '1=1'
    elif start_date is not None and end_date is not None:
        conditions += f"p.\"date\" between '{start_date}' and '{end_date}'"
    elif start_date is not None:
        conditions += f"p.\"date\" >= '{start_date}'"
    elif end_date is not None:
        conditions += f"p.\"date\" <= '{end_date}'"

    select_sql = f'''select * from performances p {conditions}'''

    cursor.execute(select_sql)
    result = cursor.fetchall()

    conn_details.commit()
    conn_details.close()

    return result

def get_seats_cost():
    conn_details = get_connection()

    cursor = conn_details.cursor()

    cursor.execute('''SELECT * FROM performances WHERE cost != 0''')
    result = cursor.fetchall()

    conn_details.commit()
    conn_details.close()

    return result

@app.get('/scrap_data')
def scrap_data():
    try:
        logger.debug(SCRAPPING_START)

        all_performances = scrapper.scrap_data()

        if all_performances is None:
            raise HTTPException(500, SCRAPPING_EXCEPTION)

        logger.debug(str.format(SCRAPPING_END_SUCCESSFULLY, all_performances))
        logger.debug(LOAD_DB_START)

        load_data_to_db(all_performances)

        logger.debug(DATA_LOADED_DB_SUCCESSFULLY)

        return DATA_LOADED_DB_SUCCESSFULLY + f' кол-во записей: {len(all_performances)}'
    except Exception as inst:
        logger.error(inst)
        raise HTTPException(500, SCRAPPING_EXCEPTION)

@app.get('/performances')
def performances(
    start_date: datetime = None,
    end_date: datetime = None
):
    try:
        return get_data_from_db(start_date, end_date)
    except Exception as inst:
        logger.error(inst)
        raise HTTPException(500, GET_DATA_EXCEPTION)
    
@app.get('/seats_cost')
def number_seats():
    try:
        return get_seats_cost()
    except Exception as inst:
        logger.error(inst)
        raise HTTPException(500, GET_DATA_EXCEPTION)