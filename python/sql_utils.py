import re
import psycopg2

CONNECTION_URL = 'postgresql://cm_data:cm_data@localhost:5433/cm_data'

float_pat = re.compile(r'^\d+\.?\d*$')
single_quote_pat = re.compile(r"'")

# TODO: Used in other project, may be useful here
# timedelta_pat = re.compile(r"^\d+ days (\d\d:\d\d:\d\d)$")

def is_float(s):
    return bool(float_pat.match(s))


def sql_str(s):
    s = single_quote_pat.sub("''", s)
    return f"'{s}'"


def parse_value(s: str):
    if not s:
        return 'NULL'
    elif s.isnumeric() or is_float(s):
        return s
    # TODO: See `timedelta_pat` above
    # elif m := timedelta_pat.match(s):
    #     return f"'{m[1]}'"
    return sql_str(s)


def parse_line(line):
    internal = ', '.join(map(parse_value, line))
    return f"({internal})"


def make_values(lines):
    return ',\n\t'.join(map(parse_line, lines))


def conn_curs():
    conn = psycopg2.connect(CONNECTION_URL)
    return conn, conn.cursor()


def execute_query_direct(sql):
    conn, curs = conn_curs()
    curs.execute(sql)
    conn.commit()
    conn.close()