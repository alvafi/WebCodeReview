import sys
import psycopg2
import backend.scrapper as scrapper
from fastapi import FastAPI, HTTPException
from loguru import logger
from datetime import datetime

logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>")
app = FastAPI()

def get_connection():
    return psycopg2.connect(
        host='postgres',
        database='DB',
        user='USER',
        password='PASSWORD',
        port='5432'
    )

def load_data_to_db(data):
    conn_details = get_connection()

    cursor = conn_details.cursor()

    delete_sql = '''DELETE FROM performances'''
    cursor.execute(delete_sql)
    cursor.executemany("INSERT INTO performances(name, date) VALUES (%s, %s)", data)

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

@app.get('/scrap_data')
def scrap_data():
    try:
        logger.debug('Начинаем скраппинг данных')

        all_performances = scrapper.scrap_data()

        if all_performances is None:
            raise HTTPException(500, 'Возникла проблема при скраппинге данных с сайта')

        logger.debug(str.format('Скраппинг успешно завершен. Содержимое: {0}', all_performances))
        logger.debug('Сохраняем полученные данные в БД')

        load_data_to_db(all_performances)

        logger.debug('Данные успешно загружены в БД')

        return 'Данные успешно загружены в БД' + f' кол-во записей: {len(all_performances)}'
    except Exception as inst:
        logger.error(inst)
        raise HTTPException(500, 'Возникла проблема при скраппинге данных с сайта')

@app.get('/performances')
def performances(
    start_date: datetime = None,
    end_date: datetime = None
):
    try:
        return get_data_from_db(start_date, end_date)
    except Exception as inst:
        logger.error(inst)
        raise HTTPException(500, 'Возникла проблема при получении данных из БД')