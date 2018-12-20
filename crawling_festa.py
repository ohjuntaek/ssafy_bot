import json
import re
import requests
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver

def _crawl_festa(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    req = urllib.request.Request(url, headers=headers)
    
    # html = requests.get(url, headers = headers)
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html.text,"lxml")

    driver = webdriver.Chrome("./chromedriver.exe")
    driver.get(url)
    driver.find_element_by_id("root").click()
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    # print(soup)
    keywords = [i.get_text() for i in soup.find_all("h3", class_=re.compile(r'sc-.+'))]
    print("keywords",keywords)
    links = [i.get("href") for i in soup.find_all("a", class_="sc-iQKALj lhBWTX")]
    print("links",links)
    idkeywords = [str(i+1)+":"+keywords[i] for i in range(len(keywords))]
    
    idkeywordslinks = [idkeywords[i]+"\n 링크 : https://festa.io"+links[i] for i in range(len(min(keywords,links)))]
    # print(keywords[0], links[0], len(keywords), len(links), len(idkeywords))

    print('LOG : print return')

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(idkeywordslinks)

def _crawl_okky(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    html = requests.get(url, headers = headers)
    soup = BeautifulSoup(html.text,"html.parser")
    print(soup)


# _crawl_festa("https://festa.io")
_crawl_okky("https://okky.kr/articles/gathering")