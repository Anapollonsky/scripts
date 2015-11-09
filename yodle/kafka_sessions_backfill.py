#!/usr/bin/python3

import psycopg2
import psycopg2.extras
from time import strftime

DEV_HOST = "nyc-devdb1.corp.yodle.com"
QA1_HOST = "qa1-db1.qa1.yodle.com"
QA2_HOST = "qa2-db1.qa2.yodle.com"

SESSIONS_TABLE = "control.session"
QUEUE_TABLE = "mapreduce.session_upload_queue"

CURRENT_HOST = QA2_HOST
CURRENT_DATABASE = "natpal"
CURRENT_USER = "qa"
CURRENT_PASSWORD = "yodleqa"
QUERY_LIMIT = 30000000


def printWithTime(message):
    print(strftime("%H:%M:%S") + " | " + message)

def getDictCursorToDBAndPrint(dbname, user, host, password):
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (dbname, user, host, password))
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    printWithTime("Connected to database %s at %s as %s" % (dbname, host, user))
    return (conn, cur)

def getTableRows(cursor, table_name):
    cursor.execute("SELECT count(*) from %s" % table_name)
    result = cursor.fetchone()
    count = result['count']
    return count

def getTableRowsAndPrint(cursor, table_name):
    count = getTableRows(cursor, table_name)
    printWithTime("Counted table_name %s to contain %d rows" % (table_name, count))
    return count

def moveSessionIdsFromTableToQueueTableAndPrint(cursor, offset, limit):
    cursor.execute("INSERT INTO %s (session_id) SELECT id FROM %s ORDER BY id asc offset %d limit %d" % (QUEUE_TABLE, SESSIONS_TABLE, offset, limit))
    printWithTime("Finished moving sessions %d-%d" % (offset, offset+limit))

def moveSessionIdsFromTableToQueueInChunksAndPrint(cursor, chunk_size, total_size):
    current_index = 0
    while(current_index * chunk_size < total_size):
        moveSessionIdsFromTableToQueueTableAndPrint(cursor,
                                                    current_index * chunk_size,
                                                    getNextMaxChunkIndex(chunk_size, total_size, current_index))
        current_index += 1

def getNextMaxChunkIndex(limit_per_chunk, total_size, current_index):
    return min(limit_per_chunk, total_size - (current_index) * limit_per_chunk)

def emptyTable(cursor, table_name):
    cursor.execute("DELETE FROM %s *" % table_name)
    printWithTime("Deleted all rows from table %s" % table_name)

# http://stackoverflow.com/questions/14471179/find-duplicate-rows-with-postgresql
def getDuplicatesAndPrint(cursor, table_name, field):
    sql = """SELECT * FROM (SELECT id,
             ROW_NUMBER() OVER(PARTITION BY %s ORDER BY id asc) AS Row
             FROM %s
             ) dups
             where
             dups.Row > 1
             """ % (field, table_name)
    cursor.execute(sql)
    duplicates = cursor.fetchall()
    message = "%d duplicates found" % (len(duplicates))
    printWithTime(message)
    return bool(duplicates)

# http://stackoverflow.com/questions/3640606/find-sql-rows-that-are-not-shared-between-two-tables-with-identical-fields
def getExclusiveItemsBetweenTablesByFields(cursor, tablea, tableb, fielda, fieldb):
    sql = """SELECT %s
             FROM %s %s
             WHERE %s NOT IN (SELECT %s
                              FROM %s %s)""" % (fielda, tablea, fielda, fielda, fieldb, tableb, fieldb)
    cursor.execute(sql)
    exclusive_items = cursor.fetchall()
    message = "%d exclusive items found" % (len(exclusive_items))
    printWithTime(message)
    return bool(exclusive_items)

def main():
    conn, cur = getDictCursorToDBAndPrint(dbname=CURRENT_DATABASE,
                                          user=CURRENT_USER,
                                          host=CURRENT_HOST,
                                          password=CURRENT_PASSWORD)
    emptyTable(cur, QUEUE_TABLE)
    sessions_total_count = getTableRowsAndPrint(cur, SESSIONS_TABLE)
    getTableRowsAndPrint(cur, QUEUE_TABLE)
    moveSessionIdsFromTableToQueueInChunksAndPrint(cur, QUERY_LIMIT, sessions_total_count)
    conn.commit()
    getTableRowsAndPrint(cur, QUEUE_TABLE)
    getDuplicatesAndPrint(cur, QUEUE_TABLE, "session_id") # Sanity-check
    getExclusiveItemsBetweenTablesByFields(cur, SESSIONS_TABLE, QUEUE_TABLE, "id", "session_id")

if __name__ == "__main__":
    main()
