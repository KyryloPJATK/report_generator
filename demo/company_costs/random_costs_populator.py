import sqlite3
import random

from datetime import date, timedelta

cost_types = [
    "Salaries",
    "Marketing",
    "Stock Investments",
    "Renting",
    "Reinvestment"
]


def populate_cost_types():
    conn = sqlite3.connect('main_db.db')
    cursor = conn.cursor()
    values_fmt = []
    for idx, cost_type in enumerate(cost_types):
        values_fmt.append(f"( {idx}, '{cost_type}' ) ")
    cursor.execute("INSERT INTO services VALUES " + ",".join(values_fmt))
    conn.commit()
    cursor.close()
    conn.close()


def populate_costs():
    conn = sqlite3.connect('main_db.db')
    cursor = conn.cursor()

    start_date = date(2023, 1, 1)
    end_date = date(2023, 12, 31)
    delta = timedelta(days=1)

    values_fmt = []
    while start_date <= end_date:
        for cost_type_id in range(len(cost_types)):
            cost_val = random.randint(100, 300)
            values_fmt.append(f"""( {cost_type_id}, {cost_val}, '{start_date.strftime('%Y-%m-%d')}')""")
        start_date += delta
    cursor.execute("INSERT INTO company_spendings VALUES " + ",".join(values_fmt))
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    # populate_cost_types()
    populate_costs()
