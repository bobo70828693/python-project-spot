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

def getDataFirebase(path, sort = None, sortBy = 'DESC' ,limit = 10):
    ref = db.reference(path)

    if sort is not None:
        ref = ref.order_by_child(sort)
        if sortBy == 'DESC':
            ref = ref.limit_to_last(limit)
        elif sortBy == 'ASC':
            ref = ref.limit_to_first(limit)

    return ref.get()

def deleteDataFirebase(path):
    ref = db.reference(path)
    ref.delete()

    return 'ok'

def updateDataFirebase(path, data):
    ref = db.reference(path)
    ref.update(data)

    return 'ok'

initFirebase()