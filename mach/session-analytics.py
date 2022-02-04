import json
from math import ceil

import seaborn as sns
import matplotlib.pyplot as plt
import requests


def fetch_data():
    global data
    url = "https://mach-backend.solvesall.com/v0/machend/mach-stats-debug"
    payload = json.dumps({
        "username": "mach-admin@solvesall.com",
        "password": "lzJ0Sae4kM0hevRCjDJk"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()


fetch_data()
timestamp = data["timestamp"]
data = data["sessions"]
value_ids = {}

print('Got', len(data), 'MACHs')
total_sessions = 0  # all recorded sessions
running_sessions = 0  # currently active sessions
sessions = []
min_time = 100000000000000000
short_sessions = []
SHORT_THRESHOLD = 5  # minutes
total_bytes = 0

for mach in data:
    total_bytes += mach["bytes"]
    for value in mach["valueIds"]:
        if value not in value_ids:
            value_ids[value] = 0
        value_ids[value] += mach["valueIds"][value]

    for session in mach["sessions"]:
        total_sessions += 1
        if session["end"] == 0:
            running_sessions += 1
            session["end"] = timestamp
        if float(session["start"]) < min_time:
            min_time = float(session["start"])

        if float(session["end"]) - float(session["start"]) < 60 * SHORT_THRESHOLD:
            short_sessions.append(session)
        sessions.append(session)
print('Collecting sessions for', (round(float(timestamp) - min_time) / 60.0), 'minutes')


def print_short_sessions():
    global session
    short_count_per_mach = {}
    for session in short_sessions:
        if session["machId"] not in short_count_per_mach:
            short_count_per_mach[session['machId']] = []
        short_count_per_mach[session['machId']].append(session)
    for machId in short_count_per_mach:
        if len(short_count_per_mach[machId]) > 5:
            print(machId, len(short_count_per_mach[machId]))


durations = [round((float(x["end"]) - float(x["start"])) / 60.0, 2) for x in sessions]
durations.sort()

print('Average kB per minute:', round(total_bytes / sum(durations) / 1024, 2))

bucket_count = int(ceil(((float(timestamp) - float(min_time)) / 60.0 / 10)))

print(len(list(filter(lambda x: x > 5000, durations))))

# print(durations)
print('Max session', max(durations), 'minutes')
print('Avg sessions', round(sum(durations) / len(durations), 2), 'minutes')


def plot_session_distribution():
    fig, axs = plt.subplots(ncols=2)
    values = [(x, value_ids[x]) for x in value_ids]
    values.sort(key=lambda x: x[1], reverse=True)
    threshold = 0.02 * values[0][1]  # filter all valueIds with less than 2% of max valueid counter
    values = filter(lambda x: x[1] > threshold, values)

    value_id_labels = [k[0] for k in values]
    value_id_counts = [value_ids[k] for k in value_id_labels]

    ax = sns.histplot(durations, bins=bucket_count, ax=axs[0])
    bx = sns.barplot(x=value_id_labels, y=value_id_counts, ax=axs[1], palette='rocket')
    ax.set(xlabel='Duration [minutes]', ylabel='MACH Count #')
    bx.set(xlabel='Value IDs', ylabel='Occurence count (Value IDs that have over ' + str(threshold) + ' samples)')
    bx.tick_params(axis='x', rotation=90)
    plt.show()


print('Total sessions:', total_sessions)
print('Running sessions:', running_sessions)
print('Short sessions (', SHORT_THRESHOLD, ' minutes):', len(short_sessions))
print_short_sessions()
plot_session_distribution()
