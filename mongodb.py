from pymongo import MongoClient
import datetime
import os
import certifi

ca = certifi.where()
password = os.getenv('APP_PASSWORD')
cluster = f'mongodb+srv://kaustubh43:{password}@cluster1.au46pco.mongodb.net/?retryWrites=true&w=majority'
# Database Name = Portfolio
# Collection Name = Form_Submissions
client = MongoClient(cluster, tlsCAFile=ca)  # Connect to MongoDB
db = client.Portfolio
collection_obj = db.Form_Submissions


def insert_into_mongoDB(data):
    entry_in_form = {"email": data["email"],
                     "subject": data["subject"],
                     "message": data["message"],
                     "date": datetime.datetime.utcnow()
                     }
    try:
        result = collection_obj.insert_one(entry_in_form)
    except:
        print("Did not save into Database")
