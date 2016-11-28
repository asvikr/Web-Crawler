import os
import youtube_dl
import urllib
import urllib2
import requests
from subprocess import check_output


def main():
    url = raw_input()
    new_url = check_output(["youtube-dl","-g", url])
    title = check_output(["youtube-dl","--get-title", url])
    title = title[:-1] + ".mp4"
    path = os.path.join("..","..","download")

    r = urllib.FancyURLopener()
    file = os.path.join(path, title)
    print "downloaded started"
    r.retrieve(new_url, file)
    print "success"

if __name__=='__main__':
    main()