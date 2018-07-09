import requests
import time
import csv
from datetime import datetime

url = 'http://data.lpp.si/bus/busLocation'
start_time = time.time()
filename = 'bus_data2.csv'
print('Start time: ', datetime.now())
end_time = start_time

with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    wr = csv.writer(csvfile, delimiter=',')
    wr.writerow(
        ['data_written_at','bus_id', 'reg_number', 'speed', 'direction', 'route_int_id', 'station_int_id', 'utc_time', 'local_time',
         'unix_time', 'lat', 'lon'])

    while end_time - start_time < 60 * 60 * 24:
        try:
            rq = requests.get(url, headers={'apikey': 'e9a2d97e-6c89-4479-ac8c-2054cd93a3e1'})
        except Exception as e:
            print(e)
            time.sleep(30)
            continue

        if rq.status_code == 200:
            for d in rq.json()['data']:
                wr.writerow([int(time.time()*1000),d['int_id'], d['reg_number'], d['speed'], d['route_int_id'], d['station_int_id'],
                             d['utc_timestamp'], d['local_timestamp'], d['unix_timestamp'],
                             d['geometry']['coordinates'][1], d['geometry']['coordinates'][0]])
            print('Written', len(rq.json()['data']), 'records to file at', datetime.now())
        else:
            print('Skipped for reasons unknown: ', datetime.now())
        time.sleep(30)

print('Finished downloading at', datetime.now())
