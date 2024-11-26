"""
This entity represents the final timeline.
"""
from lxml import etree
import os
from typing import Any, Dict, List
from copy import deepcopy


class Timeline():
    def __init__(self, videos_folder):
        self.fcpxml = etree.Element('fcpxml', version="1.11")
        self.resources = etree.SubElement(self.fcpxml, 'resources')
        self.tree = etree.ElementTree(self.fcpxml)
        self.spine = None
        self.sequence = None
        self.video_assets_refs: List[str] = []
        self.video_assets: Dict[str, Any] = {}
        self.resource_id = 0
        self.height = None
        self.width = None

        self.output_folder = os.path.join(videos_folder, 'timeline')
        self.fcpxml_filename = os.path.join(self.output_folder, 'timeline.fcpxml')

    def create_timeline_structure(self):
        """
        Create the basic timeline structure.
        """
        # Create the library element
        library = etree.SubElement(self.fcpxml, 'library')

        # Create the event element
        event = etree.SubElement(library, 'event')
        event.set('name', 'Timeline 1')

        # Create the project element
        project = etree.SubElement(event, 'project')
        project.set('name', 'Timeline 1')

        # Create the sequence element
        self.sequence = etree.SubElement(project, 'sequence')
        self.sequence.attrib.update({
            'duration': '0/1s', # Placeholder for durations
            'tcFormat': 'NDF',
            'tcStart': '0/1s',
            'format': 'r0'
        })

        # Create the spine element
        spine = etree.SubElement(self.sequence, 'spine')
        self.spine = spine


    def add_default_header(self, file):
        """
        Add the default header to the FCPXML file.
        """
        file.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(b'<!DOCTYPE fcpxml>\n')


    def generate_fcpxml_file(self):
        """
        Create the FCPXML file.
        """
        os.makedirs(self.output_folder, exist_ok=True)

        with open(self.fcpxml_filename, 'wb') as file:
            # Write default configuration in file
            self.add_default_header(file)

            # Indent the tree to 4 spaces
            etree.indent(self.tree, space='    ')

            # Add FCPXML tree to the file
            self.tree.write(file, encoding='UTF-8', pretty_print=True)

        print("FCPXML file created successfully.")
    
    def store_video_ref(self, video_ref):
        """
        Add video reference to an array.

        NOTE:
            - Video reference is an ID to that video file. Example: r1, r2, r3, etc.
        """
        self.video_assets_refs.append(video_ref)
    
    def store_video_asset(self, video_ref, video_asset):
        """
        Add video asset to the timeline.
        """
        # If the video reference already exists, append the video asset to the list
        if video_ref in self.video_assets:
            self.video_assets[video_ref].append(video_asset)
        else:
            self.video_assets[video_ref] = [video_asset]

    def get_stored_video_asset(self, video_ref, index):
        """
        Get video asset from the timeline.
        """
        return self.video_assets[video_ref][index]
    
    def remove_stored_video_asset(self, video_ref, index):
        """
        Remove video asset from the timeline.
        """
        asset_clip = self.video_assets[video_ref].pop(index)
        self.spine.remove(asset_clip)
    
    def add_format_element(self, fps, width, height, name) -> etree.Element:
        """
        Add format element to the resources.
        """
        # Set up project dimenstions if it's the first format element
        if self.resource_id == 0:
            self.height = height
            self.width = width

        # Create the format element
        format_element = etree.SubElement(self.resources, 'format')
        format_element.set('id', f"r{self.resource_id}")
        format_element.set('frameDuration', f"1/{fps}s")  # Placeholder for frame duration
        format_element.set('width', str(width))
        format_element.set('height', str(height))
        format_element.set('name', name)
        self.fps = fps
        self.resource_id += 1

        return format_element

    def add_asset_element(self, fps, num_frames, audio_channels, filename, filepath, format='r0') -> etree.Element:
        """
        Add asset element to the resources.
        """
        asset_element = etree.SubElement(self.resources, 'asset')
        asset_ref = f"r{self.resource_id}"

        """
        Note:
            Duration calculations are currently not very precise. It's differing from Davinci `.fcpxml` file
            for the same videos. We need to find a better way to calculate the duration. Although, it doesn't
            seem to visually affect the final video.
        """
        # Create the asset element
        asset_element.attrib.update({
            'duration': f"{num_frames}/{fps}s",
            'hasVideo': '1',
            'id': asset_ref,
            'audioSources': '1',  # Placeholder for audio sources
            'hasAudio': '1' if audio_channels > 0 else '0',
            'start': '0/1s',  # Placeholder start
            'name': filename,
            'audioChannels': str(audio_channels),
            'format': format,
        })

        # Create the media element
        media = etree.SubElement(asset_element, 'media-rep')
        media.set('src', filepath)
        media.set('kind', 'original-media')
        self.resource_id += 1

        # Store asset reference
        self.store_video_ref(asset_ref)

        return asset_element

    def add_adjust_transform_element(self, clip) -> etree.Element:
        """
        Add adjust-transform element to the clip.
        """
        adjust_transform = etree.SubElement(clip, 'adjust-transform')
        adjust_transform.attrib.update({
            'position': '0 0',
            'anchor': '0 0',
            'scale': '1 1',
        })

        return adjust_transform

    def add_clip_to_timeline(self, video_ref, num_frames, start, offset, fps, filename, lane=0, custom_attrib={}, format='r0', include_audio=True) -> etree.Element:
        """
        Add video clip to the timeline.
        """
        # Define Element type
        element_type = 'asset-clip' if include_audio else 'clip'

        # Create Asset Clip element
        asset_clip = etree.SubElement(self.spine, element_type)
        asset_clip_attributes = {
            'ref': video_ref,
            'duration': f"{num_frames}/{fps}s",
            'tcFormat': 'NDF',
            'enabled': '1',
            'offset':  f"{offset}/{fps}s",
            'start': f"{start}/{fps}s",
            'format': format,
            'name': filename,
            'lane': f"{lane}",
            **custom_attrib,
        }
        asset_clip.attrib.update(asset_clip_attributes)

        self.store_video_asset(video_ref, asset_clip)

        # Create Adjust Transform element
        self.add_adjust_transform_element(asset_clip)

        # Create Visual element for mute clips
        if not include_audio:
            video = etree.SubElement(asset_clip, 'video')
            video.attrib.update({
                'ref': video_ref,
                'start': '0/1s',
                'offset': '0/1s',
                'duration': f"{num_frames}/{fps}s",
            })

        return asset_clip
    
    def add_clip_to_timeline_based_on_clip(self, clip):
        """
        Add video clip to the timeline based on another clip.
        """
        clip_copy = deepcopy(clip)
        video_ref = clip_copy.get('ref')

        self.store_video_asset(video_ref, clip_copy)
        self.spine.append(clip_copy)
        return clip_copy
    
    def get_clip_attributes(self, clip) -> Dict[str, Any]:
        """
        Get clip parameters.
        """
        # Get Davinci tags
        num_frames, fps = clip.get('duration')[0:-1].split('/')
        start_frames = clip.get('start')[0:-1].split('/')[0]
        offset_frames = clip.get('offset')[0:-1].split('/')[0]

        # Get custom tags
        ave_silent = clip.get('ave_silent', 'false').lower() == 'true'

        attributes = {
            'num_frames': int(num_frames),
            'fps': int(fps),
            'start_frames': int(start_frames),
            'offset_frames': int(offset_frames),
            'ave_silent': ave_silent,
        }

        return attributes
    
    def update_sequence_duration(self):
        """
        Iterate over clips and get the last frame of the sequence to update the sequence duration.
        """
        last_frame = 0
        fps = 0

        # Iterate over all video assets
        for ref in self.video_assets_refs:
            for clip in self.video_assets[ref]:

                # Get the last frame possible in the sequence
                clip_attributes = self.get_clip_attributes(clip)
                last_frame = max(last_frame, clip_attributes['offset_frames'] + clip_attributes['num_frames'])
                fps = clip_attributes['fps']
                
        # Update sequence duration
        self.sequence.attrib.update({
            'duration': f"{last_frame}/{fps}s",
        })
    
    def get_sequence_duration(self):
        """
        Get the sequence duration and its fps.
        """
        return self.sequence.attrib['duration'][0:-1].split('/')[0], self.sequence.attrib['duration'][0:-1].split('/')[1]

