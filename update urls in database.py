# -*- coding: utf-8 -*-
import hashlib
import re
import psycopg2
import requests
from lxml import html
import urlparse
import collections
conn = psycopg2.connect("dbname='movie'")
c = conn.cursor()

c.execute("select md5(url) from links ")
md5_url = c.fetchall()
md5_url =[m[0] for m in md5_url]
print md5_url

def get_links(start_url):
    base_url = re.sub("(http://|http://www\\.|www\\.)","",start_url).split('/')[0]
    urls_queue = collections.deque()
    urls_queue.append(start_url)
    found_urls = set()
    found_urls.add(start_url)
    print base_url
    i =13000
    rule = r'.*(index.html)$'
    rule2 =r'gndy|oumeitv'
    r='^[A-Za-z][\\.:\/A-Za-z0-9]*$'# only accepts english website
    while len(urls_queue):

        url = urls_queue.popleft()
        print "Total " ,str(len(urls_queue)), " to crawl."
        i = i +1
        print "checking No. %s links" % str(i)
        if re.search(r,url):
               if (hashlib.md5(url).hexdigest() not in md5_url)  :
                   
                    try: 
                        response = requests.get(url)                                           
                        tree = html.fromstring(response.content)                                     
                        links = tree.xpath("//a/@href")                                              
                       # print links
                        if (not re.search(rule,url)) and re.search(rule2,url):
                            print "satisfied url %s *********" % url
                            query = 'insert into links values( %s,%d)'
                            data = (url,i)
                            c.execute(query,data)
                            conn.commit()
                        #print response.url
                                                                                                      
                        #print urlparse.urljoin(response.url,links[1])
                        links ={urlparse.urljoin(response.url,url) for url in links                  
                                      if urlparse.urljoin(response.url, url).startswith("http")}     
                        for link in (links - found_urls):                                            
                            if (base_url not in link): 
                                print "XXXX: get rid of: %s XXXXXXXX "%link
                                found_urls.add(link)                                              
                            else:                                                                    
                                urls_queue.append(link)                                              
                                found_urls.add(link)                                              
                    except Exception as e:
                        print "error opening page -%s EEEEEEEEEEEE"% url
       
       
    conn.close()             
    print "done"
url ="http://www.dytt8.net"
get_links(url)
