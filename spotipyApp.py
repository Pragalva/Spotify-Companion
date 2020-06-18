#Pragalva Dhungana 6/3/2020
#This program was inspired by a tutorial on spotipy by Ian Annase
#This code is a modification and extention of his code
import os
import sys
import json
import spotipy
import webbrowser
import math
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

#functions used
def makeplaylist(userID,trackURI):
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
        songSelection = input("Enter a song number to add to the playlist (a for all songs and x to exit): ")
        if songSelection == "x":
            break
        if songSelection =="a":
            tracklen = len(trackURI)
            if (tracklen < 100):
                spotifyObject.user_playlist_add_tracks(userID,createdPlaylist_id,trackURI)
                print()
                print("A playlist with all the songs has been created")
                break
            else:
                tindex = math.ceil(tracklen/100)
                start = 0
                end = 100
                for x in range(tindex):
                    spotifyObject.user_playlist_add_tracks(userID,createdPlaylist_id,trackURI[start:end])
                    start+= 100
                    end+=100
                print()
                print("A playlist with all the songs has been created")
                break
        trackSelectionList = []
        trackSelectionList.append(trackURI[int(songSelection)])
        spotifyObject.user_playlist_add_tracks(userID,createdPlaylist_id,trackSelectionList)

#Main Loop
while True:
    print()
    print("Welcome to Spotipy " + displayName)
    print("You have " + str(followers) + " followers.")
    print()

    # Current track information
    track = spotifyObject.current_user_playing_track()
    #print(json.dumps(track, sort_keys=True, indent=4)
    if track is not None:
        artist = track['item']['artists'][0]['name']
        track = track['item']['name']
        print("You are currently listining to " + artist + " - " + track)

    print()
    print("What would you like to do ?")
    print("0 - Search for an artist")
    print("1 - Manage playlists")
    print("2 - Generate Recommendations Playlist")
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
        #Uses global variable DO NOT USE FOR OTHER ASPECTS
        def print_tracks(lookupResult):

            global trackURIs
            global trackArt
            global index
            #local variables
            printedAlbums =[]

            for item in lookupResult:
                if item['name'] not in printedAlbums:
                    print("ALBUM: " + item['name'])
                    printedAlbums.append(item['name'])
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
        print("1 - Make playlist of current artist's songs")
        print("9 - Go back")
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
            makeplaylist(userID,trackURIs)

            #Exit
            if choice2 =="9":
                print()
    #Manage playlists
    if choice == "1":
        userPlaylist = spotifyObject.current_user_playlists()
        userTotal = userPlaylist["total"]
        userPlaylist = userPlaylist["items"]
        pindex = 0

        print()
        print("You currently have " + str(userTotal) +" Playlists")
        print("Here are all your playlist")

        #Display playlist names
        for item in userPlaylist:
            print(str(pindex) +" "+ item['name'])
            pindex+= 1

        #Playlist Details
        print()
        playlistSelected =input("Which playlist would you like to edit(Enter the number corresponding it) ? ")
        #print(json.dumps(userPlaylist, sort_keys=True, indent=4))
        playlistSelectedURI =userPlaylist[int(playlistSelected)]['uri']
        playlistSelectedID =userPlaylist[int(playlistSelected)]['id']
        print("You have selcted " + userPlaylist[int(playlistSelected)]['name'] )
        print()
        print("How you like to edit this playlist ?")
        print("0 - Upload Playlist Picture")
        print("1 - Edit Name")
        print("2 - Add tracks")
        print("3 - Remove tracks")
        print("9 - Exit")
        choice3 = input("Your Choice: ")
        print()

        #Playlist Choices
        #Edit name
        if choice3 =="0":
            print()

        if choice3 == "1":
            newName = input("What would you like the name the playlist ?")
            print()
            spotifyObject.user_playlist_change_details(userID,playlistSelectedID,newName)

        if choice3 == "9":
            print()
    #Generate Recommendation
    if choice == "2":
        print()
        print("How would like to generate a recommendation ?")
        print("0 - Generate playlist using Similar Artist")
        print("1 - Generate playlist using last played songs")
        print("2 - Generate playlist using your top tracks")
        print("3 - Generate playlist using tracks")
        print()
        choice4 =input("Your choice: ")

        #Generating a playlist using Similar artist in artist bio
        if choice4 == "0":
            print()
            searchQuery = input("What artist do you want to use as seed ? ")
            print()

            #Get search results
            searchResults = spotifyObject.search(searchQuery,1,0,"artist")
            seedartist = searchResults['artists']['items'][0]['id']

            #Variables used in the loop
            relatedArtists = spotifyObject.artist_related_artists(seedartist)
            relatedArtists = relatedArtists['artists']
            relatedArtistID = []
            relatedArtistNames =[]
            songResultName = []
            songResultURI = []
            rindex = 0
            printindex = 0

            print()
            print("Here are a few songs you might like ")
            for item in relatedArtists:

                #Retrive Artist Details
                relatedArtistID.append(relatedArtists[rindex]['id'])
                relatedArtistNames.append(relatedArtists[rindex]['name'])
                print()
                print(relatedArtists[rindex]['name'])

                #Retrive Song details
                songResult = spotifyObject.artist_top_tracks(relatedArtistID[rindex])
                songResult = songResult['tracks']

                #Resets the song index if there is a new artist
                songindex = 0
                for item in songResult:
                    songResultName.append(songResult[songindex]['name'])
                    print(str(printindex)+' '+ songResult[songindex]['name'])
                    songResultURI.append(songResult[songindex]['uri'])
                    songindex+= 1
                    printindex+= 1
                rindex+= 1

            #Playlist Creation
            makeplaylist(userID,songResultURI)


    #Exit
    if choice == "9":
        break

# print(json.dumps(VARIABLE, sort_keys=True, indent=4))
