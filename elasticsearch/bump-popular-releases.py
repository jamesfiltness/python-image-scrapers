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

releaseTest = [
'03212229-7462-38b7-99e8-c5069209d192' # Reinventing the Steel
'75a041d3-1fa8-3082-bf4a-ad65416c4624' # The Great Southern Trendkill
'814e0b20-6884-31c5-9d99-d215f048cfd6' # Vulgar Display of Power
'a0398241-a842-3593-83b4-a1aa1df23328' # Cowboys From Hell
'2abca5cc-8985-315f-b948-8a34df27debd' # Power Metal
'60b55a8c-fe68-3397-91a3-7444cab57d7b' # Far Beyond Driven
'14e76406-39e6-314b-8b1f-1f93857a4aff' # Metal Magic
'30f8095a-7ed8-34bf-9355-511224e8d670' # Projects in the Jungle
'd2814a47-c8fa-39a4-a5dc-9e4c0209cfff' # I Am the Night
'eafab7b9-4f8f-3083-861c-7d13869ba2ff' # Maiden Voyage
]

for release in testRelease:
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
