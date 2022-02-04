#!/usr/bin/python3
"""
This script connects to MACH Backend DB and compiles MACH user statistics

Changelog:
V1: Basic stats
"""

"""
Run this command on mach-config.json to get all MACHs scanned by AM 
cat mach-configs.json | jq '.' | jq -c 'select( (.username == "googleplay@adria-mobil.si" or .username == "mach.config@gmail.com") and .machId != "" )' | jq '. | .machId' | un    iq | wc -l
"""
import argparse
import psycopg2

def query(cur, query):
    cur.execute(query)
    data = cur.fetchone()
    return data[0]



parser = argparse.ArgumentParser()
parser.add_argument('-p', '--password', default='ZelenaSolata', help='db password')
args = parser.parse_args()
BACKEND_DB_NAME = 'machbackend'

print('Connecting to DB', BACKEND_DB_NAME)
conn_backend = psycopg2.connect(host='localhost', port=5555, database=BACKEND_DB_NAME, password=args.password, user='postgres')
backend_cur = conn_backend.cursor()
print('PostgreSQL DB version:', query(backend_cur, 'SELECT version();'))

ALL_USERS_Q = 'SELECT COUNT(*) from users;'
print('All registered users:', query(backend_cur, ALL_USERS_Q))
ALL_EXTERNAL_USERS_Q = """SELECT COUNT(*)
                        FROM users
                            WHERE username NOT LIKE '%adria-mobil.si'
                        AND username NOT LIKE '%solvesall.com';"""
print('Registered users without AM and SA:', query(backend_cur, ALL_EXTERNAL_USERS_Q))

USERS_WITH_MACH = """select count(1) from (select username
from (select "userId", email, username
      from users
      where username not ilike '%adria-mobil%'
        and username not ilike '%solvesall%'
        and username not ilike '%comsensus%') as u
         left join "userDeviceAcl" as acl on acl."userId" = u."userId" where "machId" IS NOT NULL
group by username) as u;"""
print('Users who have access to at least 1 MACH:', query(backend_cur, USERS_WITH_MACH))
MACH_WITH_USERS = """select count(1) from (select m."machId", count(1) from (select * from "userDeviceAcl") as u inner join machs as m on m."machId" = u."machId"
group by m."machId") as m;"""

print('MACH with at least 1 user:', query(backend_cur, MACH_WITH_USERS))

USERS_WITH_NO_MACH = """select count(*)
from (select u."userId", username, email, "machId", role
from (select * from users as u where username not like '%adria-mobil.si' and username not like '%solvesall.com') as u
         left join "userDeviceAcl" as acl on acl."userId" = u."userId"
order by "userId") as filtered
 where "machId" IS NULL;"""

print("Users who have no MACH:", query(backend_cur, USERS_WITH_NO_MACH))
SPAM_YES_MACH_NO = """select count(*)
from (select u."userId", username, email, "machId", role
from (select * from users as u where username not like '%adria-mobil.si' and username not like '%solvesall.com') as u
         left join "userDeviceAcl" as acl on acl."userId" = u."userId"
order by "userId") as filtered
         left join consents as c on filtered."userId" = c."userId" where "consentId" = 'consent-electronic-marketing' and "machId" IS NULL;"""
print('Users with no MACH, consented to e-marketing:', query(backend_cur, SPAM_YES_MACH_NO))

SPAM_YES_MACH_ANY = """select count(*)
from (select *
      from users as u
      where username not like '%adria-mobil.si' and username not like '%solvesall.com') as filtered
         left join consents as c on filtered."userId" = c."userId" where "consentId" = 'consent-electronic-marketing';"""

print('All users that consented to e-marketing:', query(backend_cur, SPAM_YES_MACH_ANY))
