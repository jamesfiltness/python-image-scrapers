from threading import Event, Thread
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import psycopg2
import requests
import urllib2
import json
import time

conn = psycopg2.connect(
  database="musicbrainz_db",
  user="musicbrainz",
  password="musicbrainz",
  port="15432",
  host="localhost"
)

print("DB Connection established")

cur = conn.cursor()

offset = 0
fileCount = 0
fileNameCount = 0

def writeFile(filename, msg):
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
    print "Offset:", offset, artistName, "has", len(releaseGroups), "releases"
    for releaseGroup in releaseGroups:
      print "  -- Scraping image for", releaseGroup['title'], "id:", releaseGroup['id']
      dataSrc = "http://coverartarchive.org/release-group/" + releaseGroup['id'] + "/front-250"
      print dataSrc
      try:
        image = urllib2.urlopen(dataSrc)
        result = image.read()
        print "IMAGE FOUND!"
        # print result
      except urllib2.HTTPError, e:
        print e.code, "No image found"
        writeLog('image-error-', releaseGroup['id'])
        # write a log that there's no image for releaseGroup['id']
      time.sleep(6)
  else:
    writeLog('no-release-groups-', gid)
    print "Offset:", offset, artistName,  gid, "has no releases :("

def queryArtists(offset):
  offset = str(offset)
  cur.execute("SELECT name, gid FROM artist OFFSET " + offset + " LIMIT 1");
  result =  cur.fetchone()
  artistName = result[0]
  gid = result[1]
  url="http://localhost:5000/ws/2/release-group/?query=arid:%22" + gid + "%22%20AND%20type:%22album%22%20AND%20status:%22official%22&fmt=json"
  r=requests.get(url)
  print json.loads(r.content)
  getCoverArt(json.loads(r.content), artistName, gid)

offset = 0
while offset < 1500000:
  queryArtists(offset)
  offset = offset + 1
