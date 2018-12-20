# -- coding: utf-8 --
import json
import os
import re
# import urllib.request
import requests

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = 'xoxb-507725070581-507736316784-t38CYmD3CyFuNV1g6SHkiBDB'
slack_client_id = '507725070581.508303178532'
slack_client_secret = '35a92591f70fb432bb296be978dd1c6b'
slack_verification = 'T95rgjj3DWTCaMTLo6z8LsgN'
sc = SlackClient(slack_token)

# 크롤링 함수
def _crawl_portal_keywords(option):
    print("option input : ",option)
    
    url = option
    # url = re.search(r'(https?://\S+)', text.split('|')[0]).group(0)
    # req = urllib.request.Request(url)
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    sourcecode = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    # sourcecode = urllib.request.urlopen(url).read()

    soup = BeautifulSoup(sourcecode.text, "html.parser")
    # print(sourcecode.text)
    #함수를 구현해 주세요

    keywords = [i.get_text() for i in soup.find_all("h5", class_="title ellipsis")]
    
    print('LOG : print return')
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)
# 텍스트 분기시키는 함수
def _branch_function(text):
    print("input : ",text)
    if '설명' in text:
        print('설명')
        pass
    elif '온오프믹스' in text:
        print('온오프믹스')
        return 'https://www.onoffmix.com/'
    
    



# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print('\n\n',slack_event["event"],'\n\n')

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        p = re.compile(r"\S+")
        text2 = p.findall(text)[1]
        option = _branch_function(text2)
        
        keywords = _crawl_portal_keywords(option)
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

@app.route("/", methods=["GET"])
def index():
   return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
   app.run('127.0.0.1', port=8080)