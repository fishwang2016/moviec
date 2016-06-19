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
    c.execute("""CREATE TABLE blog(id int, title text,url text, content text[], images text[],primary key (id))""")
    i = 0
    rule = r".*\/$" # ends with /
    rule2 = r'page|tag|category|.*(\/\d{2}\/)$' # category ,tag, monthly-date
    rule3 = r'(\.org)$|(\.org\/)$' # home page
    while len(urls_queue):
        url = urls_queue.popleft()
        
        if re.search(rule, url) and (not re.search(rule2,url)):

            try:

               response = requests.get(url)
               if response.ok :
                   parsed_body = html.fromstring(response.content)

                   if not re.search(rule3,url):
                       # Prints the page title

                       title =parsed_body.xpath('//header//h1/text()')[0]
                       content = parsed_body.xpath("//*[@class='entry-content']/p/text()")
                       images = parsed_body.xpath("img/@src")
                       if len(title)>0 and len(content):
                           #print title, url
                           print "inserting item no.  "+str(i)+" into database.!" 
                           query = "INSERT INTO blog VALUES(%s,%s,%s,%s,%s);"
                           data=(i,title,url,content,images)
                           c.execute(query,data)
            #           with codecs.open("titles.txt",mode="a",encoding="utf-8") as f:
             #              f.write(title+"\n")
              #             f.close()
                       # Find all links
                       conn.commit()
                   else:
                        print url 


                   urls = parsed_body.xpath('//a/@href')
                   links = {urlparse.urljoin(response.url, url) for url in urls if urlparse.urljoin(response.url, url).startswith('http')}


                   # SetS difference to find new URLs
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


STARTING_URL = "http://www.xiaoxia.org/"
print_page_title(STARTING_URL)


