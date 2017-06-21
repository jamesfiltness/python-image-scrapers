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

offset = 0
imageErrorWriteCount = 0
imageErrorFileCount = 0

def writeFile(filename, msg):
  filename = os.path.join('logs', filename)
  text_file = open(filename, "a")
  text_file.write(msg + "\n")
  text_file.close()

def writeImageErrorLog(msg):
  global imageErrorWriteCount
  global imageErrorFileCount
  if imageErrorWriteCount <= 500:
    writeFile("image-error-" + str(imageErrorFileCount) + ".txt", msg)
    imageErrorWriteCount += 1
  else:
    imageErrorWriteCount = 0
    imageErrorFileCount += 1
    writeFile("image-error-" + str(imageErrorFileCount) + ".txt", msg)

def queryReleaseGroups(offset):
  offset = str(offset)
  cur.execute("SELECT name, gid FROM release_group OFFSET " + offset + " LIMIT 1");
  result =  cur.fetchone()
  artistName = result[0]
  gid = result[1]
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
    writeImageErrorLog(releaseGroup['id'])
  time.sleep(1)

while offset < 1500000:
  queryReleaseGroup(offset)
  offset = offset + 1
