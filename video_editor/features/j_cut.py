"""
This class is responsible for creating a J-Cut transition between clips in the video timeline.

Note:
    - J-Cut is famous transition between clips. It is a video editing technique where the audio from the next
        clip starts playing before the video transition occurs. It helps to remove silence in-between clips
        and any room for distraction. Since we're making the most addictive videos on the internet, we're going
        to overdo this technique.
"""
from copy import deepcopy

class JCut:
    def __init__(self, timeline):
        self.last_frame_lane_0 = 0
        self.last_frame_lane_1 = 0
        self.min_duration = 1   # Min clip duration to do a J-Cut (in seconds)
        self.jcut_duration = 0.5 # Duration of the J-Cut (in seconds). In other words, for how long clip will overlap
        self.small_clips_duration = 0
        self.fps = 0
        self.timeline = timeline
    
    def cut_clip_in_half(self, clip):
        """
        Cut the clip in half.
        """
        # Duplicate clips
        first_half_clip = deepcopy(clip)
        second_half_clip = deepcopy(clip)

        # Get the duration of the clip
        attributes = self.timeline.get_clip_attributes(clip)
        num_frames = attributes['num_frames']
        fps = attributes['fps']
        start_frames = attributes['start_frames']

        # Cut the clip in half
        first_half_duration = num_frames // 2
        second_half_duration = num_frames - first_half_duration

        # Update clips duration
        first_half_clip.attrib.update({'duration': f"{first_half_duration}/{fps}s"})
        second_half_clip.attrib.update({'duration': f"{second_half_duration}/{fps}s"})

        # Update first half offset
        first_half_clip.attrib.update({'offset': f"{self.last_frame_lane_0}/{fps}s"})

        # Update second half start and offset
        second_half_clip.attrib.update({'start': f"{start_frames + first_half_duration}/{fps}s"})
        second_half_clip.attrib.update({'offset': f"{self.last_frame_lane_0 + first_half_duration}/{fps}s"})

        return first_half_clip, second_half_clip
    
    def jcut_clip(self, base_clip, base_clip_attributes):
        """
        Apply J-Cut to a video clip.
        """
        # Cut the clip in half
        first_half_clip, second_half_clip = self.cut_clip_in_half(base_clip)

        # Change second half lane to Video 2 track
        second_half_clip.attrib.update({'lane': '1'})

        # Add clips to timeline
        self.timeline.add_clip_to_timeline_based_on_clip(first_half_clip)
        self.timeline.add_clip_to_timeline_based_on_clip(second_half_clip)

        # Get attributes of first half clip
        second_half_clip_attributes = self.timeline.get_clip_attributes(second_half_clip)

        # Update last_frame_lane_0 and last_frame_lane_1
        self.last_frame_lane_1 = second_half_clip_attributes['offset_frames'] + second_half_clip_attributes['num_frames']
        self.last_frame_lane_0 = self.last_frame_lane_1 - int(base_clip_attributes['fps'] * self.jcut_duration)
    
    def append_small_clip(self, base_clip, base_clip_attributes):
        """
        Append small clip to Video 1 track.
        """
        # Shift clip in Video 1 track to possible frame
        clip = self.timeline.add_clip_to_timeline_based_on_clip(base_clip)
        clip.attrib.update({'offset': f"{self.last_frame_lane_0}/{base_clip_attributes['fps']}s"})

        # Update Last Frame in Video 1 track
        self.last_frame_lane_0 += base_clip_attributes['num_frames']

    def jcut_timeline(self):
        """
        Apply J-Cut to all clips in the timeline that are longer than the min_duration.

        This method applies a FIFO logic:
            - It iterates over all clips in the timeline and creates a copy of it applying the J-Cut technique.
              The original clip is removed from the timeline and the new one is added to the end of the list.
        """
        # For elem in video assets (all already cutted clips)
        """
        NOTE:
            - Iterating over a copy of the videos assets list is necessary, because as you add and remove clips,
              list size will change affecting the for loop.
        """ 
        video_assets_refs = deepcopy(self.timeline.video_assets_refs)
        video_assets = deepcopy(self.timeline.video_assets)

        # For each video reference
        for ref in video_assets_refs:

            # For each clip for a video reference
            for _ in range(len(video_assets[ref])):

                # Get the Asset Clip
                base_clip = self.timeline.get_stored_video_asset(ref, 0)

                # Get base clip attributes
                base_clip_attributes = self.timeline.get_clip_attributes(base_clip)
                num_frames = base_clip_attributes['num_frames']
                fps = base_clip_attributes['fps']

                # If clip has enough duration, apply J-Cut
                if num_frames/fps >= self.min_duration:
                    self.jcut_clip(base_clip, base_clip_attributes)

                # If clip don't have enough duration, don't apply J-Cut, just add it to Video 1 track
                else:
                    self.append_small_clip(base_clip, base_clip_attributes)
                
                # Remove the base clip from timeline
                self.timeline.remove_stored_video_asset(ref, 0)

        # Update sequence duration
        self.timeline.update_sequence_duration()
