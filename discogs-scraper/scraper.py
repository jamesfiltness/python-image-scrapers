from threading import Event, Thread
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import psycopg2
import requests
import urllib
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
artistMissingCount = 0
artistMissingFileCount = 0
imageMissingCount = 0
imageMissingFileCount = 0

def writeFile(filename, msg):
  filename = os.path.join('logs', filename)
  text_file = open(filename, "a")
  text_file.write(msg + "\n")
  text_file.close()

def artistMissingLog(msg):
  global artistMissingCount
  global artistMissingFileCount
  if artistMissingCount <= 500:
    writeFile("artist-missing-error-" + str(artistMissingFileCount) + ".txt", msg)
    artistMissingCount += 1
  else:
    artistMissingCount = 0
    artistMissingFileCount += 1
    writeFile("artist-missing-error-" + str(artistMissingFileCount) + ".txt", msg)

def imageMissingLog(msg):
  global imageMissingCount
  global imageMissingFileCount
  if imageMissingCount <= 500:
    writeFile("image-missing-" + str(imageMissingFileCount) + ".txt", msg)
    imageMissingCount += 1
  else:
    imageMissingCount = 0
    imageMissingFileCount += 1
    writeFile("image-missing-" + str(imageMissingFileCount) + ".txt", msg)

def scrapeDiscogs(artist_name, gid, offset):
  index = 0
  print "No: " + offset + "| Scraping " + artist_name + " " + gid
  artistNameEncoded = urllib.quote(artist_name)
  url="https://www.discogs.com/search/?type=artist&q=" + artistNameEncoded
  headers={
    "User-Agent" :
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
  }

  r=requests.get(url,headers=headers)
  soup = BeautifulSoup(r.content, "html.parser")
  para = soup.findAll('p')[1].getText()
  if "We couldn't find anything in the Discogs database matching your search criteria." in para:
    print "No artist found for: " + artist_name + " " + gid
    artistMissingLog(gid);
  else:
    results = soup.findAll("div", { "class" : "card_large" })
    found = False

    # loop over all results
    for card in results:
      # if the result contains an exact text match to the artist
      if card.find("h4").getText().encode("utf8", 'replace') == artist_name:
        found = True
        # grab the data-src from the image
        span = card.find("span", {"class": "thumbnail_center"})
        dataSrc = span.find("img").get('data-src')
        # if the the data-src is the dummy image then don't save it
        if dataSrc == "https://s.discogs.com/images/default-artist.png":
          print "No: " + offset + "| No img for: " + artist_name + " gid: " + gid
          imageMissingLog(gid);
        else:
          # retrieve the image and save to disc
          urllib.urlretrieve(dataSrc, "images/" + gid + ".jpg")
          print "No: " + offset + " | Img retrieved for " + artist_name + " gid: " + gid
    # if the artist name was not found in any of the results...
    if found == False:
      print "No: " + offset + "| Artist text not found: " + artist_name + " gid: " + gid
      artistMissingLog(gid);

def queryArtists(offset):
  offset = str(offset)
  cur.execute("SELECT name, gid FROM artist OFFSET " + offset + " LIMIT 1");
  result =  cur.fetchone()
  artistName = result[0]
  gid = result[1]
  image = scrapeDiscogs(artistName, gid, offset)

def call_repeatedly(interval, func):
  stopped = Event()
  def loop():
    while not stopped.wait(interval): # the first call is in `interval` secs
      global offset
      queryArtists(offset)
      offset += 1
  Thread(target=loop).start()
  return stopped.set

call_repeatedly(7, queryArtists)

