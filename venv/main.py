from datetime import datetime
from itertools import count
import pickle
import face_recognition
import cv2
import os
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np

cred = credentials.Certificate("venv\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
	'databaseURL': "https://facerecognittion-a556b-default-rtdb.firebaseio.com/",
    'storageBucket' : "facerecognittion-a556b.appspot.com"
	})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4,480)

imgBackground = cv2.imread('Resources\Backgroundd.PNG')

#importing mode image
folderModePath = 'Resources\Modes'
modePathList = os.listdir(folderModePath)
imgModeList =[]
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
    
#print(modePathList)

#loading the encoding file
print("Loading Encoded ...")
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds 
#print(studentIds)
print("Encoded file Loaded...")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success , img = cap.read()

    imgS = cv2.resize(img,(0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[175:175+480, 55:55+640] = img
    imgBackground[44:44+633, 708:708+300]=imgModeList[modeType]

    if faceCurFrame:
        for encodeFace , FaceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            #print("matches", matches)
            #print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            #print("Match Index", matchIndex)

            if matches[matchIndex]:
                #print("Known Face Detected")
                #print(studentIds[matchIndex])
                y1,x2,y2,x1 = FaceLoc
                y1,x2,y2,x1= y1*4,x2*4,y2*4,x1*4
                bbox = 55 + x1, 175 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt = 0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275,400))
                    cv2.imshow("Face Capture", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

            if counter != 0:

                if counter ==1:
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)

                    #get image from storage 
                    blob = bucket.get_blob(f'Images/{id}.jpeg')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                    #update Data of Attendance
                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                      "%Y-%m-%d %H:%M:%S")

                    secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                    print(secondsElapsed)
                    if secondsElapsed > 120:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else: 
                        modeType = 3
                        counter = 0
                        imgBackground[44:44+633, 708:708+300]=imgModeList[modeType]

                

            

                if modeType != 3:

                    if 10<counter<20:
                        modeType = 2

                    imgBackground[44:44+633, 708:708+300]=imgModeList[modeType]

            
                    if counter <= 10:
                       cv2.putText(imgBackground, str(studentInfo['total_attendance']), (750,125),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                       cv2.putText(imgBackground, str(studentInfo['major']), (808,523),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                       cv2.putText(imgBackground, str(id), (837,445),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                       cv2.putText(imgBackground, str(studentInfo['standing']), (789,637),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                       cv2.putText(imgBackground, str(studentInfo['year']), (858,637),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                       cv2.putText(imgBackground, str(studentInfo['starting_year']), (950,637),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                       (w, h), _ = cv2.getTextSize(studentInfo['Name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                       offset = (300 - w)//2
                       cv2.putText(imgBackground, str(studentInfo['Name']), (808+offset,400),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                       imgBackground[145:145+216,750:750+216] = imgStudent
           


                    counter+=1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44:44+633, 708:708+300]=imgModeList[modeType]

    else: 
        modeType = 0
        counter = 0

    #cv2.imshow("WebCam", img)
    cv2.imshow("Face Capture", imgBackground)
    cv2.waitKey(0)





























