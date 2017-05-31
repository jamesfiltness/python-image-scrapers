from threading import Event, Thread
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import psycopg2
import requests
import urllib2
import os
import time
import json

def writeFile(filename, msg):
  filename = os.path.join('logs', filename)
  text_file = open(filename, "a")
  text_file.write(msg + "\n")
  text_file.close()

def writeLog(filename, msg):
  writeFile(filename + ".txt", msg)

headers={
  "User-Agent" :
  "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}

releasesBumped = 0

for release in someRelease:
  print "------------------------------------------------------------"
  elasticSearchUrl = 'http://localhost:9200/releases/release/' + release
  elasticSearchRequest = requests.get(elasticSearchUrl, headers=headers)
  jsonResponse = json.loads(elasticSearchRequest.content)
  views = jsonResponse['_source']['views']

  # only bump release score if they haven't been bumped before
  if views == 0:
    # make a request to bump the views by 100
    data = { "script" : "ctx._source.views+=100" }
    payload = json.dumps(data)
    try:
      print jsonResponse['_source']['name']
      requests.post(elasticSearchUrl + "/_update", headers=headers, data=payload)
      releasesBumped += 1
      print "-- Bumping! Releases bumped so far", releasesBumped
    except urllib2.HTTPError, e:
      print "-- Some error in bumping view score"
      writeLog('error-release-bump', release)
  else :
    # log that release has been already bumped
    writeLog('release-already-bumped', release)
    print "--", jsonResponse['_source']['name'], "already bumped, views:", jsonResponse['_source']['views']
  time.sleep(2)
