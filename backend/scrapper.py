import datetime, os
from loguru import logger
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

SCRAP_URL = os.getenv('SCRAP_URL')

def convert_date(date: str): #Функция конвертирует строковое представление даты вида '6 декабря 2023 13:00' в тип datetime
    splitted = date.split(' ')

    day = splitted[0]
    month = None
    month_text = splitted[1]
    year = splitted[2]
    hhmm = splitted[3]

    if month_text == 'января':
        month = 1
    elif month_text == 'февраля':
        month = 2
    elif month_text == 'марта':
        month = 3
    elif month_text == 'апреля':
        month = 4
    elif month_text == 'мая':
        month = 5
    elif month_text == 'июня':
        month = 6
    elif month_text == 'июля':
        month = 7
    elif month_text == 'августа':
        month = 8
    elif month_text == 'сентября':
        month = 9
    elif month_text == 'октября':
        month = 10
    elif month_text == 'ноября':
        month = 11
    elif month_text == 'декабря':
        month = 12

    return datetime.datetime.strptime(f'{month}-{day}-{year} {hhmm}:00', '%m-%d-%Y %H:%M:%S')


def scrap_data():
    all_performances = None

    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SCRAP_URL)

        try:
            html = page.content()

            bsObj = BeautifulSoup(html, 'html.parser')
            found_perfomance = bsObj.find_all('div', {'class': 'list-group-item'})
            all_performances = []
            for i in found_perfomance:
                name = ' '.join(i.find('a', {'class': 'gray'}).text.split())
                date = ' '.join(i.find('p', {'class': 'list-group-item-text date'}).text.split()[:3])
                time = i.find('p', {'class': 'list-group-item-text date'}).text.split()[3]
                seats = ' '.join(i.find('div', {'class': 'd-flex justify-content-between align-items-center price'}).text.split()[:3])
                if seats == 'Билеты в наличии:':
                    cost = i.find('div', {'class': 'd-flex justify-content-between align-items-center price'}).text.split()[3]
                    all_performances.append((name, convert_date(f'{date} {time}'), seats, cost))
                else:
                    all_performances.append((name, convert_date(f'{date} {time}'), seats, 0))
        except Exception as inst:
            logger.error(inst)
        finally:
            browser.close()
            return all_performances