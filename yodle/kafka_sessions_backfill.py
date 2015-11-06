#!/usr/bin/python3

import psycopg2
import psycopg2.extras
from time import sleep, time


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


def getDictCursorToDBAndPrint(dbname, user, host, password):
    start_time = time()    
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (dbname, user, host, password))
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    connect_time = time()
    print("%.3f seconds | Connected to database %s at %s as %s" % (connect_time - start_time, dbname, host, user))
    return (conn, cur)

def getTableRows(cursor, table):
    cursor.execute("SELECT count(*) from %s" % table)
    result = cursor.fetchone()
    count = result['count']
    return count

def getTableRowsAndPrint(cursor, table):
    pre_time = time()
    count = getTableRows(cursor, table)
    post_time = time()
    print("%.3f seconds | Counted table %s to contain %d rows" % (post_time - pre_time, table, count))
    return count

def moveSessionIdsFromTableToQueueTableAndPrint(cursor, offset, limit):
    insert_start_time = time()
    cursor.execute("INSERT INTO %s (session_id) SELECT id FROM %s ORDER BY id asc offset %d limit %d" % (QUEUE_TABLE, SESSIONS_TABLE, offset, limit))
    insert_end_time = time()
    print("%.3f seconds | Finished moving sessions %d-%d" % (insert_end_time - insert_start_time, offset, offset+limit))
 
def moveSessionIdsFromTableToQueueInChunksAndPrint(cursor, chunk_size, total_size):
    current_index = 0
    while(current_index * chunk_size < total_size):
        moveSessionIdsFromTableToQueueTableAndPrint(cursor,
                                                    current_index * chunk_size,
                                                    getNextMaxChunkIndex(chunk_size, total_size, current_index))
        current_index += 1

def getNextMaxChunkIndex(limit_per_chunk, total_size, current_index):
    return min(limit_per_chunk, total_size - (current_index) * limit_per_chunk)

def emptyTable(cursor, table):
    cursor.execute("DELETE FROM %s *" % table)

# http://stackoverflow.com/questions/14471179/find-duplicate-rows-with-postgresql
def getDuplicatesAndPrint(cursor, table, field):
    pre_time = time()
    sql = """SELECT * FROM (SELECT id,
             ROW_NUMBER() OVER(PARTITION BY %s ORDER BY id asc) AS Row
             FROM %s
             ) dups
             where 
             dups.Row > 1
             """ % (field, table)
    cursor.execute(sql)
    duplicates = cursor.fetchall()
    post_time = time()
    if duplicates:
        message = "%.3f seconds | Duplicates found" % (post_time - pre_time) 
    else:
        message = "%.3f seconds | No duplicates found" % (post_time - pre_time)
    print(message)
    return bool(duplicates)

def main():
    conn, cur = getDictCursorToDBAndPrint(dbname=CURRENT_DATABASE,
                                          user=CURRENT_USER,
                                          host=CURRENT_HOST,
                                          password=CURRENT_PASSWORD)    
    # emptyTable(cur, QUEUE_TABLE)
    sessions_total_count = getTableRowsAndPrint(cur, SESSIONS_TABLE)
    getTableRowsAndPrint(cur, QUEUE_TABLE)
    moveSessionIdsFromTableToQueueInChunksAndPrint(cur, QUERY_LIMIT, sessions_total_count)
    conn.commit()
    getTableRowsAndPrint(cur, QUEUE_TABLE)
    getDuplicatesAndPrint(cur, QUEUE_TABLE, "session_id") # Sanity-check

if __name__ == "__main__":
    main()

###############################################################################################
# http://stackoverflow.com/questions/15938180/sql-check-if-entry-in-table-a-exists-in-table-b #
# Find subsets between two tables                                                            #
# SELECT *                                                                                   #
# FROM   B                                                                                   #
# WHERE  NOT EXISTS (SELECT 1                                                                #
#                    FROM   A                                                                #
#                    WHERE  A.ID = B.ID)                                                      #
###############################################################################################
