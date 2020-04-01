import DistanceService
import os
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
    PostbackEvent
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
    if event.source.user_id == "U2512599a6181ea0e2d9af9eae6aecfaf":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text="看你妹",
                contents={
                        "type": "bubble",
                        "size": "mega",
                        "header": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "FROM",
                                    "color": "#ffffff66",
                                    "size": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": "Akihabara",
                                    "color": "#ffffff",
                                    "size": "xl",
                                    "flex": 4,
                                    "weight": "bold"
                                }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "TO",
                                    "color": "#ffffff66",
                                    "size": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": "Shinjuku",
                                    "color": "#ffffff",
                                    "size": "xl",
                                    "flex": 4,
                                    "weight": "bold"
                                }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "TO",
                                    "color": "#ffffff66",
                                    "size": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": "Shinjuku",
                                    "color": "#ffffff",
                                    "size": "xl",
                                    "flex": 4,
                                    "weight": "bold"
                                }
                                ]
                            }
                            ],
                            "paddingAll": "20px",
                            "backgroundColor": "#0367D3",
                            "spacing": "md",
                            "height": "200px",
                            "paddingTop": "22px"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": "Total: 1 hour",
                                "color": "#b7b7b7",
                                "size": "xs"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "20:30",
                                    "size": "sm",
                                    "gravity": "center"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "filler"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "filler"
                                        }
                                        ],
                                        "cornerRadius": "30px",
                                        "height": "12px",
                                        "width": "12px",
                                        "borderColor": "#EF454D",
                                        "borderWidth": "2px"
                                    },
                                    {
                                        "type": "filler"
                                    }
                                    ],
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": "Akihabara",
                                    "gravity": "center",
                                    "flex": 4,
                                    "size": "sm"
                                }
                                ],
                                "spacing": "lg",
                                "cornerRadius": "30px",
                                "margin": "xl"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "contents": [
                                    {
                                        "type": "filler"
                                    }
                                    ],
                                    "flex": 1
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "filler"
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                            {
                                                "type": "filler"
                                            }
                                            ],
                                            "width": "2px",
                                            "backgroundColor": "#B7B7B7"
                                        },
                                        {
                                            "type": "filler"
                                        }
                                        ],
                                        "flex": 1
                                    }
                                    ],
                                    "width": "12px"
                                },
                                {
                                    "type": "text",
                                    "text": "Walk 4min",
                                    "gravity": "center",
                                    "flex": 4,
                                    "size": "xs",
                                    "color": "#8c8c8c"
                                }
                                ],
                                "spacing": "lg",
                                "height": "64px"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "20:34",
                                        "gravity": "center",
                                        "size": "sm"
                                    }
                                    ],
                                    "flex": 1
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "filler"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "filler"
                                        }
                                        ],
                                        "cornerRadius": "30px",
                                        "width": "12px",
                                        "height": "12px",
                                        "borderWidth": "2px",
                                        "borderColor": "#6486E3"
                                    },
                                    {
                                        "type": "filler"
                                    }
                                    ],
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": "Ochanomizu",
                                    "gravity": "center",
                                    "flex": 4,
                                    "size": "sm"
                                }
                                ],
                                "spacing": "lg",
                                "cornerRadius": "30px"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "contents": [
                                    {
                                        "type": "filler"
                                    }
                                    ],
                                    "flex": 1
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "filler"
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                            {
                                                "type": "filler"
                                            }
                                            ],
                                            "width": "2px",
                                            "backgroundColor": "#6486E3"
                                        },
                                        {
                                            "type": "filler"
                                        }
                                        ],
                                        "flex": 1
                                    }
                                    ],
                                    "width": "12px"
                                },
                                {
                                    "type": "text",
                                    "text": "Metro 1hr",
                                    "gravity": "center",
                                    "flex": 4,
                                    "size": "xs",
                                    "color": "#8c8c8c"
                                }
                                ],
                                "spacing": "lg",
                                "height": "64px"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "20:40",
                                    "gravity": "center",
                                    "size": "sm"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "filler"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "filler"
                                        }
                                        ],
                                        "cornerRadius": "30px",
                                        "width": "12px",
                                        "height": "12px",
                                        "borderColor": "#6486E3",
                                        "borderWidth": "2px"
                                    },
                                    {
                                        "type": "filler"
                                    }
                                    ],
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": "Shinjuku",
                                    "gravity": "center",
                                    "flex": 4,
                                    "size": "sm"
                                }
                                ],
                                "spacing": "lg",
                                "cornerRadius": "30px"
                            }
                            ]
                        }
                        }
            )
            # TextSendMessage(text=event.message.text)
        )
    elif event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    if event.message.type == 'location':
        requestData = event.message
        pos = {
            "lat" : event.message.latitude,
            "long": event.message.longitude,
        }
        recommendList = DistanceService.recommendSpot(pos)
        r=0
        columns = []
        for oneRecommend in recommendList:
            if r<=5:
                columns += [
                    CarouselColumn(
                                thumbnail_image_url=oneRecommend['thumbnailUrl'],
                                    title=oneRecommend['title'],
                                    text=oneRecommend['address'],
                                    actions=[
                                        PostbackAction(
                                            label='喜翻',
                                            display_text='喜翻',
                                            data='action=like&spot=' + oneRecommend['title']
                                        ),
                                        # MessageAction(
                                        #     label='message2',
                                        #     text='message text2'
                                        # ),
                                        # URIAction(
                                        #     label='uri2',
                                        #     uri='http://example.com/2'
                                        # )
                                    ]
                )]
                r +=1
            else:
                break;

        line_bot_api.reply_message(
                    event.reply_token,
                    TemplateSendMessage(
                        alt_text="推薦來囉",
                        template=CarouselTemplate(
                            columns=columns
                        )))

