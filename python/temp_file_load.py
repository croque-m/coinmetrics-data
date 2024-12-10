from pathlib import Path

import pandas as pd

from create_csv import COLUMN_ORDER_WITH_TICKER_AND_TIME
from sql_utils import parse_value, execute_query_direct

UPDATE_CSV_FOLDER = Path(__file__).parent.parent / 'csv3'


INSERT_INTO = "insert into update_table {} values {};"


def make_insert_into_statement(frame):
    columns = ",".join([x if x.isalnum() else f'"{x}"' for x in frame.columns]).join("()")
    values = ""
    for line in frame.to_csv(index=False, header=False).split("\n")[:-1]:
        if not line.strip():
            continue
        values += ",".join(map(parse_value, line.split(","))).join("()")
        values += ","
    values = values[:-1]

    return INSERT_INTO.format(columns, values)


def main():
    for path in UPDATE_CSV_FOLDER.glob("*.csv"):
        print(f"Copying {path.name}")
        try:
            frame: pd.DataFrame = pd.read_csv(path).rename(columns={"asset": "ticker"})
        except pd.errors.EmptyDataError as e:
            print(f"Empty File: {path}")
            continue

        frame = frame[[x for x in frame.columns if x in COLUMN_ORDER_WITH_TICKER_AND_TIME]]
        query = make_insert_into_statement(frame)
        execute_query_direct(query)


if __name__ == '__main__':
    main()
