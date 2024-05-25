import re
import io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly", "https://www.googleapis.com/auth/drive.readonly"]


class DownloadedFile:
    def __init__(self, content, name):
        self.content = content
        self.name = name


def get_video_uid(url):
    # Regular expression to match the UID in the Google Drive URL
    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    else:
        return None


def format_file_name(original_name):
    name_pattern = r'.*\(([\d-]+) ([\d:]+) GMT\)'
    match = re.match(name_pattern, original_name)
    if match:
        date_str = match.group(1)
        time_str = match.group(2).replace(':', '_')
        return f"{date_str}_{time_str}.mp4"
    else:
        return "downloaded_video.mp4"


def download_video_with_file_id(file_id):
    # Load credentials from file
    creds = Credentials.from_authorized_user_file("/opt/airflow/dags/token.json",SCOPES)

    # Build the service from the credentials
    service = build('drive', 'v3', credentials=creds)

    try:
        # Get the file metadata to retrieve the file name
        file_metadata = service.files().get(fileId=file_id, fields='name').execute()
        file_name = file_metadata['name']
        print(f"File name: {file_name}")
        print(format_file_name(file_name))

        # Request to download the file
        request = service.files().get_media(fileId=file_id)
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}% complete.")

        file_content = file_io.getvalue()
        return DownloadedFile(content=file_content, name=file_name)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def write_video_to_memory(downloaded_file):
    if downloaded_file and downloaded_file.content:
        # Format the file name
        new_name = format_file_name(downloaded_file.name)

        # Save the file to disk
        with open(new_name, 'wb') as file:
            file.write(downloaded_file.content)
        print(f"The video has been downloaded and saved successfully as {new_name}.")
        return new_name
    else:
        print("Failed to download the video.")
        return None


def download_video_from_drive(newSession):
    file_id = newSession['file_id']
    downloaded_file = download_video_with_file_id(file_id)
    if downloaded_file:
        return write_video_to_memory(downloaded_file)
    else:
        return None
