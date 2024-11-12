import mimetypes
import os

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
