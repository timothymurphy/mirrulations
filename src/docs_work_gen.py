#!/usr/bin/env python
import requests
import os
import random
import string
import redis
import redis_manager
import endpoints


def monolith():
    """
    Runs the script. This is one monolithic function (aptly named) as the script just needs to be run; however, there is a certain
    point where I we need to break out of the program if an error occurs, and I wasn't sure how exactly sys.exit() would work and whether
    or not it would mess with things outside of / calling this script, so I just made one giant method so I can return when needed.
    :return:
    """

    url_base = "https://api.data.gov/regulations/v3/documents.json?rpp=1000"

    r = redis_manager.RedisManager(redis.Redis())

    # The docs_count file keeps track of where we are in regards to the number of things available to download
    key_file = 'docs_count.txt'
    try:
        file = open(key_file, "r+")
    except:
        file = open(key_file, "w+")

    home = os.getenv("HOME")
    with open(home + '/.env/regulationskey.txt') as f:
        regulations_key = f.readline().strip()

    # Getting where we are in the number of files to be downloaded, from the docs_count file
    current_page = file.readline().replace("\n","")
    if current_page == '':
        current_page = 0
    else:
        current_page = int(current_page)

    if regulations_key != "":
        # Gets number of documents available to download
        try:
            record_count = requests.get("https://api.data.gov/regulations/v3/documents.json?api_key=" + regulations_key + "&countsOnly=1").json()["totalNumRecords"]
        except:
            print("Error occured with docs_work_gen regulations API request.")
            return 0

        # Gets the max page we'll go to; each page is 1000 documents
        max_page_hit = record_count // 1000

        # This loop generates lists of URLs, sending out a job and writing them to the work server every 1000 URLs.
        # It will stop and send whatever's left if we hit the max page limit.
        while(current_page < max_page_hit):
            url_list = []
            for i in range(1000):
                current_page += 1
                url_full = url_base + "&po=" + str(current_page * 1000)

                url_list.append(url_full)

                if current_page == max_page_hit:
                    break

            # Makes a JSON from the list of URLs and send it to the queue as a job
            docs_work = [''.join(random.choices(string.ascii_letters + string.digits, k=16)), "docs", url_list]
            r.add_to_queue(endpoints.generate_json(docs_work))

        # Saving our new page index
        file_writable = open(key_file, "w")
        file_writable.write(str(current_page))
        file_writable.close()
    else:
        print("No API Key!")

    file.close()


monolith()
