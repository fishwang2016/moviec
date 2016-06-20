# -*- coding: utf-8 -*-


"""
Created on Mon Jun 13 13:18:18 2016

@author: Fish_user
"""
# encode setting
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# above codes turn out to work for encoding Chinese characters
import requests
from lxml import html
import urlparse
import collections
import re
import psycopg2


def download_image(parsed_body,response):
    """
    input original tree body and url
    download images in downloaded_imagels directory.
    Need to create a dir before using this code

    """


    # Grab links to all images
    images = parsed_body.xpath('//img/@src')
    if not images:
        sys.exit("Found No Images")

    # Convert any relative urls to absolute urls
    images = [urlparse.urljoin(response.url, url) for url in images]
    print 'Found %s images' % len(images)

    # Only download first 10
    for url in images[0:10]:
        r = requests.get(url)
        f = open('downloaded_images/%s' % url.split('/')[-1], 'w')
        f.write(r.content)
        f.close()

if '__name__' == "__main__":

    url =""
    download_image(url)

    