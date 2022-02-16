import sqlite3
from sqlite3 import Error
from unicodedata import name

def initialize_database(db_file):
    sql_create_users_table = """CREATE TABLE IF NOT EXISTS users (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL UNIQUE
                                );"""
    
    sql_create_scores_table =    """CREATE TABLE IF NOT EXISTS scores (
                                        id integer PRIMARY KEY,
                                        score integer NOT NULL,
                                        puzzle_id integer NOT NULL,
                                        user_id integer NOT NULL
                                    );"""
    sql_create_scores_puzzle_id_index =  """CREATE INDEX 
                                            IF NOT EXISTS scores_puzzle_id_idx
                                            ON scores(puzzle_id);"""        
    conn = create_connection(db_file)

    if conn is not None:
        execute_sql(conn, sql_create_users_table)
        execute_sql(conn, sql_create_scores_table)
        execute_sql(conn, sql_create_scores_puzzle_id_index)

        conn.close()
    else:
        print("Error! cannot create the database connection")

def insert_user(db_file, name):
    conn = create_connection(db_file)
    sql =    """INSERT INTO users(name) VALUES(?);"""

    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, (name,))
        conn.commit()
    else:
        print("Error! cannot create the database connection")

    conn.close()

    return cur.lastrowid

def add_score(db_file, user_id, puzzle_id, score):
    conn = create_connection(db_file)
    sql =    """INSERT INTO scores(score, puzzle_id, user_id) VALUES(?, ?, ?);"""

    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, (score, puzzle_id, user_id))
        conn.commit()
    else:
        print("Error! cannot create the database connection")

    conn.close()

    return cur.lastrowid

def select_user_id(db_file, name):
    conn = create_connection(db_file)
    sql = "SELECT id FROM users WHERE name=?"
    cur = conn.cursor()
    cur.execute(sql, (name,))
    rows = cur.fetchall()

    conn.close()
    print(rows)
    if len(rows) == 0:
        print("None")
        return None
    else:
        print(rows[0][0])
        return rows[0][0]
    
def select_user_score(db_file, user_id, puzzle_id):
    conn = create_connection(db_file)
    sql = "SELECT score FROM scores WHERE (user_id=? and puzzle_id=?)"
    cur = conn.cursor()
    cur.execute(sql, (user_id, puzzle_id))
    rows = cur.fetchall()

    conn.close()
    print("SCORES QUERY")
    print(rows)
    if len(rows) == 0:
        print("None")
        return None
    else:
        print(rows[0][0])
        return rows[0][0]

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def execute_sql(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
    