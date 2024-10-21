"""
This class get all the video files in the input folder and concatenate them into the Timeline.
"""
import os
from moviepy.editor import VideoFileClip
from lxml import etree
import ffmpeg


class Concatenate:
    def __init__(self, timeline, videos_folder):
        self.timeline = timeline
        self.videos_folder = videos_folder
        self.total_frames = 0
        self.fps = 0
        
        # This will hold all video data, such as: width, height, fps, ...
        self.videos_data = []

        # This variables are cumulative as we add elements to the timeline
        self.resource_id = 0
        self.cumulative_duration = (0, 0)


    def format_file_path(self, file_path):
        """
        Format the file path to be used in the FCPXML file.
        """
        file_path = os.path.join(self.videos_folder, file_path)
        file_path = f"file://localhost/{os.path.abspath(file_path)}"
        file_path = file_path.replace("\\", "/")
        file_path = file_path.replace(" ", "%20")
        return file_path


    def get_video_data(self, index, data_type):
        """
        Get the video data for the video file.
        """
        return self.videos_data[index][data_type]
    

    def create_format_element(self, resources, index):
        """
        Create the format element for the video file.
        """
        # Get video data
        fps = int(self.get_video_data(index, 'fps'))
        width = self.get_video_data(index, 'width')
        height = self.get_video_data(index, 'height')

        # Create the format element
        format_element = etree.SubElement(resources, 'format')
        format_element.set('id', f"r{self.resource_id}")
        format_element.set('frameDuration', f"1/{fps}s")  # Placeholder for frame duration
        format_element.set('width', str(width))
        format_element.set('height', str(height))
        format_element.set('name', 'FFVideoFormatRateUndefined')
        self.fps = fps
        self.resource_id += 1


    def create_asset_element(self, resources, index):
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
        asset_element = etree.SubElement(resources, 'asset')
        """
        Note:
            Duration calculations are currently not very precise. It's differing from Davinci `.fcpxml` file
            for the same videos. We need to find a better way to calculate the duration. Although, it doesn't
            seem to visually affect the final video.
        """
        asset_element.attrib.update({
            'duration': f"{num_frames}/{fps}s",
            'hasVideo': '1',
            'id': f"r{self.resource_id}",
            'audioSources': '1',  # Placeholder for audio sources
            'hasAudio': '1' if audio_channels > 0 else '0',
            'start': '0/1s',  # Placeholder start
            'name': filename,
            'audioChannels': str(audio_channels),
            'format': "r0",
        })

        self.total_frames += num_frames

        # Create the media element
        media = etree.SubElement(asset_element, 'media-rep')
        media.set('src', filepath)
        media.set('kind', 'original-media')
        self.resource_id += 1
    

    def store_video_data(self, video_path, resource_id):
        """
        Store video data for later use.
        """
        # Get video data from FFMPEG
        probe = ffmpeg.probe(video_path, v='error', select_streams='v:0', show_entries='stream=nb_frames')
        num_frames = int(probe['streams'][0]['nb_frames'])

        # Get video data from MoviePy
        with VideoFileClip(video_path) as video:
            width, height = video.size
            audio_channels = video.audio.nchannels if video.audio.nchannels is not None else 0
            filename = os.path.basename(video_path)
            filepath = self.format_file_path(str(video_path))
            fps = video.fps

        self.videos_data.append({
            "width": width,
            "height": height,
            "audio_channels": audio_channels,
            "filename": filename,
            "filepath": filepath,
            "fps": fps,
            "num_frames": num_frames,
            "resource_id": resource_id,
        })


    def add_resource(self, video_path, index):
        """
        Add resource to the FCPXML object.
        """
        # Ignore if video_path is not a file
        if not os.path.isfile(video_path):
            print(f"Not a file. Ignoring: {video_path}")
            return
        
        self.store_video_data(video_path, index+1)

        # Create the resources element if it doesn't exist
        resources = self.timeline.fcpxml.find('resources')
        if resources is None:
            resources = etree.SubElement(self.timeline.fcpxml, 'resources')

        # Get format element
        format_element = resources.find('format')
        if format_element is None:
            # Create the format element
            """
            Note:
                For now we'll use the same format for all the videos. But this may need to be changed to handle
                multiple different formats.
            """
            self.create_format_element(resources, index)

        # Create the asset element
        self.create_asset_element(resources, index)

    def add_clip_to_timeline(self, spine, index):
        """
        Add the clip to the timeline.
        """
        # Get video data
        video_id = self.get_video_data(index, 'resource_id')
        num_frames = self.get_video_data(index, 'num_frames')
        filename = self.get_video_data(index, 'filename')
        fps = int(self.get_video_data(index, 'fps'))

        # Create the clip element
        asset_clip = etree.SubElement(spine, 'asset-clip')
        asset_clip_attributes = {
            'ref': f"r{video_id}",
            'duration': f"{num_frames}/{fps}s",
            'tcFormat': 'NDF',
            'enabled': '1',
            'offset':  '0/1s' if index == 0 else f"{self.cumulative_duration[0]}/{self.cumulative_duration[1]}s",
            'start': '0/1s',
            'format': 'r0',
            'name': filename,
        }
        self.timeline.video_assets_refs.append(asset_clip_attributes['ref'])
        self.timeline.video_assets[asset_clip_attributes['ref']] = [asset_clip]
        asset_clip.attrib.update(asset_clip_attributes)
        self.cumulative_duration = (self.cumulative_duration[0] + num_frames, fps)

        # Create Adjust Transform element
        adjust_transform = etree.SubElement(asset_clip, 'adjust-transform')
        adjust_transform.attrib.update({
            'position': '0 0',
            'anchor': '0 0',
            'scale': '1 1',
        })


    def add_timeline(self):
        """
        Add the timeline elements to the FCPXML object.
        """
        # Create the library element
        library = etree.SubElement(self.timeline.fcpxml, 'library')

        # Create the event element
        event = etree.SubElement(library, 'event')
        event.set('name', 'Timeline 1')

        # Create the project element
        project = etree.SubElement(event, 'project')
        project.set('name', 'Timeline 1')

        # Create the sequence element
        sequence = etree.SubElement(project, 'sequence')
        sequence.attrib.update({
            'duration': f"{self.total_frames}/{self.fps}s",
            'tcFormat': 'NDF',
            'tcStart': '0/1s',
            'format': 'r0'
        })

        # Create the spine element
        spine = etree.SubElement(sequence, 'spine')
        self.timeline.spine = spine

        # Create the asset-clips elements
        for index in range(len(self.videos_data)):
            self.add_clip_to_timeline(spine, index)


    def concatenate_video_files(self):
        """
        Concatenate all the video files in the input folder.
        """
        print("Concatenating files...")
        # Get all the video files in alphabetical order from the input folder
        video_files = [
            os.path.join(os.path.abspath(self.videos_folder), f) for f in sorted(os.listdir(self.videos_folder))
        ]

        # Concatenate the video files
        for index, video_file in enumerate(video_files):
            self.add_resource(video_file, index)
            print(f"Resource created for file: {video_file}")
        
        # Add the timeline elements
        self.add_timeline()

        print("Files concatenated successfully.")
