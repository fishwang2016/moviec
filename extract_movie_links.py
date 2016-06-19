# -*- coding: utf-8 -*-
""""
This file is to get all target links.

"""

import re
import lxml
import requests
from lxml import html  
import collections
import urlparse

import psycopg2

rule =r'(oumeitv|gndy).*(\.html)$'

def get_links(STARTING_URL):
        urls_queue = collections.deque()
        urls_queue.append(STARTING_URL)
        found_urls = set()
        found_urls.add(STARTING_URL)

        conn = psycopg2.connect("dbname='movie'")

        c = conn.cursor()
        c.execute("""create table links(

                id int,
                url text
                 ) 

                  """ )
        i = 0

                              
        while len(urls_queue):
              search_domain =re.sub("(http://|http://www\\.|www\\.)","",STARTING_URL).split('/')[0]
              url = urls_queue.popleft()  

              try:
                        response = requests.get(url)
                        if re.search(rule, url):

                           #print "url good!! ",url
                           print "This is No. "+ str(i)+ " input!"
                           query = "insert into links values(%s, %s)"
                           data = (i,url)
                           c.execute(query,data)
                           i=i+1
                           conn.commit()

                        html_tree = html.fromstring(response.content)
                        urls = html_tree.xpath('//a/@href')
                        links = {urlparse.urljoin(response.url, url) for url in urls if urlparse.urljoin(response.url, url).startswith('http')}


                       # SetS difference to find new URLs
                        for link in (links - found_urls):
                               if search_domain in link:
                                      found_urls.add(link)
                                      urls_queue.append(link)
                               else:
                                      found_urls.add(link)


              except Exception as e:
                    print "error.. : ", url
                    print e.message
        conn.close()
        return 

url = "http://www.dytt8.net/html/gndy/dyzz/20160522/51028.html"

get_links(url)

    
