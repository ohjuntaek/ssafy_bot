import json
import re
import requests
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver

def _crawl_festa(url):
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': '_ga=GA1.2.618591872.1545294432; _gid=GA1.2.272050992.1545294432',
    'Host': 'okky.kr',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    
    # html = requests.get(url, headers = headers)
    # html = urllib.request.urlopen(req).read()
    # soup = BeautifulSoup(html.text,"lxml")

    #Headless
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome("./chromedriver.exe", chrome_options=options)
    driver.get(url)
    driver.implicitly_wait(3)
    driver.find_element_by_id("root").click()
    html = driver.page_source
    driver.quit()

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
    # headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    # 'Accept-Encoding': 'gzip, deflate, br',
    # 'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'Cache-Control': 'max-age=0',
    # 'Connection': 'keep-alive',
    # 'Cookie': '_ga=GA1.2.618591872.1545294432; _gid=GA1.2.272050992.1545294432',
    # 'Host': 'okky.kr',
    # 'Upgrade-Insecure-Requests': '1',
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    # }

    # #Headless
    # options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # options.add_argument('window-size=1920x1080')
    # options.add_argument("disable-gpu")

    # driver = webdriver.Chrome("./chromedriver.exe", chrome_options=options)
    # driver.get(url)
    # driver.implicitly_wait(3)
    # # driver.find_element_by_id("root").click()
    # html = driver.page_source
    # driver.quit()



    html = requests.get(url)
    soup = BeautifulSoup(html.text,"html.parser")
    print(soup)
    print(soup.find_all("h5",class_='list-group-item-heading list-group-item-evaluate'))
    from hi import get_answer
    answer, params = get_answer("강남역 자바 스터디 찾아줘", "123123")
    # print(params)
    # print(answer, params['PURPOSE'])
    return "test"


# _crawl_festa("https://festa.io")
_crawl_okky("https://okky.kr/articles/gathering")