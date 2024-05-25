from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from check_video_status import checkVideoStatus

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly", "https://www.googleapis.com/auth/drive.readonly"]


class videoInfo:
    def __init__(self, file_id, file_name, file_extension):
        self.file_id = file_id
        self.file_name = file_name
        self.file_extension = file_extension

    def toMap(self):
        return {
            "file_id": self.file_id,
            "file_name": self.file_name,
            "file_extension": self.file_extension
        }


def getNewSessions():


    try:
        creds = Credentials.from_authorized_user_file("/opt/airflow/dags/token.json",SCOPES)
        print('I got the files')
        service = build("drive", "v3", credentials=creds)

        # Get all files in the drive
        results = service.files().list(fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get("files", [])

        while "nextPageToken" in results:
            results = service.files().list(pageToken=results["nextPageToken"],
                                           fields="nextPageToken, files(id, name, mimeType)").execute()
            items.extend(results.get("files", []))

        if not items:
            print("No files found.")
            return

        videos = {}
        for item in items:
            file_name = item["name"]
            file_id = item["id"]
            mime_type = item["mimeType"]
            if mime_type == "video/mp4":
                videos[file_id] = videoInfo(file_id, file_name, 'mp4')
            print(f"{file_name} ({file_id}) - {mime_type}")

        NewSessions = checkVideoStatus(videos.values())
        return NewSessions

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")

