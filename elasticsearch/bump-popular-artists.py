# This script takes well know artists from various genres and grabs the musicbrainz ids of their top 100 related artists
# from lastm. This script will then be run on those related artists
# The script bumps the views score in the elasticsearch index which will be used to help return relevant results for the tuneify elasticsearch autocomplete

from threading import Event, Thread
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import psycopg2
import requests
import urllib2
import urllib
import os
import time
import json

def writeFile(filename, msg):
  filename = os.path.join('logs', filename)
  text_file = open(filename, "a")
  encoded = msg.encode('utf-8')
  text_file.write(encoded + "\n")
  text_file.close()

def writeLog(filename, msg):
  writeFile(filename + ".txt", msg)

popRock = [
  "5b11f4ce-a62d-471e-81fc-a69a8278c7da", # "Nirvana",
  "01809552-4f87-45b0-afff-2c6f0730a3be", # "Elvis Presley",
  "b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d", # "The Beatles",
  "b071f9fa-14b0-4217-8e97-eb41da73f598", # "The Rolling Stones",
  "82b304c0-7da4-45d3-896a-0767c7ae1141", # "The Libertines",
  "23228f18-01d5-493e-94ce-cfcde82a8db2", # "The Jam",
  "153c9281-268f-4cf3-8938-f5a4593e5df4", # "Soundgarden",
  "ebfc1398-8d96-47e3-82c3-f782abcdb13d", # "The Beach Boys",
  "678d88b2-87b0-403b-b63d-5da7465aecc3", # "Led Zeppelin",
  "a74b1b7f-71a5-4011-9441-d0b5e4122711", # "Radiohead",
  "17b53d9f-5c63-4a09-a593-dde4608e0db9", # "The Kinks",
  "95e1ead9-4d31-4808-a7ac-32c3614c116b", # "The Killers",
  "9efff43b-3b29-4082-824e-bc82f646f93d", # "The Doors",
  "f46bd570-5768-462e-b84c-c7c993bbf47e", # "Eagles",
  "a41ac10f-0a56-4672-9161-b83f9b223559", # "Van Morrison",
  "5d02f264-e225-41ff-83f7-d9b1f0b1874a", # "Simon & Garfunkel",
  "83d91898-7763-47d7-b03b-b92132375c47", #  "Pink Floyd",
  "75167b8b-44e4-407b-9d35-effe87b223cf", # "Neil Young",
  "06fb1c8b-566e-4cb2-985b-b467c90781d4", # "Jimi Hendrix",
  "95c2339b-8277-49a6-9aaf-08d8eeeaa0be", # "Little Richard",
  "b83bc61f-8451-4a5d-8b8e-7e9ed295e822", # "Elton John",
  "ea4dfa26-f633-4da6-a52a-f49ea4897b58", # "REM",
  "a3cb23fc-acd3-4ce0-8f36-1e5aa6a18432", # "U2",
  "f181961b-20f7-459e-89de-920ef03c7ed0", # "The Strokes",
  "39ab1aed-75e0-4140-bd47-540276886b60", # "Oasis",
  "ba853904-ae25-4ebb-89d6-c44cfbd71bd2", # "Blur",
  "8bfac288-ccc5-448d-9573-c33ea2aa5c30", # "Red hot chilli peppers",
  "ada7a83c-e3e1-40f1-93f9-3e73dbc9298a", # "artic monkeys"
  "0383dadf-2a4e-4d10-a46a-e9e041da8eb3", # "Queen",
  "bd13909f-1c29-4c27-a874-d4aaf27c5b1a", # "Fleetwood Mac",
  "c5c2ea1c-4bde-4f4d-bd0b-47b200bf99d6", # "The xx",
  "69ee3720-a7cb-4402-b48d-a02c366f2bcf", # "The Cure",
  "40f5d9e4-2de7-4f2d-ad41-e31a9a9fea27", # "The Smiths",
  "63aa26c3-d59b-4da4-84ac-716b54f1ef4d", # "Tame Impala",
  "bf0f7e29-dfe1-416c-b5c6-f9ebc19ea810", # "Bee gees",
  "70248960-cb53-4ea4-943a-edb18f7d336f", # "Bruce Springsteen",
  "64b94289-9474-4d43-8c93-918ccc1920d1", # "Billy Joel",
  "401c3991-b76b-499d-8082-9f2df958ef78", # "Phil Collins",
  "5dcdb5eb-cb72-4e6e-9e63-b7bace604965", # "Bon Jovi",
  "5441c29d-3602-4898-b1a1-b77fa23b8e50", # "David Bowie",
  "9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa"  # "The Who"
]

