# This script takes well know artists from various genres and grabs the ids of their top 100 related artists (ids)
# from lastm. This script will then be run on those related artists
# The script bumps the views score which will be used to help return relevant results for the tuneify elasticsearch autocomplete
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
  "ed2ac1e9-d51d-4eff-a2c2-85e81abd6360", # "Bob Marley",
  "c296e10c-110a-4103-9e77-47bfebb7fb2e", # "Bob Marley and the wailers
  "7db6aae5-6644-4513-9bfc-ca2e79d4469c", # "Peter Josh",
  "2caa54a7-b08c-41da-b892-3a41abe778be", # "Jimmy cliff",
  "29730ee3-e1c7-4e28-9ccd-3a0e6b0e8103"  # "Toots and maytals"
]

classical = [
  "b972f589-fb0e-474e-b64a-803b0364fa75", # "mozart",
  "24f1766e-9635-4d58-a4d4-9413f9f98a4c", # "bach",
  "1f9df192-a621-4f54-8850-2c5373b7eac9", # "beethoven",
  "09ff1fe8-d61c-4b98-bb82-18487c74d7b7", # "chopin",
  "53b106e7-0cc6-42cc-ac95-ed8d30a3a98e"  # "john williams"
]

jazz = [
  "561d854a-6a28-4aa7-8c99-323e6ce46c2a", # "Miles Davis",
  "eea8a864-fcda-4602-9569-38ab446decd6", # "Louis Armstrong",
  "3af06bc4-68ad-4cae-bb7a-7eeeb45e411f", # "Duke Ellington",
  "b625448e-bf4a-41c3-a421-72ad46cdb831", # "John Coltrane",
  "54799c0e-eb45-4eea-996d-c4d71a63c499", # "Ella Fitzgerald",
  "c7356af9-9ea6-4a78-a55b-c73775716312", # "Charlie Parker",
  "d59c4cda-11d9-48db-8bfe-b557ee602aed", # "Billie Holiday",
  "8e8c7417-c905-46b1-b42a-5260b4274ed4"  # "Thelonious Monk"
]

punk = [
  "e5db18cb-4b1f-496d-a308-548b611090d3", # "Sex Pistols",
  "084308bd-1654-436f-ba03-df6697104e19", # "Green day",
  "d6ed7887-a401-47a8-893c-34b967444d26", # "Ramones",
  "8f92558c-2baa-4758-8c38-615519e9deda", # "The Clash",
  "31e9c35b-2675-4632-8596-f9bd9286f6c8"  # "Buzzcocks"
]

soul = [
  "afdb7919-059d-43c1-b668-ba1d265e7e42", # "Marvin Gaye",
  "2f9ecbed-27be-40e6-abca-6de49d50299e", # "Aretha Franklin",
  "1ee18fb3-18a6-4c7f-8ba0-bc41cdd0462e", # "Stevie Wonder",
  "fb7272ba-f130-4f0a-934d-6eeea4c18c9a", # "Al Green",
  "20ff3303-4fe2-4a47-a1b6-291e26aa3438", # "James Brown",
  "82b1f5fd-cd31-41a9-b5d4-7e33f0eb9751", # "Otis Reddding",
  "2ce02909-598b-44ef-a456-151ba0a3bd70"  # "Ray Charles"
]

electronic = [
  "f22942a1-6f70-4f48-866e-238cb2308fbd", # "Aphex Twin",
  "1946a82a-f927-40c2-8235-38d64f50d043", # "Chemical Brothers",
  "ae002c5d-aac6-490b-a39a-30aa9e2edf2b", # "Skillrex",
  "5700dcd4-c139-4f31-aa3e-6382b9af9032", # "Kraftwerk",
  "4a00ec9d-c635-463a-8cd4-eb61725f0c60", # "Deadmau5",
  "aabb1d9f-be12-45b3-a84d-a1fc3e8181fd", # "tiesto",
  "8970d868-0723-483b-a75b-51088913d3d4", # "Moby",
  "056e4f3e-d505-4dad-8ec1-d04f521cbb56", # "Daft Punk",
  "69158f97-4c07-4c4e-baf8-4e4ab1ed666e", # "Boards of canada",
  "4a4ee089-93b1-4470-af9a-6ff575d32704", # "The Prodigy",
  "ff95eb47-41c4-4f7f-a104-cdc30f02e872", # "Brian Eno",
  "34c63966-445c-4613-afe1-4f0e1e53ae9a"  # "Fatboy Slim"
]

metal = [
 # todo
]

headers={
  "User-Agent" :
  "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}

artistsBumped = 0

for artist in reggae:
  print "------------------------------------------------------------"
  elasticSearchUrl = 'http://localhost:9200/artists/artist/' + artist
  elasticSearchRequest = requests.get(elasticSearchUrl, headers=headers)
  jsonResponse = json.loads(elasticSearchRequest.content)
  views = jsonResponse['_source']['views']

  # only bump artist score if they haven't been bumped before
  if views == 0:
    # make a request to bump the views by 100
    data = { "script" : "ctx._source.views+=100" }
    payload = json.dumps(data)
    try:
      print jsonResponse['_source']['name']
      requests.post(elasticSearchUrl + "/_update", headers=headers, data=payload)
      artistsBumped += 1
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
