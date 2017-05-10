from threading import Event, Thread
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import psycopg2
import requests
import urllib
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
fileNameCount = 11

def writeFile(fileName, msg):
  text_file = open(fileName, "a")
  text_file.write(msg + "\n")
  text_file.close()

def getCoverArt(json, artistName, gid):
  print "---------------------------------------------------------------------------------------"
  global offset
  releaseGroups = json['release-groups']
  if releaseGroups and len(releaseGroups) > 0:
    print "Offset:", offset, artistName, "has", len(releaseGroups), "releases"
    for releaseGroup in releaseGroups:
      print "  -- Scraping image for", releaseGroup['title'], "id:", releaseGroup['id']
      dataSrc = "http://coverartarchive.org/release-group/" + releaseGroup['id']
      print dataSrc
      image = urllib.urlopen(dataSrc, "images/" + releaseGroup['id'] + ".jpg")
      print "sdfsdfsdfsdf", image.getcode()
      if image.getcode() == 404:
        print("Fuck, no image")
      elif image.getcode() == 307:
        print image.read()
      time.sleep(6)
  else:
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