folk = [
  "af18a9bc-e4ab-4068-9489-b64e8186fcf1", # "Pete Seeger",
  "72c536dc-7137-4477-a521-567eeb840fa8", # "Bob Dylan",
  "99ea432a-e3d8-42cb-9d5e-db316a6a8458", # "Nick Drake",
  "65314b12-0e08-43fa-ba33-baaa7b874c15", # "Leonard Cohen",
  "7cec4a03-0a83-4308-856a-afb8aa5db0fc", # "Billy Bragg",
  "cbd827e1-4e38-427e-a436-642683433732", # "Woody Guthrie",
  "ecfeacaf-0399-470f-8207-d1c646569fd0", # "Richard Thompson",
  "72d7d717-0837-4f2a-9641-d0f9fdd3acf7", # "Donovan",
  "e821a756-487f-4931-a02f-27cf11cec7bf", # "John Martyn",
  "d7f95537-2b48-403d-9ac2-f1fc7aad0960", # "Bert Jansch",
  "1880815f-5f43-4eba-9038-96ba0380134d", # "Tom Paxton",
  "8bf5abde-89d0-4676-98ef-7e1a4eecd03d"  # "Ralph McTell"
]

hiphop = [
  "f82bcf78-5b69-4622-a5ef-73800768d9ac", # "jay-z",
  "164f0d73-1234-4e2c-8743-d77bf2191051", # "Kanye west",
  "b95ce3ff-3d05-4e87-9e01-c97b66af13d4", # "Eminem",
  "5f6ab597-f57a-40da-be9e-adad48708203", # "Dr dre",
  "381086ea-f511-4aba-bdf9-71c753dc5077", # "Kendrick Lamar",
  "ac9a487a-d9d2-4f27-bb23-0f4686488345", # "Lil wayne",
  "f90e8b26-9e52-4669-a5c9-e28529c47894", # "Snoop dog",
  "382f1005-e9ab-4684-afd4-0bdae4ee37f2", # "2pac",
  "cfbc0924-0035-4d6c-8197-f024653af823", # "Nas",
  "d5d97b2b-b83b-4976-814a-056d9076c8c3", # "Notorious big",
  "0febdcf7-4e1f-4661-9493-b40427de2c13", # "wu tang",
  "3a54bffa-2314-44a2-927b-60144119c780", # "Nwa",
  "8e68819d-71be-4e7d-b41d-f1df81b01d3f", # "50 cent",
  "9beb62b2-88db-4cea-801e-162cd344ee53", # "Beastie boys",
  "a4dd0e77-83b8-4e92-89b7-effb0e47fd8c", # "ll cool j",
  "bf2e15d0-4b77-469e-bfb4-f8414415baca", # "public enemy",
  "5ecc3f72-20a6-47a0-8dc5-fb0b3dadeea0"  # "run dmc"
]

pop = [
  "650e7db6-b795-4eb5-a702-5ea2fc46c848", # "Lady Gaga",
  "cc2c9c3c-b7bc-4b8b-84d8-4fbd8779e493", # "Adele",
  "0ab49580-c84f-44d4-875f-d83760ea2cfe", # "Maroon 5",
  "79239441-bfd5-4981-a70c-55c3f15c1287", # "Madonna",
  "2fddb92d-24b2-46a5-bf28-3aed46f4684c", # "Kylie minogue"
  "f27ec8db-af05-4f36-916e-3d57f91ecf5e", # "michael Jackson",
  "847e8a0c-cc20-4213-9e16-975515c2a926", # "celine dion",
  "d87e52c5-bb8d-4da8-b941-9f4928627dc8", # "abba",
  "20244d07-534f-4eff-b4d4-930878889970", # "taylor swift",
  "e21857d5-3256-4547-afb3-4b6ded592596", # "Gorillaz",
  "122d63fc-8671-43e4-9752-34e846d62a9c", # "Kate Perry",
  "b7539c32-53e7-4908-bda3-81449c367da6", # "Lana Del Ray",
  "91a81925-92f9-4fc9-b897-93cf01226282", # "The ChainSmokers",
  "9fff2f8a-21e6-47de-a2b8-7f449929d43f", # "Drake",
  "b8a7c51f-362c-4dcb-a259-bc6e0095f0a6", # "Ed Sheeran",
  "f4fdbb4c-e4b7-47a0-b83b-d91bbfcfa387", # "Ariana Grande",
  "596ffa74-3d08-44ef-b113-765d43d12738", # "Justin Timberlake",
  "381086ea-f511-4aba-bdf9-71c753dc5077", # "Kendrick Lamar",
  "73e5e69d-3554-40d8-8516-00cb38737a1c", # "Rihanna"
  "afb680f2-b6eb-4cd7-a70b-a63b25c763d5"  # "Bruno Mars"
]

country = [
  "906bddec-bc73-49f8-ac1e-eaee691c6cf9", # "Hank Williams",
  "ad82dd72-0df3-4a09-8d7a-1af9c9e80522", # "Patsy Cline",
  "35ef61ca-43db-4772-ba27-0489e9ebcb69", # "Emmylou Harris",
  "faabb55d-3c9e-4c23-8779-732ac2ee2c0d", # "Shania Twain",
  "d43d12a1-2dc9-4257-a2fd-0a3bb1081b86", # "Johnny Cash",
  "2819834e-4e08-47b0-a2c4-b7672318e8f0"  # "The byrds"
]

