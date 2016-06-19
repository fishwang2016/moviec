# -*- coding: utf-8 -*-


"""
Created on Mon Jun 13 13:18:18 2016

@author: Fish_user

This file is to extract movie data from eachi link in the data base;

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


# 正则表达式提取名字,中文需要前面加u
rcn_name = re.compile(ur'.*译.*名.?|：')
ren_name = re.compile(ur".*片.*名.?|：")
ryn_name = re.compile(ur"原.*名.?|：")
ryear = re.compile(ur"年.*代.?|：")
rcountry = re.compile(ur"国.*家.?|：")
rcategory = re.compile(ur"类.*别.?|：")
rlanguage = re.compile(ur"语.*言.?|：")
rlan_script = re.compile(ur"字.*幕.?|：")
rimdb_score = re.compile(ur"(.*imdb..?)|：",re.IGNORECASE)
rfile_format = re.compile(ur".*文件格式..?|：")
rvideo_size = re.compile(ur".*视频尺寸..?|：")
rcd_numbers = re.compile(ur".*文件大小..?|：")
rvideo_length = re.compile(ur"片.*长.?|：")
ractors = re.compile(ur"主.*演.?|：")
rdirector = re.compile(ur"导.*演.?|：")

rcn_name1 = re.compile(ur"译.*名")
ren_name1 = re.compile(ur"片.*名")
ryn_name1 = re.compile(ur"原.*名")

ryear1 = re.compile(ur"年.*代")
rcountry1 = re.compile(ur"国.*家")
rcategory1 = re.compile(ur"类.*别")
rlanguage1 = re.compile(ur"语.*言")
rlan_script1 = re.compile(ur"字.*幕")
rimdb_score1 = re.compile(ur"IMDB")
rfile_format1 = re.compile(ur"文件格式")
rvideo_size1 = re.compile(ur"视频尺寸")
rcd_numbers1 = re.compile(ur"文件大小")
rvideo_length1 = re.compile(ur"片.*长")
ractors1 = re.compile(ur"主.*演")
rdirector1 = re.compile(ur"导.*演")




def strip_off(str):
    """
    input a string with mess characters
    return a clean string
    """
    new_str = re.sub("[【 ，•。？、~@#￥%……&*（）】]+".decode("utf8"), "".decode("utf8"),str).strip()
    return new_str

def check_item(item, regular_ex):
    """
    input the item , and regular expression rule
    output the end position of the match
    """
    return regular_ex.search(item[:10])


def get_category(item,regular_ex):
    """
    output the spring results for each item.
    """
    print "checking category"
    return regular_ex.split(item)[-1]
    


def get_detail(movie_content):
    cn_name=''
    en_name=''
    country=''
    year = ''
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

    print "checking movie items"

    print "printing item "

    print movie_content

    for item in movie_content:
        if  check_item(item,rcn_name1):

            cn_name = get_category(item,rcn_name)
            continue
        elif check_item(item,ren_name1):

            en_name =  get_category(item,ren_name)
            continue
        elif check_item(item,ryn_name1):

            en_name =  get_category(item,ryn_name)
            continue
        elif check_item(item,ryear1):
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
        elif item[0:5]==u"　　　　　" :
            actors.append(item.strip())
            continue

        elif len(item) > 65:
            description.append(item.strip())
            continue

    return  (cn_name,en_name,country,year,category,language,lan_script,imdb_score,file_format,video_size,cd_numbers,video_length, director,description,actors)


try:
    from bs4 import UnicodeDammit             # BeautifulSoup 4

    def decode_html(html_string):
        converted = UnicodeDammit(html_string)
        if not converted.unicode_markup:
            raise UnicodeDecodeError(
                "Failed to detect encoding, tried [%s]",
                ', '.join(converted.tried_encodings))
        # print converted.original_encoding
        return converted.unicode_markup

except ImportError:
    from BeautifulSoup import UnicodeDammit   # BeautifulSoup 3

    def decode_html(html_string):
        converted = UnicodeDammit(html_string, isHTML=True)
        if not converted.unicode:
            raise UnicodeDecodeError(
                "Failed to detect encoding, tried [%s]",
                ', '.join(converted.triedEncodings))
        # print converted.originalEncoding
        return converted.unicode




def get_movie(url):
    print " extracting content "
   
    cn_name=''
    en_name=''
    country=''
    year = ''
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

    response = requests.get(url)

    data = response.content
    #data = data.decode(response.encoding)  # This is a file to ensure Chiness characthers can be encode correctly so that the tree is correct.
    tree = html.fromstring(decode_html(data))

    movie_content = tree.xpath("//*[@id='Zoom']//text()")
    print movie_content
    (cn_name, en_name,country,year,category,language, lan_script,imdb_score,file_format,video_size,cd_numbers, video_length,director,description,actors)  = get_detail(movie_content) 
   # for content in movie_content:
       # print content 
    #image lins
    image_links =  tree.xpath("//p/img/@src")
    #download urls
    links = tree.xpath("//td/a/@href")
    download_urls = [link for link in links if link.startswith("ftp")]
    # database handling
   # query ='insert into dytt values (%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,  %s,%s,%s,%s, %s,%s,%s,%s)'
    #data = (cn_name, en_name,country,year,category,language,  lan_script,imdb_score,file_format,video_size, cd_numbers, video_length,director,description,actors,image_links,download_urls,url)

    #c.execute(query,data)
   # conn.commit()


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



if  __name__ == "__main__":

    conn = psycopg2.connect("dbname='movie'")
    c = conn.cursor()
    c.execute("select url from links")
    urls = c.fetchall()
    urls = [url[0] for url in urls]
    i = 0
    print "begins "
    # use integer instead of int
    # c.execute("""create table dytt (cn_name text,
    #       en_name text,
    #       country text,
    #       year text, 
    #       category text ,
    #       language text,
    #       lan_script text,
    #       imdb_score text,
    #       file_format text,
    #       video_size text,
    #       cd_numbers text,
    #       video_length text,
    #       director text,
    #       description text [],
    #       actors text [],  
    #       image_links text [],
    #       download_urls text [],
    #       url text 

    #     );""")

    # print "done"
  
    # for url in urls:


    #     print "Trying No. %d" % i
    #     i = i+1

    #     try:
        

         
    #         get_movie(url)

    #     except Exception as e:
    #         print "error %s XXXXXXXXXXXX" % url 
    #         print e.message


    url ="http://www.dytt8.net/html/gndy/dyzz/20160519/51013.html"
    get_movie(url)



    conn.close()






#
