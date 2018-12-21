# -- coding: utf-8 --
import json
import os
import re
# import urllib.request
import requests

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template, jsonify

import multiprocessing as mp
from threading import Thread
import time
from datetime import datetime, timedelta


app = Flask(__name__)

slack_token = 'xoxb-507725070581-509337063188-4B2dlNiaypkubaIFJubwKUsd'
slack_client_id = '507725070581.510907025158'
slack_client_secret = '84c1760c4c34aa394d931595be57c1f4'
slack_verification = 'qXIrHbajFWXzXpgOFQVSo60D'
sc = SlackClient(slack_token)

# threading function
def processing_event(queue):
   while True:
       # 큐가 비어있지 않은 경우 로직 실행
       if not queue.empty():
           slack_event = queue.get()

           # Your Processing Code Block gose to here
           channel = slack_event["event"]["channel"]
           text = slack_event["event"]["text"]

           # 챗봇 크롤링 프로세스 로직 함수
           keywords = _crawl_portal_keywords(text)


           # 아래에 슬랙 클라이언트 api를 호출하세요
           sc.api_call(
               "chat.postMessage",
               channel=channel,
               text=keywords
           )


def get_answer(text, user_key):
    data_send = {
        'query': text,
        'sessionId': user_key,
        'lang': 'ko'
    }
    data_header = {
        'Authorization': 'Bearer 75878193acd643819852c272fd782a00',
        'Content-Type':'application/json; charset=utf-8'
    }
    dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'

    res = requests.post(dialogflow_url, data=json.dumps(data_send), headers=data_header)
    if res.status_code != requests.codes['ok']:
        return '오류가 발생했습니다.'

    data_receive = res.json()
    answer = data_receive['result']['fulfillment']['speech']
    print(data_receive)
    params = data_receive['result']['parameters']

    return answer, params

# 크롤링 함수_온오프믹스
def _crawl_portal_keywords(option):
    print("option input : ",option)
    
    url = option
    # url = re.search(r'(https?://\S+)', text.split('|')[0]).group(0)
    # req = urllib.request.Request(url)
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    sourcecode = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    # sourcecode = urllib.request.urlopen(url).read()

    soup = BeautifulSoup(sourcecode.text, "lxml")
    # print(sourcecode.text)
    #함수를 구현해 주세요

    keywords = [i.get_text() for i in soup.find_all("h5", class_="title ellipsis")]
    
    s = soup.select("ul > li > article > a")
    links = [i.get("href") for i in s]
    
    # links = [i['href'].get_text() for i in soup.find_all("article > a",class_="event_area event_main")]
    # print(links)
    idkeywords = [str(i+1)+":"+keywords[i] for i in range(len(keywords))]
    print(keywords[0], links[0], len(keywords), len(links), len(idkeywords))
    idkeywordslinks = [idkeywords[i]+"\n 링크 : https://www.onoffmix.com"+links[i] for i in range(len(keywords))]
    print('LOG : print return')
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(idkeywordslinks)
# 텍스트 분기시키는 함수
def _branch_function(text):
    print("input :",text)
    
    if ('온오프믹스' or 'onoffmix' or 'dhsdhvmal') in text:
        p = re.compile(r':\S+')
        print(p.search(text))
        if p.search(text):
            w = p.search(text)[0][1:]
            print("w",w)
            from urllib import parse
            q = parse.urlencode({'s' : w})
            print(q)
            return 'https://www.onoffmix.com/event/main?'+q, 2
        else:
            return 'https://www.onoffmix.com', 1
    elif '페스타' in text:
        return 'https://festa.io/', 3
    elif '오키' in text:
        return "테스트중..", 4
    else:
        print('설명')
        return "SSAFY 짱", 0
    



# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print('\n\n',slack_event["event"],'\n\n')

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        p = re.compile(r"> .+")
        text2 = p.search(text).group()[2:]


        print("text2",text2)
        url, option = _branch_function(text2)
        
        if option == 0:
            keywords = '''
설명
===========================================================================
질문						|답변
---------------------------------------------------------------------------------------------------------------------
온오프믹스			|온오프믹스 메인 사이트의 모임/세미나의 정보를 보여줍니다.
onoffmix				|온오프믹스 메인 사이트의 모임/세미나의 정보를 보여줍니다.
온오프믹스 :(단어)			|온오프믹스 검색 결과의 모임/세미나 정보를 보여줍니다.
온오프믹스 :#(단어)			|온오프믹스 태그 검색 결과의 정보를 보여줍니다.
페스타				|festa.io사이트의 모임/세미나 정보를 보여줍니다.
festa				|festa.io사이트의 모임/세미나 정보를 보여줍니다.
            '''
        elif option == 3:
            from crawling_festa import _crawl_festa
            keywords = "링크 주소 :"+url+"\n"+_crawl_festa(url)
        elif option == 4:
            from crawling_festa import _crawl_okky
            keywords = url+"\n"+_crawl_okky("https://okky.kr/articles/gathering")
        else:
            keywords = "링크 주소 :"+url+"\n"+_crawl_portal_keywords(url)
        
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )


        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
   slack_event = json.loads(request.data)
   if slack_event['event_time'] < (datetime.now() - timedelta(seconds=1)).timestamp():
        return make_response("this message is before sent.", 200, {"X-Slack-No-Retry": 1})


   if "challenge" in slack_event:
       return make_response(slack_event["challenge"], 200, {"content_type":
                                                                "application/json"
                                                            })

   if slack_verification != slack_event.get("token"):
       message = "Invalid Slack verification token: %s" % (slack_event["token"])
       make_response(message, 403, {"X-Slack-No-Retry": 1})

   if "event" in slack_event:
       event_type = slack_event["event"]["type"]
       return _event_handler(event_type, slack_event)

   # If our bot hears things that are not events we've subscribed to,
   # send a quirky but helpful error response
   return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                       you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["POST","GET"])
def index(c,u):
    content = request.args.get('content')
    userid = request.args.get('userid')

    return "<h1>Server is ready.</h1><br>"

if __name__ == '__main__':
   event_queue = mp.Queue()

   p = Thread(target=processing_event, args=(event_queue,))
   p.start()
   print("subprocess started")

   app.run('127.0.0.1', port=8080)
   p.join()