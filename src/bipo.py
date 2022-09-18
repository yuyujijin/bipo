
from __future__ import unicode_literals
import youtube_dl
from typing import List, Tuple
from mxlrc import *
import time
from pytube import Search
import pygame


def download_song(song : str, filename : str) -> bool:
    # Looking for the song
    results = Search(song).results
    if len(results) < 1:
        return False

    url = f"https://www.youtube.com/watch?v={ results[0].vid_info['videoDetails']['videoId'] }"

    print(f"\nStarting download of '{song}' ({url})...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'downloads/{filename}.%(ext)s'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return True

def print_lyrics(lyrics : List[str], filename : str = None) -> None:
    if filename == None:
        print("Filename is None, stopping...")
        return

    input('\nPress a key when ready to start...')
    print('\n[*] Starting lyricing...')
    n = 0

    # Five first line are song description
    for line in lyrics[:5]:
        # Skip first line (hehe)
        if n == 0:
            pass
        # Else we show the song description
        else:
            # Remove the brackets
            line = line[1:-2]
            # Split with the first ':'
            idx = line.find(':')
            line = [line[:idx], line[idx + 1:]]
            # Descriptors
            desc = {'ar' : 'Artist', 'ti' : 'Title', 'al' : 'Album', 'length' : 'Length'}
            print(f"{desc[line[0]]} : {line[1]}")
        n += 1

    # Now lyricing

    # Start the song
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Start the timer for sync
    start = time.perf_counter()
    idx = 5

    while idx < len(lyrics):
        lyric = lyrics[idx]

        timestamp = lyric[1 : lyric.find(']')]
        timestamp = float(timestamp[:2]) * 60 + float(timestamp[3:5]) + float(timestamp[6:]) * .01

        now = time.perf_counter()
        elapsed = now - start

        if(elapsed >= timestamp):
            print(lyric[lyric.find(']') + 1:])
            idx += 1

def generate_clip(songs: List[Tuple[str, str]] = None, filenames : List[str] = None) -> None:
    for (artist, song), filename in zip(songs, filenames):
        filename = f"lyrics/{str(filename).replace(',','')}.lrc"
        with open(filename, "r") as f:
            # Download the song and put it in /downloads
            if not download_song(f"{artist} - {song}", f"{artist}{song}"):
                print(f"Error while downloading {filename}, stoping...")
            # Print the lyrics synced to the song
            print_lyrics(f.readlines(), filename = f"downloads/{artist}{song}.mp3")
            

if __name__ == "__main__":
    rename_logging_level_names()
    args = parse_args()
    logging_level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format='%(levelname)s %(message)s', level=logging.DEBUG if args.debug else logging_level)
    args = init_args(args)
    if args is not None:
        print(f"\n{args.songs['count']} lyrics to fetch")
        
        success, filenames = main(args)
        if success:
            songs = list(map(lambda x : (x[0].strip(), x[1].strip()), zip(args.songs['artists'], args.songs['titles'])))
            generate_clip(songs, filenames)