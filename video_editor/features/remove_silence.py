"""
This class is used to remove all silence parts from video timeline.
"""
import subprocess
import os
import json
from copy import deepcopy
import ffmpeg


class RemoveSilence:
    def __init__(self, timeline, videos_folder, margin=0.1):
        self.timeline = timeline

        # Loud maps settings
        self.videos_folder = videos_folder
        self.loud_maps_folder = os.path.join(videos_folder, 'remove_silence')
        self.loud_map_sufix = '_loud_map.json'

        # Preview video settings
        self.loud_video_preview_sufix = '_preview.mp4'
        self.preview_videos_list_file = os.path.join(self.loud_maps_folder, 'videos.txt')
        self.preview_final_video = os.path.join(self.loud_maps_folder, 'final_preview.mp4')

        # General settings
        self.cumulative_duration = 0        
        self.margin = f"{margin}sec"

    def generate_video_loud_map(self, video_path, video_name):
        """
        This detect all parts of the video with sound louder than the threshold.
        """
        # Define the path to your video file
        command = [
            "auto-editor",
            video_path,
            "--export-as-json",
            "--margin",
            self.margin,
            "--output-file",
            os.path.join(self.loud_maps_folder, f"{video_name}{self.loud_map_sufix}")
        ]

        # Execute the command
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print(result.stdout)  # Output from the command
            print(f"Loud Map generated successfully! Input: {video_path}")
        except subprocess.CalledProcessError as e:
            print("An error occurred:", e.stderr)  # Error output


    def generate_loud_video_preview(self, video_path, video_name):
        """
        This method generate preview videos for all videos in the folder.
        """
        command = [
            "auto-editor",
            video_path,
            "--margin",
            self.margin,
            "--output-file",
            os.path.join(self.loud_maps_folder, f"{video_name}{self.loud_video_preview_sufix}"),
            "--no-open"
        ]
        
        # Execute the command
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print(result.stdout)  # Output from the command
            print(f"Loud Video preview generated successfully! Input: {video_path}")
        except subprocess.CalledProcessError as e:
            print("An error occurred:", e.stderr)  # Error output


    def generate_loud_map_for_each_video_in_folder(self):
        """
        This method remove all silence parts from video timeline.
        """
        video_files = [
            os.path.join(os.path.abspath(self.videos_folder), f) for f in sorted(os.listdir(self.videos_folder))
        ]

        os.makedirs(self.loud_maps_folder, exist_ok=True)

        for video in sorted(video_files):
            if not os.path.isfile(video):
                continue

            video_path = video
            video_name = os.path.basename(video_path).split('.')[0]
            self.generate_video_loud_map(video_path, video_name)
    

    def get_loud_map(self, video_name):
        """
        This method return the loud map for a video.
        """
        loud_map_path = os.path.join(self.loud_maps_folder, f"{video_name}{self.loud_map_sufix}")
        with open(loud_map_path, 'r') as file:
            return json.load(file)


    def remove_silence(self):
        """
        This method remove all silence parts from video timeline.
        """
        for ref in self.timeline.video_assets_refs:
            # Get loud map for the video
            base_asset_clip = self.timeline.video_assets[ref][0]
            filename = base_asset_clip.attrib['name'].split('.')[0]
            loud_map_json = self.get_loud_map(filename)
            loud_map = loud_map_json['v'][0]
            timebase = loud_map_json['timebase'].split('/')[0]

            previous_video_duration = self.cumulative_duration
            
            # Split asset clip in loud parts
            for loud_part in loud_map:
                # Create new asset clip
                asset_clip = deepcopy(base_asset_clip)
                asset_clip.attrib.update({
                    # **Note:** auto-editor returns start and offset element switched
                    'start': f"{loud_part['offset']}/{timebase}s",
                    'offset': f"{previous_video_duration + loud_part['start']}/{timebase}s",
                    'duration': f"{loud_part['dur']}/{timebase}s",
                })
                self.timeline.spine.append(asset_clip)
                self.cumulative_duration += loud_part['dur']
            
            self.timeline.spine.remove(base_asset_clip)
    
    def remove_silence_from_videos(self):
        """
        This method remove all silence parts from video timeline based on a generated loud map.
        """
        # Generate loud maps for all videos
        self.generate_loud_map_for_each_video_in_folder()

        # Remove silence from videos
        self.remove_silence()


    def generate_previews_for_videos(self):
        """
        This method generate preview videos for all videos in the folder.
        """
        video_files = [
            os.path.join(os.path.abspath(self.videos_folder), f) for f in sorted(os.listdir(self.videos_folder))
        ]

        os.makedirs(self.loud_maps_folder, exist_ok=True)

        for video in sorted(video_files):
            if not os.path.isfile(video):
                continue

            video_path = video
            video_name = os.path.basename(video_path).split('.')[0]
            self.generate_loud_video_preview(video_path, video_name)
    
    def join_all_preview_videos(self):
        """
        This method join all preview videos in a single video.
        """
        # Get all preview videos
        preview_videos = [
            os.path.join(self.loud_maps_folder, f) for f in sorted(os.listdir(self.loud_maps_folder))
            if f.endswith(self.loud_video_preview_sufix)
        ]

        with open(self.preview_videos_list_file, 'w') as f:
            for video in preview_videos:
                f.write(f"file '{video}'\n")

        # Run the ffmpeg concat command
        (
            ffmpeg
            .input(self.preview_videos_list_file, format='concat', safe=0)
            .output(self.preview_final_video, c='copy')
            .run(overwrite_output=True)  # Overwrite if output exists
        )

    def generate_final_preview_video(self):
        """
        This method generate the final preview video. This can be used to generate subtitles.
        """
        self.generate_previews_for_videos()
        self.join_all_preview_videos()
        print("Final preview video generated successfully!")
