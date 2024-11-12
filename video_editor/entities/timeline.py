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
        self.tree = etree.ElementTree(self.fcpxml)
        self.spine = None
        self.sequence = None
        self.video_assets_refs: List[str] = []
        self.video_assets: Dict[str, Any] = {}

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
        self.update_sequence_duration()

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
    
    def add_clip_to_timeline(self, video_ref, num_frames, start, offset, fps, filename, lane=0, custom_attrib={}) -> etree.Element:
        """
        Add video clip to the timeline.
        """
        # Create Asset Clip element
        asset_clip = etree.SubElement(self.spine, 'asset-clip')
        asset_clip_attributes = {
            'ref': video_ref,
            'duration': f"{num_frames}/{fps}s",
            'tcFormat': 'NDF',
            'enabled': '1',
            'offset':  f"{offset}/{fps}s",
            'start': f"{start}/{fps}s",
            'format': 'r0',
            'name': filename,
            'lane': f"{lane}",
            **custom_attrib,
        }
        asset_clip.attrib.update(asset_clip_attributes)

        self.store_video_asset(video_ref, asset_clip)

        # Create Adjust Transform element
        adjust_transform = etree.SubElement(asset_clip, 'adjust-transform')
        adjust_transform.attrib.update({
            'position': '0 0',
            'anchor': '0 0',
            'scale': '1 1',
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
