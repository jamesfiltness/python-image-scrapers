from threading import Event, Thread
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import psycopg2
import requests
import urllib2
import json
import time
import os

conn = psycopg2.connect(
  database="musicbrainz_db",
  user="musicbrainz",
  password="musicbrainz",
  port="15432",
  host="localhost"
)

print("DB Connection established")

cur = conn.cursor()

offset = 513
fileCount = 0
fileNameCount = 1

def writeFile(filename, msg):
  filename = os.path.join('logs', filename)
  text_file = open(filename, "a")
  text_file.write(msg + "\n")
  text_file.close()

def writeLog(fileName, msg):
  global fileCount
  global fileNameCount
  if fileCount < 500:
    writeFile(fileName + str(fileNameCount) + ".txt", msg)
    fileCount += 1
  else:
    fileCount = 0
    fileNameCount += 1
    writeFile(fileName + str(fileNameCount) + ".txt", msg)


def getCoverArt(json, artistName, gid):
  print "---------------------------------------------------------------------------------------"
  global offset
  releaseGroups = json['release-groups']
  if releaseGroups and len(releaseGroups) > 0:
    print artistName, "has", len(releaseGroups), "releases", "(Offset:", offset, ")"
    for releaseGroup in releaseGroups:
      print "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _"
      print "  -- Scraping image for", releaseGroup['title'], "id:", releaseGroup['id']
      dataSrc = "http://coverartarchive.org/release-group/" + releaseGroup['id'] + "/front-250"
      print "  --", dataSrc
      try:
        request = urllib2.Request(
          dataSrc,
          headers={
            "User-Agent" :
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
          }
        )

        image = urllib2.urlopen(request).read()
        filename = releaseGroup['id'] + '.jpg'
        filename = os.path.join('images', filename)
        file_ = open(filename, 'w')
        file_.write(image)
        file_.close()
        print "  -- IMAGE SAVED!", releaseGroup['id'] + ".jpg"
      except urllib2.HTTPError, e:
        print "  --", e.code, "No image found"
        writeLog('image-error-', releaseGroup['id'])
        # write a log that there's no image for releaseGroup['id']
      time.sleep(6)
  else:
    writeLog('no-release-groups-', gid)
    print artistName,  gid, "has no releases :(", "(Offset:", offset, ")"

def queryArtists(offset):
  offset = str(offset)
  cur.execute("SELECT name, gid FROM artist OFFSET " + offset + " LIMIT 1");
  result =  cur.fetchone()
  artistName = result[0]
  gid = result[1]
  url="http://localhost:5000/ws/2/release-group/?query=arid:%22" + gid + "%22%20AND%20type:%22album%22%20AND%20status:%22official%22&fmt=json"
  r=requests.get(url)
  getCoverArt(json.loads(r.content), artistName, gid)

offset = 0
while offset < 1500000:
  queryArtists(offset)
  offset = offset + 1
