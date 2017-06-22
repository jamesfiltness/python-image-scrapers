from threading import Event, Thread
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
imagesSaved = 0
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
  global imagesSaved
  offset = str(offset)
  cur.execute("SELECT name, gid FROM release_group OFFSET " + offset + " LIMIT 1");
  result =  cur.fetchone()
  artistName = result[0]
  gid = result[1]
  print "  -- Scraping image for ", artistName, " ", gid, " offset", offset
  dataSrc = "http://coverartarchive.org/release-group/" + gid + "/front-250"
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
    filename = gid + '.jpg'
    filename = os.path.join('images', filename)
    file_ = open(filename, 'w')
    file_.write(image)
    file_.close()
    imagesSaved = imagesSaved + 1
    print "  -- IMAGE SAVED!", gid + ".jpg", " IMAGES SAVED:", imagesSaved
    print "---------------------------------------------------------------------------------"
  except urllib2.HTTPError, e:
    print "  --", e.code, "No image found"
    print "---------------------------------------------------------------------------------"
    writeImageErrorLog(gid)
  time.sleep(0.5)
