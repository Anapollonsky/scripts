#!/usr/bin/python3

import psycopg2
import psycopg2.extras
from datetime import datetime

DEV_HOST = "nyc-devdb1.corp.yodle.com"
QA1_HOST = "qa1-db1.qa1.yodle.com"
QA2_HOST = "qa2-db1.qa2.yodle.com"

SESSIONS_TABLE = "control.session"
QUEUE_TABLE = "mapreduce.session_upload_queue"

CURRENT_HOST = QA1_HOST
CURRENT_DATABASE = "natpal"
CURRENT_USER = "qa"
CURRENT_PASSWORD = "yodleqa"
QUERY_LIMIT = 30000000


def printWithTime(message, query=""):
    time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    message = "%s | %s" % (time, message)
    if query:
        message += " --- {%s}" % query
    print(message)

def getDictCursorToDBAndPrint(dbname, user, host, password):
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (dbname, user, host, password))
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    printWithTime("Connected to database %s at %s as %s" % (dbname, host, user))
    return (conn, cur)

def getTableRowsAndPrint(cursor, table_name):
    sql = "SELECT count(*) from %s" % table_name
    cursor.execute(sql)
    count = cursor.fetchone()['count']
    printWithTime("Counted %s to contain %d rows" % (table_name, count), sql)
    return count

def getMaxIdAndPrint(cursor, table_name):
    sql = "SELECT id from %s ORDER BY id desc limit 1" % table_name
    cursor.execute(sql)
    max_id= cursor.fetchone()['id']
    printWithTime("Found %s to have highest id of %d" % (table_name, max_id), sql)
    return max_id

def moveSessionIdsFromTableToQueueTableAndPrint(cursor, lower_limit, upper_limit):
    sql = "INSERT INTO %s (session_id) SELECT id FROM %s WHERE id > %s AND id <= %s" % (QUEUE_TABLE, SESSIONS_TABLE, lower_limit, upper_limit)
    cursor.execute(sql)
    printWithTime("Finished moving sessions with ids between %d and %d" % (lower_limit, upper_limit), sql)

def moveSessionIdsFromTableToQueueInChunksAndPrint(cursor, chunk_size, total_size):
    current_index = 0
    while(current_index * chunk_size <= total_size):
        moveSessionIdsFromTableToQueueTableAndPrint(cursor,
                                                    current_index * chunk_size,
                                                    min((current_index + 1) * chunk_size, total_size))
        current_index += 1

def emptyTable(cursor, table_name):
    sql = "DELETE FROM %s *" % table_name
    cursor.execute(sql)
    printWithTime("Deleted all rows from table %s" % table_name, sql)

# http://stackoverflow.com/questions/14471179/find-duplicate-rows-with-postgresql
def getDuplicatesAndPrint(cursor, table_name, field):
    sql = """SELECT * FROM (SELECT id, ROW_NUMBER() OVER(PARTITION BY %s ORDER BY id asc) AS Row FROM %s) dups where dups.Row > 1""" % (field, table_name)
    cursor.execute(sql)
    duplicates = cursor.fetchall()
    printWithTime("%d duplicates found" % (len(duplicates)), sql)
    return bool(duplicates)

# http://stackoverflow.com/questions/3640606/find-sql-rows-that-are-not-shared-between-two-tables-with-identical-fields
def getExclusiveItemsBetweenTablesByFields(cursor, tablea, tableb, fielda, fieldb):
    sql = """SELECT %s FROM %s %s WHERE %s NOT IN (SELECT %s FROM %s %s)""" % (fielda, tablea, fielda, fielda, fieldb, tableb, fieldb)
    cursor.execute(sql)
    exclusive_items = cursor.fetchall()
    printWithTime("%d exclusive items found" % (len(exclusive_items)), sql)
    return bool(exclusive_items)

def main():
    conn, cur = getDictCursorToDBAndPrint(dbname=CURRENT_DATABASE,
                                          user=CURRENT_USER,
                                          host=CURRENT_HOST,
                                          password=CURRENT_PASSWORD)
    max_session_id = getMaxIdAndPrint(cur, SESSIONS_TABLE)
    emptyTable(cur, QUEUE_TABLE)
    getTableRowsAndPrint(cur, SESSIONS_TABLE)
    getTableRowsAndPrint(cur, QUEUE_TABLE)
    moveSessionIdsFromTableToQueueInChunksAndPrint(cur, QUERY_LIMIT, max_session_id)
    conn.commit()
    getTableRowsAndPrint(cur, QUEUE_TABLE)
    getDuplicatesAndPrint(cur, QUEUE_TABLE, "session_id") # Sanity-check
    getExclusiveItemsBetweenTablesByFields(cur, SESSIONS_TABLE, QUEUE_TABLE, "id", "session_id") # crazy slow bro

if __name__ == "__main__":
    main()
