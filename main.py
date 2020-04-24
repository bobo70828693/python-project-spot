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
    userId = event.source.user_id
    s = hashlib.sha1()
    s.update(userId.encode('utf-8'))
    enUserId = s.hexdigest()
    if event.message.text == '規劃行程':
        # initial user travel
        basePath = 'users/{enUserId}'.format(enUserId=enUserId)
        FirebaseConnect.deleteDataFirebase(basePath)

        # pick transportation
        ReplyActionService.PickTransportation(line_bot_api, userId)
    elif event.message.text == '熱門景點':
        ReplyActionService.RecommendPoPularSpot(line_bot_api, userId)
    elif event.message.text == '建立行程':
        ReplyActionService.EstablishTrip(line_bot_api, userId)
    elif event.message.text == '查看目前清單':
        ReplyActionService.ReviewSpot(line_bot_api, userId)
        ReplyActionService.AskEnd(line_bot_api, userId, 'preview')
    elif event.message.text == '出發時間':
        ReplyActionService.PickTransportation(line_bot_api, userId)
    elif event.message.text == '更多景點':
        ReplyActionService.RecommendSpot(line_bot_api, userId, event.reply_token)
    elif event.message.text == '清除目前清單':
        # initial user travel
        basePath = 'users/{enUserId}/spotList'.format(enUserId=enUserId)
        FirebaseConnect.deleteDataFirebase(basePath)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    s = hashlib.sha1()
    s.update(event.source.user_id.encode('utf-8'))
    enUserId = s.hexdigest()
    if event.message.type == 'location':
        userPath = 'users/{enUserId}/mode'.format(enUserId = enUserId)

        userMode = FirebaseConnect.getDataFirebase(userPath)
        data = event.message
        if userMode == 'establish':
            pos = {
                "lat" : data.latitude,
                "long": data.longitude,
            }
            posPath = "users/{enUserId}/pos".format(enUserId=enUserId)
            FirebaseConnect.insertDataFirebase(posPath, pos)
            ReplyActionService.EstablishTrip(line_bot_api, event.source.user_id)
        else:
            ReplyActionService.RecommendSpot(line_bot_api, event.source.user_id, event.reply_token, data)

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
            userPath = 'users/{enUserId}/'.format(enUserId = enUserId)
            userData = FirebaseConnect.getDataFirebase(userPath)
            pos = userData.get('pos', None)
            dataFb = userData.get('spotList', None)
            dataPath = 'users/{enUserId}/spotList'.format(enUserId = enUserId)
            distance = data.get('distance', [0])
            
            if dataFb is not None:
                check = next((check for check in dataFb if check['name'] == data['spot'][0]), None)
                if check is not None:
                    replyText = '已加入喜翻'
                else:
                    replyText = '幫您加入喜翻'
                    likeSpots = dataFb
                    likeSpots += [{
                        "name": data['spot'][0],
                        "distance": min(distance)
                    }]
                    FirebaseConnect.insertDataFirebase(dataPath, likeSpots)
            else:
                replyText = '幫您加入喜翻'
                likeSpots += [{
                    "name": data['spot'][0],
                    "distance": min(distance)
                }]
                FirebaseConnect.insertDataFirebase(dataPath, likeSpots)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=replyText)
            )
            ReplyActionService.AskEnd(line_bot_api, event.source.user_id)
        if action == 'unLike':
            dataPath = 'users/{enUserId}/spotList/{key}'.format(enUserId = enUserId, key = data['key'][0])
            FirebaseConnect.updateDataFirebase(dataPath, {"unLike": 1})

            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="已幫你取消")
                )

            ReplyActionService.AskEnd(line_bot_api, event.source.user_id)
        elif action == 'pick_time':
            # 挑選時間
            currentTime = datetime.now()
            pickTime = event.postback.params.get('time', currentTime.strftime("%H:%M"))

            dataPath = 'users/{enUserId}/startTime'.format(enUserId = enUserId)
            FirebaseConnect.insertDataFirebase(dataPath, pickTime)
            replyText = "你選的出發時間為: {time}".format(time=pickTime)
            result = ReplyActionService.PushMessage(line_bot_api, event.reply_token, replyText)
            if result == 'ok':
                ReplyActionService.AskEstablished(line_bot_api, event.source.user_id)
            #     ReplyActionService.PickTransportation(line_bot_api, event.source.user_id)
        elif action == 'pick_transportation':
            # 挑選交通工具
            dataPath = 'users/{enUserId}/transportation'.format(enUserId = enUserId)
            FirebaseConnect.insertDataFirebase(dataPath, data['transportation'][0])
            replyText = "你挑選的交通工具為: {transportation}".format(transportation=data['display_text'][0])
            result = ReplyActionService.PushMessage(line_bot_api, event.reply_token, replyText)
            if result == 'ok':
                # 傳送gps
                ReplyActionService.PickGps(line_bot_api, event.source.user_id)
        elif action == 'spot_detail':
            distance = data.get('distance', [0])
            result = ReplyActionService.SpotDetail(line_bot_api, event.reply_token, min(data['spot']), min(distance))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
