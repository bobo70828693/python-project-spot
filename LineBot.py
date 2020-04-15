import DistanceService
import os
import FirebaseConnect
import hashlib
import ReplyActionService
from datetime import datetime
from time import strftime
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from urllib import parse
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, 
    TextMessage, 
    TextSendMessage, 
    LocationMessage, 
    FlexSendMessage, 
    CarouselTemplate, 
    TemplateSendMessage, 
    CarouselColumn, 
    PostbackAction, 
    MessageAction, 
    URIAction, 
    PostbackEvent,
    QuickReplyButton,
    QuickReply
)

app = Flask(__name__)
load_dotenv()

secret = os.getenv('LINE_CHANNEL_SECRET')
accessToken = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
line_bot_api = LineBotApi(accessToken)
handler = WebhookHandler(secret)

@app.route("/", methods=['GET'])
def hello():
    print("Hello World")
    return 'ok'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    if event.source.user_id == "U2512599a6181ea0e2d9af9eae6aecfaf":
        if event.message.text == '規劃行程':
            # initial user travel
            s = hashlib.sha1()
            s.update(event.source.user_id.encode('utf-8'))
            enUserId = s.hexdigest()
            basePath = 'users/{enUserId}'.format(enUserId=enUserId)
            FirebaseConnect.deleteDataFirebase(basePath)
            # pick transportation
            ReplyActionService.pickTransportation(line_bot_api, event.source.user_id)
        elif event.message.text == '建立行程':
            ReplyActionService.establishTrip(line_bot_api, event.source.user_id)
        elif event.message.text == '出發時間':
            ReplyActionService.pickTransportation(line_bot_api, event.source.user_id)
    elif event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    if event.message.type == 'location':
        data = event.message
        ReplyActionService.recommendSpot(line_bot_api, event.source.user_id, event.reply_token, data)

@handler.add(PostbackEvent)
def reply_back(event):
    if event.type == "postback":
        s = hashlib.sha1()
        s.update(event.source.user_id.encode('utf-8'))
        enUserId = s.hexdigest()
        # analyze url parameters
        data = parse.parse_qs(event.postback.data)
        action = data['action'][0]
        likeSpots = []
        if action == 'like':
            dataPath = 'users/{enUserId}/spotList'.format(enUserId = enUserId)
            dataFb = FirebaseConnect.getDataFirebase(dataPath)
            if dataFb is not None:
                check = next((check for check in dataFb if check['name'] == data['spot'][0]), None)
                if check is not None:
                    replyText = '已加入喜翻'
                else:
                    replyText = '幫您加入喜翻'
                    likeSpots = dataFb
                    likeSpots += [{
                        "name": data['spot'][0],
                        "distance": data['distance'][0]
                    }]
                    FirebaseConnect.insertDataFirebase(dataPath, likeSpots)
            else:
                replyText = '幫您加入喜翻'
                likeSpots += [{
                    "name": data['spot'][0],
                    "distance": data['distance'][0]
                }]
                FirebaseConnect.insertDataFirebase(dataPath, likeSpots)
                
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=replyText)
                )

            ReplyActionService.askEnd(line_bot_api, event.source.user_id)
        elif action == 'pick_time':
            # 挑選時間
            currentTime = datetime.now()
            pickTime = event.postback.params.get('time', currentTime.strftime("%H:%M"))

            dataPath = 'users/{enUserId}/startTime'.format(enUserId = enUserId)
            FirebaseConnect.insertDataFirebase(dataPath, pickTime)
            replyText = "你選的出發時間為: {time}".format(time=pickTime)
            result = ReplyActionService.PushMessage(line_bot_api, event.reply_token, replyText)
            if result == 'ok':
                ReplyActionService.askEstablished(line_bot_api, event.source.user_id)
            #     ReplyActionService.pickTransportation(line_bot_api, event.source.user_id)
        elif action == 'pick_transportation':
            # 挑選交通工具
            dataPath = 'users/{enUserId}/transportation'.format(enUserId = enUserId)
            FirebaseConnect.insertDataFirebase(dataPath, data['transportation'][0])
            replyText = "你挑選的交通工具為: {transportation}".format(transportation=data['display_text'][0])
            result = ReplyActionService.PushMessage(line_bot_api, event.reply_token, replyText)
            if result == 'ok':
                # 傳送gps
                ReplyActionService.pickGps(line_bot_api, event.source.user_id)


        # data = event.postback.data
        # print(event.postback.params['like'])
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage
        # )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
