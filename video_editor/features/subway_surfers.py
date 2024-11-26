"""
This class adds Subway Surfers to video to retain people with an attention span of a goldfish.
"""
import os
import random

from utils.files import get_video_files, get_video_file_specs
from entities.timeline import Timeline


class SubwaySurfers:
    def __init__(self, timeline: Timeline):
        self.subway_surfers_folder = os.path.join(os.path.dirname(__file__), '../../assets/subway_surfers')
        self.timeline: Timeline = timeline
        self.timeline_shift_ratio = 20
    
    def get_subway_surfers_video(self):
        """
        Get Subway Surfers video.
        """
        # Get possible videos in the folder
        video_files = get_video_files(self.subway_surfers_folder)

        # Draw a random video from file
        index = random.randint(0, len(video_files) - 1)
        return video_files[index] if video_files else None

    def add_video_format_resource(self, video_specs):
        """
        Add video format resource to the timeline.
        """
        # Add format element to resources
        return self.timeline.add_format_element(video_specs['fps'], video_specs['width'], video_specs['height'], 'SubwaySurfersVideoFormat')

    def add_asset_element(self, video_specs, format_id):
        """
        Add asset element to the resources.
        """
        # Add asset element to resources
        return self.timeline.add_asset_element(
            video_specs['fps'],
            video_specs['num_frames'],
            video_specs['audio_channels'],
            video_specs['filename'],
            video_specs['localhost_path'],
            format=format_id
        )
    
    def add_subway_surfers_clips(self, asset, timeline_duration: int, video_specs, format_elem):
        """
        Add Subway Surfers clips to the whole duration of the video.
        """
        covered_duration = 0

        while covered_duration < timeline_duration:
            # Add Subway Surfers clip to the timeline
            clip = self.timeline.add_clip_to_timeline(
                video_ref=asset.attrib['id'],
                num_frames=str(min(timeline_duration - covered_duration, video_specs['num_frames'])),
                start='0',
                offset=str(covered_duration),
                fps=video_specs['fps'],
                filename=video_specs['filename'],
                lane='2',
                format=format_elem.attrib['id'],
                include_audio=False,
            )

            # Edit the clip
            self.edit_subway_surfers_clip(clip, video_specs)

            covered_duration += video_specs['num_frames']
    
    def shift_timeline_clips_up(self):
        """
        Shift timeline clips up to make space for Subway Surfers.
        """
        # Iterate over all clips in the timeline
        for ref in self.timeline.video_assets_refs:
            for clip in self.timeline.video_assets[ref]:

                # Get clip data
                self.timeline.move_clip(clip, x=0, y=self.timeline_shift_ratio)

    def edit_subway_surfers_clip(self, clip, video_specs):
        """
        Edit the Subway Surfers clip to occupy the bottom half of the screen.
        """
        # Get clip height in project
        clip_project_height = video_specs['height'] * self.timeline.width / video_specs['width']

        # Get the wanted zoom ratio
        zoom_ratio = self.timeline.height / (clip_project_height * 2)

        # Get relative position of the clip
        y_position = - (self.timeline.height / 4) / clip_project_height
        y_position *= 100

        # Edit the clip
        self.timeline.zoom_clip(clip, zoom_ratio)
        self.timeline.move_clip(clip, x=0, y=y_position)

    def add_subway_surfers(self):
        """
        Add Subway Surfers to the video.
        """
        # Get timeline current duration in frames
        sequence_frames, sequence_fps = map(int, self.timeline.get_sequence_duration())

        # Get Subway Surfers video
        subway_surfers_video = self.get_subway_surfers_video()

        # Add Subway Surfers to the timeline
        if not subway_surfers_video:
            print('No Subway Surfers video found.')
            return
        
        # Shift timeline clips up to make space for Subway Surfers
        self.shift_timeline_clips_up()
        
        # Get video specs
        video_specs = get_video_file_specs(subway_surfers_video)

        # Convert timeline duration to Subway Surfers fps
        fps = int(video_specs['fps'])
        duration = int((fps/sequence_fps) * sequence_frames)

        # Add Subway Surfers video format resource
        format_elem = self.add_video_format_resource(video_specs)

        # Add Subway Surfers asset
        asset = self.add_asset_element(video_specs, format_id=format_elem.attrib['id'])

        # Add Subway Surfers video to the timeline
        self.add_subway_surfers_clips(asset, duration, video_specs, format_elem)