@handler.add(PostbackEvent)
def reply_back(event):
    print(event)
    if event.type == "postback":
        data = parse.parse_qs(event.postback.data)
        if data['action'][0] == 'like':
             line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=data['spot'][0])
                )
        # data = event.postback.data
        # print(event.postback.params['like'])
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage
        # )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

# FlexSendMessage(
#     alt_text='hello',
#     contents={
#                 "type": "bubble",
#                 "hero": {
#                     "type": "image",
#                     "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
#                     "size": "full",
#                     "aspectRatio": "20:13",
#                     "aspectMode": "cover",
#                     "action": {
#                     "type": "uri",
#                     "uri": "http://linecorp.com/"
#                     }
#                 },
#                 "body": {
#                     "type": "box",
#                     "layout": "vertical",
#                     "contents": [
#                     {
#                         "type": "text",
#                         "text": "Brown Cafe",
#                         "weight": "bold",
#                         "size": "xl"
#                     },
#                     {
#                         "type": "box",
#                         "layout": "baseline",
#                         "margin": "md",
#                         "contents": [
#                         {
#                             "type": "icon",
#                             "size": "sm",
#                             "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
#                         },
#                         {
#                             "type": "icon",
#                             "size": "sm",
#                             "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
#                         },
#                         {
#                             "type": "icon",
#                             "size": "sm",
#                             "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
#                         },
#                         {
#                             "type": "icon",
#                             "size": "sm",
#                             "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
#                         },
#                         {
#                             "type": "icon",
#                             "size": "sm",
#                             "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
#                         },
#                         {
#                             "type": "text",
#                             "text": "4.0",
#                             "size": "sm",
#                             "color": "#999999",
#                             "margin": "md",
#                             "flex": 0
#                         }
#                         ]
#                     },
#                     {
#                         "type": "box",
#                         "layout": "vertical",
#                         "margin": "lg",
#                         "spacing": "sm",
#                         "contents": [
#                         {
#                             "type": "box",
#                             "layout": "baseline",
#                             "spacing": "sm",
#                             "contents": [
#                             {
#                                 "type": "text",
#                                 "text": "Place",
#                                 "color": "#aaaaaa",
#                                 "size": "sm",
#                                 "flex": 1
#                             },
#                             {
#                                 "type": "text",
#                                 "text": "Miraina Tower, 4-1-6 Shinjuku, Tokyo",
#                                 "wrap": True,
#                                 "color": "#666666",
#                                 "size": "sm",
#                                 "flex": 5
#                             }
#                             ]
#                         },
#                         {
#                             "type": "box",
#                             "layout": "baseline",
#                             "spacing": "sm",
#                             "contents": [
#                             {
#                                 "type": "text",
#                                 "text": "Time",
#                                 "color": "#aaaaaa",
#                                 "size": "sm",
#                                 "flex": 1
#                             },
#                             {
#                                 "type": "text",
#                                 "text": "10:00 - 23:00",
#                                 "wrap": True,
#                                 "color": "#666666",
#                                 "size": "sm",
#                                 "flex": 5
#                             }
#                             ]
#                         }
#                         ]
#                     }
#                     ]
#                 },
#                 "footer": {
#                     "type": "box",
#                     "layout": "vertical",
#                     "spacing": "sm",
#                     "contents": [
#                     {
#                         "type": "button",
#                         "style": "link",
#                         "height": "sm",
#                         "action": {
#                         "type": "uri",
#                         "label": "CALL",
#                         "uri": "https://linecorp.com"
#                         }
#                     },
#                     {
#                         "type": "button",
#                         "style": "link",
#                         "height": "sm",
#                         "action": {
#                         "type": "uri",
#                         "label": "WEBSITE",
#                         "uri": "https://linecorp.com"
#                         }
#                     },
#                     {
#                         "type": "spacer",
#                         "size": "sm"
#                     }
#                     ],
#                     "flex": 0
#                 }
#             }
# )