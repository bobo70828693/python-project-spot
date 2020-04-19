import FirebaseConnect
import hashlib
import DistanceService
from time import strftime,strptime,gmtime
from datetime import datetime, timedelta
from linebot.models import (
    QuickReply,
    QuickReplyButton,
    TextSendMessage,
    MessageAction,
    PostbackAction,
    FlexSendMessage,
    TemplateSendMessage,
    CarouselTemplate,
    CarouselColumn,
    LocationAction
)

import os
from dotenv import load_dotenv
from linebot import (
    LineBotApi, WebhookHandler
)
load_dotenv()

def AskEnd(lineBotApi, userId, mode = 'default'):
    currentTime = datetime.now()
    if mode == 'default':
        lineBotApi.push_message(
            userId, 
            TextSendMessage(
                text="該出發了吧？",
                quick_reply=QuickReply(items=[
                    QuickReplyButton(action={
                        "type":"datetimepicker",
                        "label":"選擇出發時間",
                        "data":"action=pick_time",
                        "mode":"time",
                        "initial":currentTime.strftime("%H:%M"),
                        "max":"23:59",
                        "min":"00:00"
                    }),
                    QuickReplyButton(action=MessageAction(label="我還要", text="更多景點")),
                    QuickReplyButton(action=MessageAction(label="看一下選了什麼", text="查看目前清單")),
                ])
        ))
    elif mode == 'preview':
        lineBotApi.push_message(
            userId, 
            TextSendMessage(
                text="該出發了吧？",
                quick_reply=QuickReply(items=[
                    QuickReplyButton(action={
                        "type":"datetimepicker",
                        "label":"選擇出發時間",
                        "data":"action=pick_time",
                        "mode":"time",
                        "initial":currentTime.strftime("%H:%M"),
                        "max":"23:59",
                        "min":"00:00"
                    }),
                    QuickReplyButton(action=MessageAction(label="一鍵清除", text="清除目前清單")),
                ])
        ))


def AskEstablished(lineBotApi, userId):
    lineBotApi.push_message(
        userId, 
        TextSendMessage(
            text="是否建立行程？",
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="出發", text="建立行程"))
            ])
    ))
def RecommendSpot(lineBotApi, userId, replyToken, data = None):
    s = hashlib.sha1()
    s.update(userId.encode('utf-8'))
    enUserId = s.hexdigest()
    
    basePath = 'users/{enUserId}'.format(enUserId=enUserId)
    userData = FirebaseConnect.getDataFirebase(basePath)

    if data is not None:
        pos = {
            "lat" : data.latitude,
            "long": data.longitude,
        }
        posPath = "{base}/pos".format(base=basePath)
        FirebaseConnect.insertDataFirebase(posPath, pos)
    else:
        pos = userData.get('pos', None)

    userSpotList = userData.get('spotList', [])
    userTransportation = userData.get('transportation', 'driving')
    recommendList = DistanceService.RecommendSpot(pos, userTransportation)
    r=0
    columns = []
    for oneRecommend in recommendList:
        if r<10:
            checkExist = next((checkExist for checkExist in userSpotList if checkExist['name'] == oneRecommend['title']), None)
            if checkExist is None:
                columns += [
                    CarouselColumn(
                        thumbnail_image_url=oneRecommend['thumbnailUrl'],
                            title=oneRecommend['title'],
                            text=oneRecommend['address'],
                            actions=[
                                PostbackAction(
                                    label='了解更多',
                                    display_text='詳細資訊',
                                    data='action=spot_detail&spot={title}&distance={distance}'.format(title=oneRecommend['title'], distance=str(round(oneRecommend['distance'], 1)))
                                ),
                                PostbackAction(
                                    label='喜翻',
                                    display_text='喜翻',
                                    data='action=like&spot={title}&distance={distance}'.format(title=oneRecommend['title'], distance=str(round(oneRecommend['distance'], 1)))
                                )
                            ]
                )]
                r +=1
        else:
            break;

    lineBotApi.reply_message(
        replyToken,
        TemplateSendMessage(
            alt_text="推薦來囉",
            template=CarouselTemplate(
                columns=columns
            )))

