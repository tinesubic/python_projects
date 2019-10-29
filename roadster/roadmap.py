import requests
import csv

"""CSV generator for IJS road mapping"""

def make_url(lat,lon):
    return 'https://www.google.si/maps/place/{},{}/@{},{},14.48z'.format(lat, lon, lat, lon)


url='http://traffic.ijs.si/API/optimum/counters'
counter = 0
counter_all = 0
data = requests.get(url).json()

with open('roads4.csv', 'w', encoding='UTF-8') as roadmap:
    csvwriter = csv.writer(roadmap, delimiter=',', quotechar='"', lineterminator='\n')
    csvwriter.writerow(['SystemCodeNumber', 'Id', 'Url', 'Lat', 'Lon', 'Type', 'Lane', 'Direction'])
    for d in data:
        for r in d['Readings']:
            if r['Type'] == 'headway':
                counter_all +=1
                try:
                    pass
                    print(r['Direction'])
                    #csvwriter.writerow([d['SystemCodeNumber'], r['Id'], make_url(d['Lat'], d['Lng']), d['Lat'], d['Lng'], r['Type'], r['Lane'], r['Direction']])
                except Exception as e:
                    csvwriter.writerow(
                        [d['SystemCodeNumber'], r['Id'], make_url(d['Lat'], d['Lng']), d['Lat'], d['Lng'], r['Type'],
                         r['Lane'], r['DirectionRaw']])
                    print(e, d,r)
                    counter+=1
print(counter_all)
