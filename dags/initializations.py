import firebase_admin
from firebase_admin import credentials, storage, firestore

# Initialize the app with a service account, granting admin privileges
cred = credentials.Certificate("/opt/airflow/dags/serviceKey.json")
# cred = credentials.Certificate("serviceKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': "meetingarchives.appspot.com"
})


def getFirebaseStorageBucket():
    return storage.bucket()


def getFirestoreClient():
    return firestore.client()
