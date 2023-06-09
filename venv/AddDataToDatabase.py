
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("venv\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
	'databaseURL': "https://facerecognittion-a556b-default-rtdb.firebaseio.com/"

	})

ref = db.reference('Students')

data = {
		"123":{
			"Name": "Edgar Mugambi",
			"major": "Computer Science",
			"starting_year": "2017",
			"total_attendance": 7,
			"standing": "G",
			"year": 4,
			"last_attendance_time": "2023-06-06 01:15:10"
		    },
		"145":{
			"Name": "Ted Munene",
			"major": "Student",
			"starting_year": "2022",
			"total_attendance": 12,
			"standing": "T",
			"year": 1,
			"last_attendance_time": "2023-06-05 00:55:10"
		    },
		"234":{
			"Name": "Elon Musk",
			"major": "Machine Learning",
			"starting_year": "2020",
			"total_attendance": 15,
			"standing": "A",
			"year": 3,
			"last_attendance_time": "2023-06-06 01:10:50"
		    }

	}

for key, value in data.items():
	ref.child(key).set(value)