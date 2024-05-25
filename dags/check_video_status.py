from initializations import getFirestoreClient


def checkVideoStatus(videos):
    firebaseClient = getFirestoreClient()
    batch = firebaseClient.batch()
    videos_to_be_processed = []

    # Retrieve all ProcessedVideos documents at once
    processed_videos_ref = firebaseClient.collection("ProcessedVideos")
    processed_videos_docs = processed_videos_ref.get()
    processed_videos = {doc.id: doc.get("status") for doc in processed_videos_docs}

    for video in videos:
        if video.file_id not in processed_videos:
            videos_to_be_processed.append(video.toMap())
            video_ref = firebaseClient.collection("VideosToBeProcessed").document(video.file_id)
            batch.set(video_ref, video.toMap())
        else:
            print(f"{video.file_name} ({video.file_id}) - Already processed")

    batch.commit()
    return videos_to_be_processed


def setCurrentVideoToProcessed():
    firebaseClient = getFirestoreClient()
    videos_to_be_processed_ref = firebaseClient.collection("VideosToBeProcessed")
    videos_to_be_processed_docs = videos_to_be_processed_ref.get()
    # return the first video in to be processed
    if len(videos_to_be_processed_docs) == 0:
        return []
    currentVideoToProcess = videos_to_be_processed_docs[0].to_dict()
    current_ref = firebaseClient.collection("CurrentProcessingVideo").document('current_processing_video')
    current_ref.set(currentVideoToProcess)
    return currentVideoToProcess


def getCurrentVideoToProcessed():
    firebaseClient = getFirestoreClient()
    currentVideoToProcess_ref = firebaseClient.collection("CurrentProcessingVideo").document('current_processing_video')
    currentVideoToProcess = currentVideoToProcess_ref.get()
    return currentVideoToProcess.to_dict()
