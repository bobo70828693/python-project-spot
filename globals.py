import FirebaseConnect


def initializeSpot():
    global spotData
    spotData = FirebaseConnect.getDataFirebase('spotInform')
initializeSpot()