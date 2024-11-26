"""
This class get all the video files in the input folder and concatenate them into the Timeline.
"""
import os

from utils.files import get_video_files, get_video_file_specs
from entities.timeline import Timeline


class Concatenate:
    def __init__(self, timeline: Timeline, videos_folder):
        self.timeline = timeline
        self.videos_folder = videos_folder
        self.fps = 0
        
        # This will hold all video data, such as: width, height, fps, ...
        self.videos_data = []

        # This variables are cumulative as we add elements to the timeline
        self.cumulative_duration = (0, 0)


    def get_video_data(self, index, data_type):
        """
        Get the video data for the video file.
        """
        return self.videos_data[index][data_type]
    

    def create_format_element(self, index):
        """
        Create the format element for the video file.
        """
        # Get video data
        fps = int(self.get_video_data(index, 'fps'))
        width = self.get_video_data(index, 'width')
        height = self.get_video_data(index, 'height')
        name = 'DefaultVideoFormat'

        # Create the format element
        self.timeline.add_format_element(fps, width, height, name)


    def create_asset_element(self, index):
        """
        Create the asset element for the video file.
        """
        # Get video data
        audio_channels = self.get_video_data(index, 'audio_channels')
        filename = self.get_video_data(index, 'filename')
        filepath = self.get_video_data(index, 'filepath')
        num_frames = self.get_video_data(index, 'num_frames')
        fps = int(self.get_video_data(index, 'fps'))

        # Create the asset element
        self.timeline.add_asset_element(fps, num_frames, audio_channels, filename, filepath)


    def store_video_data(self, video_path, resource_id):
        """
        Store video data for later use.
        """
        # Get video specs
        video_specs = get_video_file_specs(video_path)

        self.videos_data.append({
            "width": video_specs['width'],
            "height": video_specs['height'],
            "audio_channels": video_specs['audio_channels'],
            "filename": video_specs['filename'],
            "filepath": video_specs['localhost_path'],
            "fps": video_specs['fps'],
            "num_frames": video_specs['num_frames'],
            "resource_id": resource_id,
        })


    def add_resource(self, video_path, index):
        """
        Add resource to the FCPXML object.
        """
        # Store video data
        self.store_video_data(video_path, index+1)

        # Get resources element from Timeline
        resources = self.timeline.resources

        # Get format element
        format_element = resources.find('format')
        if format_element is None:
            # Create the format element
            """
            Note:
                For now we'll use the same format for all the videos. But this may need to be changed to handle
                multiple different formats.
            """
            self.create_format_element(index)

        # Create the asset element
        self.create_asset_element(index)

    def add_clip_to_timeline(self, index):
        """
        Add the clip to the timeline.
        """
        # Get video data
        video_id = self.get_video_data(index, 'resource_id')
        num_frames = self.get_video_data(index, 'num_frames')
        filename = self.get_video_data(index, 'filename')
        fps = int(self.get_video_data(index, 'fps'))
        video_ref = f"r{video_id}"

        # Create the clip element
        self.timeline.add_clip_to_timeline(video_ref, num_frames, 0, self.cumulative_duration[0], fps, filename)

        self.cumulative_duration = (self.cumulative_duration[0] + num_frames, fps)


    def add_timeline(self):
        """
        Add the timeline elements to the FCPXML object.
        """
        # Create timeline structure
        self.timeline.create_timeline_structure()

        # Create the asset-clips elements
        for index in range(len(self.videos_data)):
            self.add_clip_to_timeline(index)
        
        # Update sequence duration
        self.timeline.update_sequence_duration()


    def concatenate_video_files(self):
        """
        Concatenate all the video files in the input folder.
        """
        print("Concatenating files...")
        # Get all the video files in alphabetical order from the input folder
        video_files = get_video_files(self.videos_folder)

        # Concatenate the video files
        for index, video_file in enumerate(video_files):
            self.add_resource(video_file, index)
            print(f"Resource created for file: {video_file}")

        # Add the timeline elements
        self.add_timeline()

        print("Files concatenated successfully.")
