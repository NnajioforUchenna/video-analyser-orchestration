import time
from celery import Celery, group
from moviepy.editor import VideoFileClip
import os

app = Celery('video_audio_spliting', broker='redis://redis-celery:6379/0', backend='redis://redis-celery:6379/0')

@app.task
def encode_video_chunk(video_path, start_time, end_time, output_path):
    print(f"Starting video chunk encoding from {start_time} to {end_time} into {output_path}")
    clip = VideoFileClip(video_path).subclip(start_time, end_time)
    clip.write_videofile(output_path, codec='libx264')
    print(f"Finished video chunk encoding: {output_path}")
    return output_path

@app.task
def encode_audio_chunk(video_path, start_time, end_time, output_path):
    print(f"Starting audio chunk encoding from {start_time} to {end_time} into {output_path}")
    clip = VideoFileClip(video_path).subclip(start_time, end_time)
    clip.audio.write_audiofile(output_path)
    print(f"Finished audio chunk encoding: {output_path}")
    return output_path

def get_chunk_times(video_path, interval_minutes=10):
    print("Calculating chunk times...")
    clip = VideoFileClip(video_path)
    total_duration = clip.duration
    seconds_per_chunk = interval_minutes * 60  # 10 minutes in seconds

    chunk_times = []
    start_time = 0
    while start_time < total_duration:
        end_time = min(start_time + seconds_per_chunk, total_duration)
        chunk_times.append((start_time, end_time))
        start_time = end_time

    print(f"Chunk times calculated: {chunk_times}")
    return chunk_times

@app.task
def split_video_into_chunks(video_path, output_folder='output'):
    print(f"Starting to split video: {video_path}")
    start_time = time.time()  # Start the timer

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = f"{output_folder}_{base_name}"  # Add base_name to output_folder

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    chunk_times = get_chunk_times(video_path)

    video_tasks = []
    audio_tasks = []

    for i, (start_time, end_time) in enumerate(chunk_times):
        video_output_path = os.path.join(output_folder, f"{base_name}_chunk_{i + 1}.mp4")
        audio_output_path = os.path.join(output_folder, f"{base_name}_chunk_{i + 1}.mp3")
        video_tasks.append(encode_video_chunk.s(video_path, start_time, end_time, video_output_path))
        audio_tasks.append(encode_audio_chunk.s(video_path, start_time, end_time, audio_output_path))

    job = group(video_tasks + audio_tasks)
    result = job.apply_async()

    result.save()  # Save the result to backend

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    print(f"All tasks completed. Chunks saved to: {output_folder}")
    print(f"Total time taken: {elapsed_time:.2f} seconds")

    return output_folder
