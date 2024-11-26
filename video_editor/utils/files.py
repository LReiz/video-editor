import mimetypes
import os
import ffmpeg
from moviepy.editor import VideoFileClip

def get_video_files(videos_folder):
    """
    Get all video files in a folder.
    """
    video_files = []

    for f in sorted(os.listdir(videos_folder)):
        # Verify if element in folder is a video file
        file_type, _ = mimetypes.guess_type(f)
        if file_type is None or not file_type.startswith('video'):
            continue

        # Add video file to the list
        video_files.append(os.path.join(os.path.abspath(videos_folder), f))

    # Return all videos found in the folder
    return video_files

def format_localhost_filepath(file_path):
    """
    Format the file path to be used in the FCPXML file.
    """
    file_path = f"file://localhost/{os.path.abspath(file_path)}"
    file_path = file_path.replace("\\", "/")
    file_path = file_path.replace(" ", "%20")
    return file_path

def get_video_file_specs(video_path):
    """
    Get the video file specifications.
    """
    # Get video data from FFMPEG
    probe = ffmpeg.probe(video_path, v='error', select_streams='v:0', show_entries='stream=nb_frames')
    num_frames = int(probe['streams'][0]['nb_frames'])

    # Get video data from MoviePy
    with VideoFileClip(video_path) as video:
        width, height = video.size
        audio_channels = video.audio.nchannels if video.audio.nchannels is not None else 0
        filename = os.path.basename(video_path)
        fps = int(video.fps)
        localhost_path = format_localhost_filepath(str(video_path))
    
    return {
        'num_frames': num_frames,
        'width': width,
        'height': height,
        'audio_channels': audio_channels,
        'filename': filename,
        'localhost_path': localhost_path,
        'fps': fps
    }
