import peewee
from models import Album, Artist


def main():
    band = Artist.select().where(Artist.name == "Kutless").get()
    print("[+] found: " + band.name)


if __name__ == '__main__':
    main()