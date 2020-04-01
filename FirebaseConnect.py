import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

def initFirebase():
    # 引用私密金鑰
    cred = credentials.Certificate('./serviceAccount.json')

    # init firebase
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://python-project-spot.firebaseio.com/"
    })

    return 'ok'


def insertDataFirebase(spotList):

    for oneSpot in spotList:
        print(oneSpot['title'])
        data = {
            'address': oneSpot['address'],
            'imgUrl': oneSpot['thumbnailUrl'],
            'lat':     oneSpot['lat'],
            'long':    oneSpot['long'],
            'viewer':  oneSpot['viewer'],
        }

        ref = db.reference('/spotInform/')
        userRef = ref.child(oneSpot['title'])
        userRef.set(data)
    
    return 'ok'

def getDataFirebase():
    ref = db.reference('/spotInform/')
    data = ref.get()

    return data