def RecommendPoPularSpot(lineBotApi, userId):
    s = hashlib.sha1()
    s.update(userId.encode('utf-8'))
    enUserId = s.hexdigest()
    userPath = 'users/{enUserId}'.format(enUserId=enUserId)
    FirebaseConnect.updateDataFirebase(userPath, {'mode': 'popular'})

    popularSpotList = DistanceService.PopularSpot()
    columns = []
    for oneSpot in popularSpotList:
        columns += [
            CarouselColumn(
                thumbnail_image_url=oneSpot['thumbnailUrl'],
                    title=oneSpot['title'],
                    text=oneSpot['address'],
                    actions=[
                        PostbackAction(
                            label='了解更多',
                            display_text='詳細資訊',
                            data='action=spot_detail&spot={title}'.format(title=oneSpot['title'])
                        ),
                        PostbackAction(
                            label='喜翻',
                            display_text='喜翻',
                            data='action=like&spot={title}'.format(title=oneSpot['title'])
                        )
                    ]
        )]

    lineBotApi.push_message(
        userId,
        TemplateSendMessage(
            alt_text="熱門景點",
            template=CarouselTemplate(
                columns=columns
            )))


def ReviewSpot(lineBotApi, userId):
    s = hashlib.sha1()
    s.update(userId.encode('utf-8'))
    enUserId = s.hexdigest()

    dataPath = 'users/{enUserId}/'.format(enUserId=enUserId)
    data = FirebaseConnect.getDataFirebase(dataPath)
    currentSpot = data.get("spotList", [])
    if len(currentSpot) > 0:
        # 過濾掉已取消的
        currentSpot = [spot for spot in currentSpot if 'unLike' not in spot]
        columns = []
        for key, userSpot in enumerate(currentSpot):
            spotInfo = FirebaseConnect.getDataFirebase('spotInform/{spotTitle}'.format(spotTitle=userSpot['name']))
            columns += [
                CarouselColumn(
                    thumbnail_image_url=spotInfo['thumbnailUrl'],
                        title=userSpot['name'],
                        text=spotInfo['address'],
                        actions=[
                            PostbackAction(
                                label='不要了',
                                display_text='討厭',
                                data='action=unLike&key={key}'.format(key=key)
                            )
                        ]
            )]
        
        lineBotApi.push_message(
            userId,
            TemplateSendMessage(
                alt_text="你挑選的景點",
                template=CarouselTemplate(
                    columns=columns
                )))
    else:
        lineBotApi.push_message(
            userId,
            TextSendMessage(text="尚未挑選景點"))

