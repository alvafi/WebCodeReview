import sys
import backend.scrapper as scrapper
from fastapi import FastAPI, HTTPException
from loguru import logger
from datetime import datetime
from dotenv import load_dotenv
import backend.db_operations as db_operations

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

@app.get('/scrap_data')
def scrap_data():
    try:
        logger.debug(SCRAPPING_START)

        all_performances = scrapper.scrap_data()

        if all_performances is None:
            raise HTTPException(500, SCRAPPING_EXCEPTION)

        logger.debug(str.format(SCRAPPING_END_SUCCESSFULLY, all_performances))
        logger.debug(LOAD_DB_START)

        db_operations.load_data_to_db(all_performances)

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
        return db_operations.get_data_from_db(start_date, end_date)
    except Exception as inst:
        logger.error(inst)
        raise HTTPException(500, GET_DATA_EXCEPTION)
    
@app.get('/seats_cost')
def number_seats():
    try:
        return db_operations.get_seats_cost()
    except Exception as inst:
        logger.error(inst)
        raise HTTPException(500, GET_DATA_EXCEPTION)