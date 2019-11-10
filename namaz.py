import requests, sys, pickle, json, localizations
from cachetools import cached, LRUCache, TTLCache
from datetime import datetime as dt

#9541 for Istanbul, retrieves from script filter command line
placeId = sys.argv[1] if len(sys.argv) > 1 else "9541"

# Default lang is English when not indicated
langCode = sys.argv[2] if len(sys.argv) > 2 else "en" 
localization = eval("localizations." + langCode)

fmt = '%H:%M'

# Flag for displaying remaining time
displayed_remaining_time_once = False

times = [0,0,0,0,0,0]
items = {'items': []}

try:
    with open('prayer.pickle', 'rb') as f:
        cache = pickle.load(f)
except FileNotFoundError:
    #Cache expires in 1 hour as seconds
    cache = TTLCache(maxsize=1024, ttl=3600)

@cached(cache)
def getTimes():
    global times
    vakit = requests.get("https://ezanvakti.herokuapp.com/vakitler?ilce=" + placeId)
    root = json.loads(vakit.text)[0]
    # 5 + 1 times
    times = [
        localization.Fajr + ": " + root["Imsak"],
        localization.Sun + ": " + root["Gunes"],
        localization.Dhuhr + ": " + root["Ogle"],
        localization.Asr + ": " + root["Ikindi"],
        localization.Maghrib + ": " + root["Aksam"],
        localization.Isha + ": " + root["Yatsi"]
        ]
    title =  localization.results_for + root["MiladiTarihKisa"] + " / " + root["HicriTarihUzun"].title()
    #first item is date for display at the top
    times.insert(0, title)
    return times

def main():
    global times, displayed_remaining_time_once
    now = dt.now().strftime(fmt)
    times = getTimes()
    subtitle = ""
    for time in times:
        if times.index(time) != 0:
            clock_time = ":".join(time.split(":")[-2:]).replace(" ","")
            delta = dt.strptime(clock_time, fmt) - dt.strptime(now, fmt)
            if delta.total_seconds() > 1 and not displayed_remaining_time_once:
                subtitle = localization.remaining + ":".join(str(delta).split(":")[:2]) #2:43:00 -> 2:43
                displayed_remaining_time_once = True
            else:
                subtitle = ""
        items["items"].append({"title": time, "subtitle": subtitle})
    print(json.dumps(items))

main()

with open('prayer.pickle', 'wb') as f:
    pickle.dump(cache, f)
