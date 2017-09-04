import sqlite3
import peewee
from models import Album, Artist
import datetime


def main():
    new_artist = Artist.create(name="Newsboys")
    new_album = Album(artist=new_artist,
                      title="Album title",
                      publisher="Sparrow",
                      release_date=datetime.date(1988, 12, 1),
                      media_type="CD",
                      )
    new_album.save()

    # batch save

    albums = [{"artist": new_artist,
               "title": "Hell is for Wimps",
               "release_date": datetime.date(1990, 7, 31),
               "publisher": "Sparrow",
               "media_type": "CD"
               },
              {"artist": new_artist,
               "title": "Love Liberty Disco",
               "release_date": datetime.date(1999, 11, 16),
               "publisher": "Sparrow",
               "media_type": "CD"
               },
              {"artist": new_artist,
               "title": "Thrive",
               "release_date": datetime.date(2002, 3, 26),
               "publisher": "Sparrow",
               "media_type": "CD"}
              ]

    for album in albums:
        a = Album(**album)
        a.save()

    bands = ["MXPX", "Kutless", "Thousand Foot Krutch"]
    for band in bands:
        artist = Artist(name=band)
        artist.save()

    print("[+] done")

if __name__ == '__main__':
    main()
