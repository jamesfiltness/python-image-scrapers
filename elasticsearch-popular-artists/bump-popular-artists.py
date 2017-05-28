from threading import Event, Thread
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import psycopg2
import requests
import urllib2
import os
import time
import json


#Artists to bump manually
#Nirvana

def writeFile(filename, msg):
  filename = os.path.join('logs', filename)
  text_file = open(filename, "a")
  text_file.write(msg + "\n")
  text_file.close()

def writeLog(filename, msg):
  writeFile(filename + ".txt", msg)

popRock = [
"Elvis Presley",
"The Beatles",
"The Rolling Stones",
"The clash",
"Nirvana",
"The Libertines",
"The Jam",
"Soundgarden",
"The Beach Boys",
"Led Zepelin",
"Radiohead",
"The Kinks",
"The Killers",
"The Doors",
"Eagles",
"Van Morrison",
"Simon & Garfunkel",
"Pink Floyd",
"Neil Young",
"Jimi Hendrix",
"Elton John",
"REM",
"U2",
"The Strokes",
"Oasis",
"Blur",
"Red hot chilli peppers",
"artic monkeys"
"Queen",
"Fleetwood Mac",
"The xx",
"The Cure",
"Tame Impala",
"Bee gees",
"Bruce Springsteen",
"Billy Joel",
"Phil Collins",
"Bon Jovi",
"Fleetwood mac",
"David Bowie",
"The Who"
]

folk = [
"Pete Seeger",
"Bob Dylan",
"Nick Drake",
"Leonard Cohen",
"Billy Bragg",
"Woody Guthrie",
"Richard Thompson",
"Donovan",
"John Martyn",
"Bert Jansch",
"Tom Paxton",
"Ralph McTell"
]

hiphop = [
 "jay-z",
 "Drake",
 "Kanye west",
 "Eminem",
 "Dr dre",
 "Kendrick Lamar",
 "Lil wayne",
 "Snoop dog",
 "2pac",
 "Nas",
 "Sean coombs",
 "Notorious big",
 "wu tang",
 "Nwa",
 "50 cent",
 "Beastie boys",
 "ll cool j",
 "public enemy",
 "run dmc"
]

pop = [
"Lady Gaga",
"Adele",
"Maroon 5",
"Madonna",
"Kylie minogue"
"michael Jackson",
"celine dion",
"abba",
"taylor swift",
"Gorillaz",
"Kate Perry",
"Lana Del Ray",
"The ChainSmokers",
"Drake",
"Ed Sheeran",
"Ariana Grande",
"Justin Timberlake",
"Kendrick Lamar",
"Rihanna"
"Bruno Mars"
]

country = [
 "Hank Williams",
 "Patsy Cline",
 "Emmylou Harris",
 "Shania Twain",
 "Johnny Cash"
]

blues = [
  "bb king",
  "Muddy waters",
  "Buddy guy",
  "Robert Johnson",
  "Howlin wolf",
  "JOhn lee hooker",
  "Lead belly",
  "eric clapton",
  "son house",
  "John mayall",
  "skip james",
  "big bill broonzy",
  "ray charles"
]

reggae = [
  "Bob Marley",
  "Peter Josh",
  "Jimmy cliff",
  "Toots and maytals"
]

classical = [
"mozart",
"bach",
"beethoven",
"chopin",
"john williams"
]

jazz = [
"Miles Davis",
"Louis Armstrong",
"Duke Ellington",
"John Coltrane",
"Ella Fitzgerald",
"Charlie Parker".
"Billie Holiday",
"Thelonious Monk"
]

punk = [
 "Sex Pistols",
 "Green day",
 "Ramones",
 "The Clash",
 "Buzzcocks"
]

soul = [
"Marin Gaye",
"Aretha Franklin",
"Stevie Wonder",
"Al Green",
"James Brown",
"Otis Reddding",
"Ray Charles"
]

electronic = [
"Aphex Twin",
"Chemical Brothers",
"Skillrex",
"Kraftwerk",
"Deadmau5",
"tiesto",
"Moby",
"Daft Punk",
"Boards of canada",
"The Prodigy",
"Brian Eno",
"Fatboy Slim"
]

metal = [

]


artistsBumped = 0
for artist in test:
  print "------------------------------------------------------------"
  elasticSearchUrl = 'http://localhost:9200/artists/artist/' + artist
  elasticSearchRequest = requests.get(elasticSearchUrl, headers=headers)
  jsonResponse = json.loads(elasticSearchRequest.content)
  views = jsonResponse['_source']['views']

  if views == 0:
    # make a request to bump the views by 100
    data = { "script" : "ctx._source.views+=100" }
    payload = json.dumps(data)
    try:
      requests.post(elasticSearchUrl + "/_update", headers=headers, data=payload)
      print "-- Bumping! Artists bumped so far", artistsBumped
      releaseGroupsUrl = "http://localhost:5000/ws/2/release-group/?query=arid:%22" + artist + "%22%20AND%20type:%22album%22%20AND%20status:%22official%22&fmt=json"

      releaseGroupData = requests.get(releaseGroupsUrl)
      releaseGroupsJson = json.loads(releaseGroupData.content)
      releaseGroups = releaseGroupsJson['release-groups']
      print "-- Saving release groups: ", len(releaseGroups)
      for releaseGroup in releaseGroups:
        writeLog('release-group', releaseGroup['id'])

      # call last fm and get all related artists and log those to a file (to be run against this script later)
      lastFmSimilarArtistsUrl = "http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&mbid=" + artist + "&api_key=57ee3318536b23ee81d6b27e36997cde&format=json"
      lastFmSimilarArtistsRequest = requests.get(lastFmSimilarArtistsUrl, headers=headers)
      lastFmJsonSimilarArtistsResponse = json.loads(lastFmSimilarArtistsRequest.content)
      similarArtists = lastFmJsonSimilarArtistsResponse['similarartists']['artist']
      print "-- Saving similar artists: ", len(similarArtists)
      for artist in similarArtists:
        try:
          if artist['mbid']:
            writeLog('similar-artist', artist['name'] + artist['mbid'])
        except:
          continue
    except urllib2.HTTPError, e:
      print "-- Some error in bumping view score or getting release data"
      writeLog('error-check-artist-bump', artistMbid)
  else :
    # log that artist has been already bumped
    writeLog('artist-already-bumped', artistMbid)
    print "--", jsonResponse['_source']['name'], "already bumped, views:", jsonResponse['_source']['views']
  time.sleep(2)
