#!/usr/bin/python3

import argparse
import psycopg2

def query(cur, query):
    cur.execute(query)
    data = cur.fetchone()
    return data[0]

import time
import re

parser = argparse.ArgumentParser()
parser.add_argument('-dp', '--db-port', default=5555, help='Database Port')
parser.add_argument('-m', '--mach-id', required=True, help='MACH ID')
parser.add_argument('-p', '--password', default='testpwd', help='db password')
args = parser.parse_args()
BACKEND_DB_NAME = 'machlogger'

print('Connecting to DB', BACKEND_DB_NAME)
conn_backend = psycopg2.connect(host='localhost', port=args.db_port, database=BACKEND_DB_NAME, password=args.password, user='postgres')
cur = conn_backend.cursor()
machID = args.mach_id
# print("Found MACHs:", cur.fetchone())
print('go transaction')
cur.execute('BEGIN')

with open(machID+ '-dblog.log', 'w') as wf:


    cur.execute("DECLARE mcur CURSOR FOR SELECT * FROM errors where client_id = '"+machID+"' ORDER BY timestamp, id ASC")
    cur.execute('FETCH 10 FROM mcur')
    data = cur.fetchall()
    while len(data) > 0:

        cur.execute('FETCH 10 FROM mcur')
        data = cur.fetchall()
        for row in data:

            src = row[4]
            if 'Log4j2Logger' in src:
                src = src.replace("com.solvesall.mach.logging.Log4j2Logger", "log")

            msg = row[5].replace('ParameterizedMessage',"")
            src = re.sub(r'Log4j2Logger.java:[0-9]*',"",  src)
            if 'messagePattern=' in msg:
                pattern = re.findall(r'messagePattern=[^"]*?,',msg)[0].replace("messagePattern=", "")[:-1]
                args = re.findall(r"stringArgs=\[[^']*?\]", msg)[0].replace('stringArgs=[', '')[:-1].split(',')
                for arg in args:
                    pattern = re.sub(r'{}', arg, pattern, 1)  
            else:
                pattern = msg

            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2]/1000.0))
            stra = "[{0}] [{1}]: [{2}] - {3}".format(row[1], ts, src, pattern)
            wf.write(stra + '\n')    
            print(stra)

cur.execute('COMMIT')
conn_backend.commit()
