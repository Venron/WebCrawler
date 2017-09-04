import optparse
from bs4 import *
import requests
import os
import time
import sys
from threading import Thread, Semaphore
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests.packages.urllib3.exceptions import NewConnectionError, MaxRetryError
import getpass
from peewee import *
import peewee

screenLock = Semaphore(value=1)

HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"


def main():
    parser = optparse.OptionParser("usage %prog -r <root url>")
    parser.add_option("-r", dest="root_url", type="string", help="specify parser root url")
    (options, args) = parser.parse_args()
    root_url = options.root_url

    if root_url == None:
        print(parser.usage)
        exit(0)

    # test progress bar

    os.system("cls" if os.name == "nt" else "clear")

    # arr = ["[", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "]"]
    # index = 1
    # for i in range(101):
    #     time.sleep(0.05)
    #     if i % 5 == 0:
    #         if index == 21:
    #             pass
    #         else:
    #             arr[index] = "#"
    #             index += 1
    #     sys.stdout.write("\r%s %d%%" % ("".join(arr), i))
    #     sys.stdout.flush()
    # print("\n")

    db_server = input("Enter database server: ")
    db_name = input("Enter username: ")
    db_password = getpass.getpass()

    print(db_server)
    print(db_name)
    print(db_password)

    print("[+] connecting to database at '" + db_server + "'...")




    input()

    print("[+] parsing url " + root_url + "...")
    complete_urls = crawl_url(url=root_url, stage=0)
    count = 1
    if len(complete_urls) == 0:
        print("[+] no urls found")
    else:
        for url in complete_urls:
            t = Thread(target=crawl_url, args=(url, count))
            t.start()
            count += 1


def crawl_url(url, stage):
    validator = URLValidator()
    screenLock.acquire()
    try:
        validator(url)
        # print("[+] validation of %s successful" % url)
    except ValidationError as e:
        # print("[-] validation for %s failed" % url)
        return

    res = requests.get(url)
    try:
        res.raise_for_status()
        # print("[+] (stage=" + str(stage) + ") download of %s successful" % url)
    except Exception as e:
        print("[-] (stage=%d) download of %s failed: %s" % (stage, url, e))

    print("[+] gathering links from %s..." % url)
    soup = BeautifulSoup(res.text, "html.parser")
    all_links = soup.find_all("a")
    all_links_length = len(all_links)
    print("[+] (stage=" + str(stage) + ") found %d total links" % len(all_links))

    """
        akzeptiere nur Links die mit /<uri> anfangen
    """
    crawl_links = []
    for item in all_links:
        try:
            if item == None or not item.get("href").startswith("/") or item.get("href") == "/":
                del item
            else:
                link = item.get("href")
                crawl_links.append(link)
        except AttributeError as e:
            del item
    complete_urls = []
    print("[+] (stage=" + str(stage) + ") remaining %d/%d links" % (len(crawl_links), all_links_length))
    for item in crawl_links:
        temp = url + item
        complete_urls.append(temp)
    print("[+] (stage=" + str(stage) + ") building new absolute urls (%d)" % len(crawl_links))

    """
        lade die die neuen seiten
    """
    successful_crawls = 0
    for item in complete_urls:
        # print("[*] (stage=" + str(stage) + ") loading %s" % item)
        try:
            res = requests.get(item)
        except ConnectionError as e:
            print("[-] (stage=" + str(stage) + ") (" + FAIL + "timeout" + ENDC + ")" + " download failed: " + str(e))

        try:
            soup = BeautifulSoup(res.text, "html.parser")
            res.raise_for_status()
            if soup.title == None or soup.title.text.strip() == "":
                title = "--- no title set ---"
            else:
                title = soup.title.text.strip()
            print("[*] (stage=" + str(stage) + ") (" + OKGREEN + str(
                res.status_code) + ENDC + ") title=" + title + ", url=" + item)
            successful_crawls += 1
        except ConnectionError as e:
            print("[-] (stage=" + str(stage) + ") (" + FAIL + "timeout" + ENDC + ")" + " download failed: " + str(e))
        except Exception as e:
            print("[-] (stage=" + str(stage) + ") (" + FAIL + str(
                res.status_code) + ENDC + ")" + " download failed: " + str(e))
        screenLock.release()
    # complete_urls.append(successful_crawls)
    # if stage == 0:
    #     return complete_urls[:5]
    # else:
    #     return complete_urls
    screenLock.acquire()
    print("[+]" + WARNING + " ++++++++++++++++++++++++++++++" + ENDC + "\n" + "[+] (stage=" + str(
        stage) + ") done (" + str(
        successful_crawls) + ")" + ENDC + "\n" + "[+]" + WARNING + " ++++++++++++++++++++++++++++++" + ENDC)
    screenLock.release()
    return complete_urls


if __name__ == "__main__":
    main()