blues = [
  "dcb03ce3-67a5-4eb3-b2d1-2a12d93a38f3", # "bb king",
  "f86f1f07-d182-45ce-ae93-ef610880ca72", # "Muddy waters",
  "4336a134-d091-4e54-9967-c7c433db6d4e", # "Buddy guy",
  "8a8bbba6-72f7-4900-a306-c40b94f2631b", # "Robert Johnson",
  "ca5b38c2-f39d-45a4-ad3d-daf4448846ef", # "Howlin wolf",
  "b0122194-c49a-46a1-ade7-84d1d76bd8e9", # "John lee hooker",
  "ddcfbdcf-cf8d-4776-8a69-10f39376b5a2", # "Lead belly",
  "618b6900-0618-4f1e-b835-bccb17f84294", # "eric clapton",
  "8c87dda0-be58-4e48-a3b5-2626f26364c7", # "son house",
  "18c1e06b-fe76-4802-b070-53a2f6b707bd", # "John mayall",
  "f205743d-4441-471d-a3af-66f584738e29", # "skip james",
  "05bc49f8-3108-44c8-82b9-ac3254896a69"  # "big bill broonzy",
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
  "65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab", # "Metallica",
  "bdacc37b-8633-4bf8-9dd5-4662ee651aec", # "Slayer",
  "5182c1d9-c7d2-4dad-afa0-ccfeada921a8", # "Black Sabbath",
  "541f16f5-ad7a-428e-af89-9fa1b16d3c9c", # "Pantera",
  "ca891d65-d9b0-4258-89f7-e6ba29d83767", # "Iron Maiden",
  "ac865b2e-bba8-4f5a-8756-dd40d5e39f46", # "Korn",
  "b616d6f0-ec1f-4c69-8a79-12a97ece7372", # "Anthrax",
  "dbb3b771-ae77-4381-b61c-758b5b7898ec", # "Death",
  "26f07661-e115-471d-a930-206f5c89d17c", # "Motley Crue",
  "6b335658-22c8-485d-93de-0bc29a1d0349", # "Judas Priest",
  "a466c2a2-6517-42fb-a160-1087c3bafd9f", # "Slipknot",
  "57961a97-3796-4bf7-9f02-a985a8979ae9", # "Motorhead",
  "4bd95eea-b9f6-4d70-a36c-cfea77431553"  # "Alice in Chains"
]

headers={
  "User-Agent" :
  "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}

genres = [
  'popRock',
  'folk',
  'hiphop',
  'metal',
  'electronic',
  'soul',
  'punk',
  'jazz',
  'classical',
  'reggae',
  'blues',
  'country',
  'pop'
]

artistsBumped = 0
for artist in popRock:
  print "------------------------------------------------------------"
  elasticSearchUrl = 'http://localhost:9200/artists/artist/' + artist
  elasticSearchRequest = requests.get(elasticSearchUrl, headers=headers)
  jsonResponse = json.loads(elasticSearchRequest.content)
  try:
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
        if len(releaseGroups) > 0:
          print "-- Saving release groups: ", len(releaseGroups)
          for releaseGroup in releaseGroups:
            writeLog('release-group', "'" + releaseGroup['id'] + "'" + " # " + releaseGroup['title'])

          # call last fm and get all related artists and log those to a file (to be run against this script later)
          lastFmSimilarArtistsUrl = "http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&mbid=" + artist + "&api_key=57ee3318536b23ee81d6b27e36997cde&format=json"
          lastFmSimilarArtistsRequest = requests.get(lastFmSimilarArtistsUrl, headers=headers)
          lastFmJsonSimilarArtistsResponse = json.loads(lastFmSimilarArtistsRequest.content)
          similarArtists = lastFmJsonSimilarArtistsResponse['similarartists']['artist']
          print "-- Saving similar artists: ", len(similarArtists)
          for artist in similarArtists:
            try:
              if artist['mbid']:
                writeLog('similar-artist', "'" + artist['mbid'] + "',")
            except:
              continue
        else:
          writeLog("no-release-groups-found", "'" + artist['mbid'] + "'")
      except urllib2.HTTPError, e:
        print "-- Some error in bumping view score or getting release data"
        writeLog('error-check-artist-bump', artist)
    else :
      # log that artist has been already bumped
      writeLog('artist-already-bumped', artist)
      print "--", jsonResponse['_source']['name'], "already bumped, views:", jsonResponse['_source']['views']
    time.sleep(2)
  except:
    writeLog('mbid-not-found-in-index', artist)
    print "-- Mbid not found in elasticsearch index"
