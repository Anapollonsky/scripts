#!/usr/bin/python3

import psycopg2
import psycopg2.extras
import json
import datetime
import requests
import atexit
from time import sleep

TABLE = "control.session"
POST_ENDPOINT_URL = "http://localhost:8080/api/v1/kafka/upload/zack-topic"

def getDictCursorToDB(dbname, user, host, password):
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (dbname, user, host, password))
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    return cur

def convertDatesInDictionaryToString(dictToConvert):
    for key in dictToConvert:
        if (isinstance(dictToConvert[key], datetime.datetime)):
            dictToConvert[key] = str(dictToConvert[key])

def main():
    cur = getDictCursorToDB(dbname="natpal",
                            user="qa",
                            host="nyc-devdb1.corp.yodle.com",
                            password="yodleqa")
    cur.execute("""SELECT * FROM %s""" % TABLE)

    for session in cur:
        sessionid = session["id"]

        convertDatesInDictionaryToString(session)

        message = {"message": json.dumps(session)}

        response = requests.post(POST_ENDPOINT_URL, params=message)
        print(sessionid, response)

if __name__ == "__main__":
    main()
