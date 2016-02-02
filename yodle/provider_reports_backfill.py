#!/usr/bin/python3

import json
import psycopg2
from psycopg2.extras import RealDictCursor
from kafka import *
from datetime import datetime
from time import sleep

SQL_HOST_DEV = "nyc-devdb1.corp.yodle.com"
SQL_HOST_QA1 = "qa1-db1.qa1.yodle.com"
SQL_HOST_QA2 = "qa2-db1.qa2.yodle.com"

# KAFKA_HOSTS = ["dev-kafka-events1.nyc.dev.yodle.com:9092", "dev-kafka-events2.nyc.dev.yodle.com:9092"]
KAFKA_HOSTS = 'dev-kafka-events1.nyc.dev.yodle.com:9092'
KAFKA_CLIENT = KafkaClient(KAFKA_HOSTS)
KAFKA_TOPIC = "providerReports"

CURRENT_HOST = SQL_HOST_QA1
CURRENT_DATABASE = "natpal"
CURRENT_USER = "qa"
CURRENT_PASSWORD = "yodleqa"


def printWithTime(message):
    time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    message = "%s | %s" % (time, message)
    print(message)


def getDictCursorToDBAndPrint(dbname, user, host, password):
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (dbname, user, host, password))
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    printWithTime("Connected to database %s at %s as %s" % (dbname, host, user))
    return (conn, cur)


def getSomeProviderReports(cur):
    sql = """
    select
pv.basecampaign_id,
pv.day,
acb.client_id,
pv.impressions,
pv.clicks,
pv.margincost,
pv.averagebid,
pv.averagerank,
pv.avgcontentbid,
enumtarget.type as targettype,
enumct.type as campaigntype,
bc.matchtype
from aggregates.provider_reports_basecampaign_day pv
join control.basecampaign bc on bc.id = pv.basecampaign_id
join control.campaignconfiguration cc on cc.id = bc.campaignconfiguration_id
join control.adconfiguration acn on acn.id = cc.adconfiguration_id
join control.adconfigurable acb on acb.id = acn.adconfigurable_id
join enum.campaign_type enumct on enumct.id = bc.campaigntype
join enum.target_type enumtarget on enumtarget.id = bc.target
where pv.day between '2016-01-20' and '2016-01-25'
and acb.dtype='CLIENT'
limit 10000;
"""
    cur.execute(sql)
    listOfJsonObjects = cur.fetchall()
    printWithTime("Extracted %d messages" % len(listOfJsonObjects))
    return listOfJsonObjects


def makeKafkaProducer():
    # producer = KafkaProducer(bootstrap_servers=KAFKA_HOSTS, value_serializer=json.loads)
    producer = SimpleProducer(KAFKA_CLIENT)
    printWithTime("Created kafka producer")
    return producer


def sendDatasToKafka(prod, topic, listOfJsonObjects):
    for jsonObject in listOfJsonObjects:
        jsonObject["day"] = str(jsonObject["day"])
        prod.send_messages(topic, json.dumps(jsonObject).encode("utf-8"))
        sleep(.01)


def main():
    conn, cur = getDictCursorToDBAndPrint(dbname=CURRENT_DATABASE,
                                          user=CURRENT_USER,
                                          host=CURRENT_HOST,
                                          password=CURRENT_PASSWORD)

    listOfJsonObjects = getSomeProviderReports(cur);
    producer = makeKafkaProducer()
    sendDatasToKafka(producer, KAFKA_TOPIC, listOfJsonObjects)

if __name__ == "__main__":
    main()
