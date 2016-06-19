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
                   print  url
               # Find all links
               urls = parsed_body.xpath('//a/@href')
               links = {urlparse.urljoin(response.url, url) for url in urls if urlparse.urljoin(response.url, url).startswith('http')}


               # Set difference to find new URLs
               for link in (links - found_urls):
                         if search_domain in link:
                              found_urls.add(link)
                              urls_queue.append(link)
                         else:
                              found_urls.add(link)

        except Exception as e:

             print "error  "+ url
             print e.message
             pass

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

def strip_off(str):
    """
    input a string with mess characters
    return a clean string
    """
    new_str = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！：【... ，•。？、~@#￥%……&*（）】]+".decode("utf8"), "".decode("utf8"),str).strip()
    return new_str


def get_category(item,regular_ex):
    """
    output the spring results for each item.
    """

    m = regular_ex.search(item[:8])
    if m:
        index =m.span()[-1]

        return strip_off(item[index:])
    else:
        return "!nothing"
    


def check_item(item, regular_ex):
    """
    input the item , and regular expression rule
    output the end position of the match
    """
    return regular_ex.search(item[:10])



def get_movie(url):

    """
    extract features of each movie

    """
    cn_name=''
    en_name=''
    country=''
    year=''
    category=''
    language=''
    lan_script=''
    imdb_score=''
    file_format=''
    video_size=''
    cd_numbers=''
    video_length=''
    director=''
    description =[]
    actors =[]

    # 正则表达式提取名字,中文需要前面加u
    rcn_name = re.compile(ur"译.*名")
    ren_name = re.compile(ur"片.*名")
    ryn_name = re.compile(ur"原.*名")

    ryear = re.compile(ur"年.*代")
    rcountry = re.compile(ur"国.*家")
    rcategory = re.compile(ur"类.*别")
    rlanguage = re.compile(ur"语.*言")
    rlan_script = re.compile(ur"字.*幕")
    rimdb_score = re.compile(ur"IMDB")
    rfile_format = re.compile(ur"文件格式")
    rvideo_size = re.compile(ur"视频尺寸")
    rcd_numbers = re.compile(ur"文件大小")
    rvideo_length = re.compile(ur"片.*长")
    ractors = re.compile(ur"主.*演")
    rdirector = re.compile(ur"导.*演")


    html_tree,response_page = parse_html(url)

    movie_content = html_tree.xpath("//*[@id='Zoom']//p/text()")


    for item in movie_content:
        if  check_item(item,rcn_name) :

            cn_name = get_category(item,rcn_name)
            continue
        elif check_item(item,ren_name):

            en_name =  get_category(item,ren_name)
            continue
        elif check_item(item,ryn_name):

            en_name =  get_category(item,ryn_name)
            continue
        elif check_item(item,ryear):
            year =  get_category(item,ryear)
            continue
        elif check_item(item,rcountry):
            country =  get_category(item,rcountry)
            continue
        elif check_item(item,rcategory):
            category = get_category(item,rcategory)
            continue

        elif check_item(item,rlanguage):
            language =  get_category(item,rlanguage)
            continue

        elif check_item(item,rlan_script):
            lan_script =  get_category(item,rlan_script)
            continue

        elif check_item(item,rimdb_score):
            imdb_score =  get_category(item,rimdb_score)
            continue

        elif check_item(item,rfile_format):
            file_format =  get_category(item,rfile_format)
            continue
        elif check_item(item,rvideo_size):
            video_size =  get_category(item,rvideo_size)
            continue
        elif check_item(item,rcd_numbers):
            cd_numbers =  get_category(item,rcd_numbers)
            continue

        elif check_item(item,rvideo_length):
            video_length =  get_category(item,rvideo_length)
            continue

        elif check_item(item,rdirector):
            director =  get_category(item,rdirector)
            continue
        elif check_item(item,ractors):
            actors.append(get_category(item,ractors))
            continue
        elif item[0:5]==u"　　　　　":
            actors.append(item[5:].strip())
            continue

        elif len(item)>65:
            description.append(item.strip())
            continue

    #image lins
    image_links =  html_tree.xpath("//p/img/@src")

    #download urls
    links = html_tree.xpath("//td/a/@href")
    download_urls = [link for link in links if link.startswith("ftp")]
    print u"中文： ",cn_name
    print u"英文： ",en_name
    print u"国家： ",country
    print u"年代： ",year
    print u"类别： ",category
    print u"语言： ",language
    print u"字幕： ",lan_script
    print u"imdb： ",imdb_score
    print u"文件格式： ",file_format
    print u"视频尺寸： ",video_size
    print u"文件大小： ",cd_numbers
    print u"片长： " , video_length
    print  u"导演： ",director.decode("utf8")
    print u"主演： "
    for actor in actors:
        print actor
        print "****"
    print u"简介： "
    for de in description:
        print  de
    print u"下载链接： "
    for d in download_urls:
        print d
    print u"图片链接： "
    for img in image_links:
        print img


url="http://www.dytt8.net/html/tv/rihantv/20160329/50579.html"
get_movie(url)

class Movie():
    """
     This is a movie class for future use.
    """
    def __init__(self,cn_name,en_name,year,country,category="",language="",language_script="",show_time="",IMDB_score="",video_size="",file_format="",length="",

                 director="",actors=[],description="",download_urls=[],images_urls=[]):

        self.cn_name = cn_name
        self.en_name = en_name
        self.year = year
        self.country = country
        self.category = category
        self.language = language
        self.lan_script = language_script
        self.show_time = show_time
        self.IMDB_score = IMDB_score
        self.file_format = file_format
        self.video_size = video_size
        self.video_length = video_length
        self.cd_numbers = cd_numbers
        self.actors = actors
        self.description = description
        self.download_urls = download_urls
        self.images_urls = images_urls




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