def EstablishTrip(lineBotApi, userId):
    s = hashlib.sha1()
    s.update(userId.encode('utf-8'))
    enUserId = s.hexdigest()

    dataPath = 'users/{enUserId}/'.format(enUserId=enUserId)
    FirebaseConnect.updateDataFirebase(dataPath, {'mode': 'establish'})
    data = FirebaseConnect.getDataFirebase(dataPath)
    pos = data.get("pos")

    if pos is None:
        PickTransportation(lineBotApi, userId)
    else:
        currentSpot = data.get("spotList", [])
        # 過濾掉已取消的
        currentSpot = [spot for spot in currentSpot if 'unLike' not in spot]
        currentSpot.sort(key = lambda k: (float(k.get('distance'))))
        defaultStartTime = datetime.now() + timedelta(hours=1)
        userTransportation = data.get("transportation", "driving")
        userStartTime = data.get("startTime", defaultStartTime.strftime("%H:%M"))

        bodyContent = []
        totalTime = 0

        length = len(currentSpot)
        FlexMsg = []
        count = 1
        lastPos = pos

        # 第一個點為目前位置
        bodyContent += [
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                {
                    "type": "text",
                    "text": userStartTime,
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
                    "text": "目前位置",
                    "gravity": "center",
                    "flex": 4,
                    "size": "sm"
                }
                ],
                "spacing": "lg",
                "cornerRadius": "30px",
            },
        ]
        nextTimeStr = userStartTime 
        for key, spotInfo in enumerate(currentSpot):
            getDestinationInfo = FirebaseConnect.getDataFirebase('/spotInform/{spotName}'.format(spotName=spotInfo['name']))
            destPos = {
                'lat': getDestinationInfo['lat'],
                'long': getDestinationInfo['long']
            }
            distanceResult = DistanceService.calPlaceInfo(lastPos, destPos, userTransportation)
            lastPos = destPos
            durationTime = distanceResult['rows'][0]['elements'][0]['duration']['value']
            totalTime += durationTime
            nextTime = datetime.strptime(nextTimeStr, "%H:%M")
            nextTimeStr = (nextTime + timedelta(seconds=durationTime)).strftime("%H:%M") 

            # 不滿一小時
            if strftime("%H", gmtime(durationTime)) == "00":
                transportationTimeStr = "{transportation} {durationTime} ".format(transportation=userTransportation, durationTime=strftime("%M min", gmtime(durationTime)))
            else:
                transportationTimeStr = "{transportation} {durationTime} ".format(transportation=userTransportation, durationTime=strftime("%H hour %M min", gmtime(durationTime)))
            
            # 增加垂直線
            bodyContent += [{
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
                    "text": transportationTimeStr.capitalize(),
                    "gravity": "center",
                    "flex": 4,
                    "size": "xs",
                    "color": "#8c8c8c"
                }
                ],
                "spacing": "lg",
                "height": "64px"
            }]
                
        
            # 增加景點，組合FlexMessage
            circleColor = "#6486E3"
            bodyContent += [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "text",
                        "text": nextTimeStr,
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
                            "borderColor": circleColor,
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
                        "text": spotInfo['name'],
                        "gravity": "center",
                        "flex": 4,
                        "size": "sm"
                    }
                    ],
                    "spacing": "lg",
                    "cornerRadius": "30px",
                },
            ]

        if strftime("%H", gmtime(totalTime)) == "00":
            totalTimeStr = "Total: " + strftime("%M min", gmtime(totalTime))
        else:
            totalTimeStr = "Total: " + strftime("%H hour %M min", gmtime(totalTime))

        bodyContent.insert(0,{
                "type": "text",
                "text": totalTimeStr,
                "color": "#b7b7b7",
                "size": "xs"
        })
        FlexContentHeader = {
            'type': 'box',
            'layout': 'vertical',
            'contents': [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "FROM",
                            "color": "#ffffff",
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": "目前位置",
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
                            "color": "#ffffff",
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": currentSpot[-1]['name'],
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
            "height": "154px",
            "paddingTop": "22px"
        }

        FlexMsg = {
            "type": "bubble",
            "size": "mega",
            "header": FlexContentHeader,
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": bodyContent
            }
        }
        lineBotApi.push_message(
            userId,
            FlexSendMessage(
                alt_text="建立行程",
                contents=FlexMsg
            )
        )

def PickTransportation(lineBotApi, userId):
    lineBotApi.push_message(userId, TextSendMessage(
        text="選擇你的交通方式",
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(image_url="https://storage.googleapis.com/python-project-spot.appspot.com/icons/car_icon.png", action=PostbackAction(label="瑪莎他弟", display_text="汽車", data="action=pick_transportation&transportation=driving&display_text=汽車")),
                QuickReplyButton(image_url="https://storage.googleapis.com/python-project-spot.appspot.com/icons/walk_icon.png", action=PostbackAction(label="11號公車", display_text="走路", data="action=pick_transportation&transportation=walking&display_text=走路")),
                QuickReplyButton(image_url="https://storage.googleapis.com/python-project-spot.appspot.com/icons/bike_icon.png", action=PostbackAction(label="卡打掐", display_text="腳踏車", data="action=pick_transportation&transportation=bicycling&display_text=腳踏車")),
                # QuickReplyButton(image_url="https://storage.googleapis.com/python-project-spot.appspot.com/icons/bus_icon.png", action=PostbackAction(label="真的公車", display_text="大眾交通工具", data="action=pick_transportation&transportation=transit"))
            ]
        )
    ))
    return 'ok'

