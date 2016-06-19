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

import codecs
import psycopg2

def print_page_title(STARTING_URL):

    """
    gets all the links and print title and download path
    """
    search_domain =re.sub("(http://|http://www\\.|www\\.)","",STARTING_URL).split('/')[0]
    print search_domain
    urls_queue = collections.deque()
    urls_queue.append(STARTING_URL)
    found_urls = set()
    found_urls.add(STARTING_URL)
    conn = psycopg2.connect("dbname='title'")
    c = conn.cursor()
    #c.execute("""CREATE TABLE title if not exists(id int, title text,url text)""")
    i = 0
    while len(urls_queue):
        url = urls_queue.popleft()
        cookie =''
        try:
           response = requests.get(url)
           if response.ok:
               parsed_body = html.fromstring(response.content)
               # Prints the page title

               title =parsed_body.xpath('//title/text()')[0]
               if len(title)>0:
                   print "inserting item no.  "+str(i)+" into database.!" 
                   query = "INSERT INTO blog VALUES(%s,%s,%s)"
                   data=(i,title,url)
                   c.execute(query,data)
    #           with codecs.open("titles.txt",mode="a",encoding="utf-8") as f:
     #              f.write(title+"\n")
      #             f.close()
               # Find all links
                   conn.commit()
               urls = parsed_body.xpath('//a/@href')
               links = {urlparse.urljoin(response.url, url) for url in urls if urlparse.urljoin(response.url, url).startswith('http')}


               # Set difference to find new URLs
               for link in (links - found_urls):
                         if search_domain in link:
                              found_urls.add(link)
                              urls_queue.append(link)
                         else:
                              found_urls.add(link)
           i += 1
        except Exception as e:

             print "error  "+ url
             print e.message
             pass

    conn.close()
    print "done"



def parse_html(url):
    """
    import url, and return a lxml.html.tree
    try get title using xpath
    for example:
    tree = html.fromstring(pagecontent)
    return title:   tree.xpath('//title/text()')
    return links: tree.xpath(''//a/@href)

    """
    response_page = requests.get(url)
    html_tree = html.fromstring(response_page.content)
    return html_tree, response_page



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

class Movie():
    """
     This is a movie class for future use.
    """
    def __init__(self,cn_name,en_name,year,country,category,language,show_time,IMDB_score,total_number,length,

                 director,actors,description,urls):

        self.cn_name = cn_name
        self.en_name = en_name
        self.year = year
        self.country = country
        self.category = category
        self.language = language
        self.show_time = show_time
        self.IMDB_score = IMDB_score
        self.total_number = total_number
        self.length = length
        self.director = director
        self.actors = actors
        self.description = description
        self.urls = urls


STARTING_URL = 'http://xiaoxia.org'.strip()# need to strip space
print_page_title(STARTING_URL)


def useful_stuff(url):
    """
    useful tips
    """
    response = requests.get(url)
    # Response
    print response.status_code # Response Code
    print response.headers # Response Headers
    print response.content # Response Body Content

    # Request
    print response.request.headers # Headers you sent with the request
    #use proxy
    proxy = {'http' : 'http://102.32.3.1:8080',
           'https': 'http://102.32.3.1:4444'}
    response = requests.get('http://jakeaustwick.me', proxies=proxy)
#
#
#    import redis
#    import requests
#    from readability.readability import Document
#
#    r = redis.StrictRedis()
#
#    def urls():
#        for url in open('urls.txt', 'r'):
#            if not r.hexists('url-content', url):
#                yield url
#
#    if __name__ == '__main__':
#        for url in urls():
#            try:
#                response = requests.get(url, timeout=10)
#
#                # Only store the content if the page load was successful
#                if response.ok:
#                    page_content = Document(response.content).summary()
#                    r.hset('url-content', url, page_content)
#            except:
#                print 'Error processing URL: %s' % url
#
#        print 'Processed all URLs'
