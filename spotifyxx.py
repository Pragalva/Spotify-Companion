#Pragalva Dhungana 6/3/2020
#This program was made by following tutorial on spotipy by Ian Annase
#This code is a modification and extention of his code
import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

#Get username
username = sys.argv[1]
scope = 'user-read-private user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private'

# Erase cache and prompt for permission
try:
    token = util.prompt_for_user_token(username, scope)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope)

# Create spotifyObject
spotifyObject = spotipy.Spotify(auth=token)

# Get current device
devices = spotifyObject.devices()
deviceID = devices['devices'][0]['id']

#User info
user = spotifyObject.current_user()
#print(json.dumps(user, sort_keys=True, indent=4))

displayName = user['display_name']
followers = user['followers']['total']
userID = user['id']

#Main Loop
while True:
    print()
    print("Welcome to Spotipy " + displayName)
    print("You have " + str(followers) + " followers.")
    print()

    # Current track information
    track = spotifyObject.current_user_playing_track()
    #print(json.dumps(track, sort_keys=True, indent=4))

    if track is not None:
        artist = track['item']['artists'][0]['name']
        track = track['item']['name']
        print("You are currently listining to " + artist + " - " + track)
    print()
    print("What would you like to do ?")
    print("0 - Search for an artist")
    #print("1 - Manage playlists")
    print("9 - Exit")
    print()
    choice = input("Your Choice: ")

    #Search for artist
    if choice == "0":
        print()
        searchQuery = input("What artist do you want to search ? ")
        print()

        #Get search results
        searchResults = spotifyObject.search(searchQuery,1,0,"artist")
        #print(json.dumps(searchResults, sort_keys=True, indent=4))

        #Artist details
        print("The artist that we have found is ")
        artist = searchResults['artists']['items'][0]
        print(artist['name'])
        print(str(artist['followers']['total']) + " followers")
        print(artist['genres'][0])
        print()
        print("Here are all the songs we found in the artists page")
        #webbrowser.open(artist['images'][0]['url'])
        artistID = artist["id"]

        #Album and track details
        trackURIs =[]
        trackArt =[]
        index = 0

        #function for printing tracks in an album
        #Discalimer!!!! Since Global is used do not use it for other purposes
        def print_tracks(lookupResult):
            #Global variable index is used this function
            global index
            global trackURIs
            global trackArt

            for item in lookupResult:
                print("ALBUM: " + item['name'])
                albumID = item['id']
                albumArt = item ['images'][0]['url']

                #extract track data
                trackResults = spotifyObject.album_tracks(albumID)
                trackResults = trackResults['items']

                for item in trackResults:
                    print(str(index)+ ": " + item['name'])
                    trackURIs.append(item['uri'])
                    trackArt.append(albumArt)
                    index+=1
                print()


        #Album details
        albumResults = spotifyObject.artist_albums(artistID,'album')
        albumResults = albumResults['items']
        print_tracks(albumResults)

        #Singles
        singleResults = spotifyObject.artist_albums(artistID,'single')
        singleResults = singleResults['items']
        print_tracks(singleResults)

        #See album art
        print("What would you like to do ?")
        print("0 - Listen to songs on your current devive")
        print("1 - Make playlist and current artist's songs")
        print("9 - Exit")
        print()
        choice2 = input("Your Choice: ")

        #Play songs
        if choice2 == "0":
            while True:
                playSelection = input("Enter a song number to see album art and play the song (x to exit): ") # and play the song
                if playSelection == "x":
                    break
                playSelectionList = []
                playSelectionList.append(trackURIs[int(playSelection)])
                spotifyObject.start_playback(deviceID, None, playSelectionList) # added
                webbrowser.open(trackArt[int(playSelection)])

        #Make playlist
        if choice2 == "1":
            print()
            playlist_name = input("What would you like to name the playlist? ")
            spotifyObject.user_playlist_create(userID,playlist_name)
            print()

            #plalist details
            playlistResult = spotifyObject.user_playlists(userID)
            #print(json.dumps(playlistResult, sort_keys=True, indent=4))
            createdPlaylist_id = playlistResult["items"][0]["id"]

            #Add songs
            while True:
                songSelection = input("Enter a song number to add to the playlist (x to exit): ")
                if songSelection == "x":
                    break
                trackSelectionList = []
                trackSelectionList.append(trackURIs[int(songSelection)])
                spotifyObject.user_playlist_add_tracks(userID,createdPlaylist_id,trackSelectionList)

            #Exit
            if choice2 =="9":
                break
    #Exit
    if choice == "9":
        break

# print(json.dumps(VARIABLE, sort_keys=True, indent=4))
