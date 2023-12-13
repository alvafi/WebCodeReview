# Скраппер постановок с сайта чайковского театра драмы и комедии

## Описание
Проект собирает данные с сайта [чайковского театра драмы и комедии](https://perm.kassy.ru/widget/20-1/events/) и загружает в БД. Дальше можно найти постановки, котрые проходят в определенны даты. 

## Инструменты
FastAPI, Vvicorn, Playwright, Docker compose, PostgreSQL

## Запуск
1. `sh ./build.sh` - сборка проекта в контейнер и запуск проекта
2. Для работы с проектом необходимо перейти в браузере по адресу http://127.0.0.1:8000

## Работа с проектом
1. `/scrap_data` - собирает данные с сайта и загружает в БД
2. `/performances?start_date=2023-12-06+00:00:00&end_date=2024-01-06+00:00:00` - ищет данные в БД, которые попадают в заданный интервал времени. Параметры `start_date` и `end_date` можно не указывать, тогда вернутся все данные из БД 
3. `/seats_cost` - возвращает постановки, на которые остались билеты