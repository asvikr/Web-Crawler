"""
fetch data movie file from your folder and five sorted order based on their rating on imdb
"""

import os
import requests
import urllib
import urllib2
from bs4 import BeautifulSoup

BASE_URL = 'http://www.imdb.com'

def find_rating(title):
    """
    :param title:
    :return: rating of given movie
    """
    movie = title
    print movie
    url ="%s/find?s=tt&q=%s" % (BASE_URL, movie)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, "lxml")

    list = soup.find("table", class_="findList")
    actual_url = BASE_URL + list.tr.a["href"]
    new_soup = BeautifulSoup(requests.get(actual_url).content, "lxml")
    rating = new_soup.find("div", class_="ratingValue").get_text().split("/")[0]
    print rating
    return float(rating)


def get_files(path):
    """
    :param path:
    :return: file name of movie(title)
    """
    files = [file.split(".")[0] for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
    return files

def main():
    print "give folder address"
    r = raw_input().split("/")
    path = "/"
    for s in r:
        path = os.path.join(path, s)
    files = []
    if os.path.exists(path):
        files = get_files(path)
    else:
        print "path does not exists"
        return
    movie_data = [(title, find_rating(title)) for title in files]
    movie_data.sort(key = lambda x: x[1], reverse = True)
    print movie_data


if __name__=='__main__':
    main()
