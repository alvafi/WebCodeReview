import os
import psycopg2

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