def PushMessage(lineBotApi, token, text):
    lineBotApi.reply_message(token, TextSendMessage(
        text=text
    ))
    return 'ok'

def PickGps(lineBotApi, userId):
    lineBotApi.push_message(userId, TextSendMessage(
        text="取得目前位置",
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(action=LocationAction(label="Location"))
            ]
        )
    ))

def SpotDetail(lineBotApi, replyToken, spotName, distance):
    dataPath = "spotInform/{spotName}".format(spotName=spotName)
    spotInfo = FirebaseConnect.getDataFirebase(dataPath)

    imgContent = []
    if len(spotInfo['imgList']) > 3:
        imgContent = [
            {
                "type": "image",
                "url": spotInfo['imgList'][0],
                "size": "5xl",
                "aspectMode": "cover",
                "aspectRatio": "150:196",
                "gravity": "center",
                "flex": 1
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "image",
                    "url": spotInfo['imgList'][1],
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "150:98",
                    "gravity": "center"
                },
                {
                    "type": "image",
                    "url": spotInfo['imgList'][2],
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "150:98",
                    "gravity": "center"
                }
                ],
                "flex": 1
            }
        ]
    else:
        imgContent = [
            {
                "type": "image",
                "url": spotInfo['thumbnailUrl'],
                "size": "5xl",
                "aspectMode": "cover",
                "aspectRatio": "150:196",
                "gravity": "center",
                "flex": 1
            }
        ]

    descContent = [
        {
            "type": "span",
            "text": spotName,
            "weight": "bold",
            "color": "#000000"
        },
        {
            "type": "span",
            "text": "     "
        },
        {
            "type": "span",
            "text": "{description} ..... ".format(description=spotInfo['description'])
        }
    ]

    linkContent = [
        {
            "type": "span",
            "text": "連結網址",
            "weight": "bold",
            "color": "#000000"
        },
        {
            "type": "span",
            "text": spotInfo['link'],
            "color": "#0972db"
        }
    ]

    viewerContent = [
        {
            "type": "text",
            "text": format(spotInfo['viewer'], ',') + " Like",
            "size": "sm",
            "color": "#bcbcbc"
        }
    ]

    footerContent = [
        {
            "type": "button",
            "style": "link",
            "action": {
                "label": "喜翻",
                "type": "postback",
                "display_text": "喜翻",
                "data": "action=like&spot={title}&distance={distance}".format(title=spotName, distance=distance)
            }
        }
    ]

    # 組合
    bodyContent = [
        # image box
        {
            "type": "box",
            "layout": "horizontal",
            "contents": imgContent
        },
        # description box
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "contents": descContent,
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "contents": linkContent,
                            "action": {
                                "type": "uri",
                                "uri": spotInfo['link']
                            },
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": viewerContent,
                            "spacing": "sm",
                            "margin": "md"
                        }
                    ]
                }
            ],
            "spacing": "xl",
            "paddingAll": "20px"
        }
    ]

    FlexMsg = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": bodyContent
        },
        "footer": {
            "type": "button",
            "layout": "vertical",
            "contents": footerContent,
            "flex": 0
        }
    }

    lineBotApi.reply_message(
        replyToken,
        FlexSendMessage(
            alt_text="test",
            contents=FlexMsg
        )
    )

    return 'ok'