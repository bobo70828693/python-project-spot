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


def insertDataFirebase(path, data):

    ref = db.reference(path)
    ref.set(data)
    
    return 'ok'

def getDataFirebase(path):
    ref = db.reference(path)
    data = ref.get()

    return data

def deleteDataFirebase(path):
    ref = db.reference(path)
    ref.delete()

    return 'ok'

initFirebase()