"""
spotify_youtube_downloader.py
-----------------------------
Command-line tool to download songs or playlists from Spotify and YouTube as MP3 files.
Author: SoundIsOff (https://github.com/SoundIsOff)
"""

import os
import time
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from pathlib import Path


# Config 
load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET
    )
)


def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def get_playlist_tracks(playlist_url):
    try:
        results = sp.playlist_tracks(playlist_url)
        tracks = []
        for item in results['items']:
            track = item['track']
            title = track['name']
            artist = track['artists'][0]['name']
            tracks.append(f"{artist} - {title}")
        return tracks
    except spotipy.exceptions.SpotifyException as e:
        print(f"[ERROR] Could not retrieve the playlist: {e}")
        return []


def download_mp3(song_or_url, destination_folder):

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'cachedir': False,
        'retries': 10,
        'quiet': True, 
        'no_warnings': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch:{song_or_url}"])


def download_spotify_playlist(playlist_url, destination_folder):

    playlist_name = sp.playlist(playlist_url)['name']
    playlist_name = sanitize_filename(playlist_name)
    playlist_folder = os.path.join(destination_folder, playlist_name)
    os.makedirs(playlist_folder, exist_ok=True)

    tracks = get_playlist_tracks(playlist_url)
    if not tracks:
        print("[INFO] No tracks found in the playlist.")
        return

    for song in tracks:
        print(f"Downloading: {song}")
        download_mp3(song, playlist_folder)
        time.sleep(0.5)  

    print(f"Download completed!")


# ------------------------------------

if __name__ == "__main__":
    print("[=== Spotify/YouTube MP3 Downloader ===]\n")
    print("1. Download a Spotify playlist")
    print("2. Download a YouTube video or song\n")

    choice = input("Select an option (1/2): ")
    folder = str(Path.home() / "Downloads")

    if choice == "1":
        url = input("Enter a Spotify playlist URL: ").strip()
        download_spotify_playlist(url, folder)
    elif choice == "2":
        url = input("Enter a YouTube URL or song name: ").strip()
        download_mp3(url, folder)
        print("\nDownload completed.")
    else:
        print("Invalid option.")
