"""
This class remove wordless clips from video.
"""
import stable_whisper
import os
from copy import deepcopy

from utils.files import get_video_files


class RemoveWordless:
    """
    NOTE:
        - Using a model worst than 'small' can work very badly in some cases. The model may understand noises as words...
    """
    def __init__(self, timeline, videos_folder, model='small'):
        self.timeline = timeline
        self.videos_folder = videos_folder
        self.model = stable_whisper.load_model(model)
        self.transcriptions = []
    
    def convert_seconds_to_frames(self, seconds, fps):
        """
        Convert seconds to frames.
        """
        return int(seconds * fps)

    def segment_is_inside_clip(self, segment_start_frame, segment_end_frame, clip_start_frame, clip_end_frame):
        """
        Verify if the segment is inside the clip. In other words, if the clip has speech.
        """
        return (
            segment_start_frame >= clip_start_frame and segment_start_frame <= clip_end_frame
        ) or (
            segment_end_frame >= clip_start_frame and segment_end_frame <= clip_end_frame
        ) or (
            segment_start_frame < clip_start_frame and segment_end_frame > clip_end_frame
        )

    def remove_wordless_clips(self):
        """
        Remove wordless clips from the video timeline.

        NOTE:
            - This script works in a FIFO logic. It iterates through all clips in the timeline and just
              add the clips that are not wordless to the end of the timeline. Then, for each iteration, the
              clip analyzed clip is removed from the timeline.
        """
        # Get all video files in the folder
        video_files = get_video_files(self.videos_folder)

        # Transcribe each video in the folder
        for video in sorted(video_files):
            if not os.path.isfile(video):
                continue

            transcription = self.model.transcribe(video)
            self.transcriptions.append(transcription)
        
        # Offset to append video clips to the timeline
        current_offset = 0

        # Make copy of video assets references
        video_assets_copy = deepcopy(self.timeline.video_assets)

        # Iterate through all videos
        for ref_idx, ref in enumerate(self.timeline.video_assets_refs):
            transcription = self.transcriptions[ref_idx]
            segment_index = 0
            segment = transcription[segment_index]

            # Iterate through all clips cutted from video
            for _ in video_assets_copy[ref]:
                # Get clip attributes
                asset_clip = self.timeline.get_stored_video_asset(ref, 0)
                clip_attrib = self.timeline.get_clip_attributes(asset_clip)
                fps = clip_attrib['fps']
                ave_silent = clip_attrib['ave_silent']
                clip_start_frame = clip_attrib['start_frames']
                clip_end_frame = clip_attrib['start_frames'] + clip_attrib['num_frames']
                
                # Get segments start and end frames
                segment_start_frame = self.convert_seconds_to_frames(segment.start, fps)
                segment_end_frame = self.convert_seconds_to_frames(segment.end, fps)

                # Move segment pointer to next segment closer to current clip
                while segment_end_frame < clip_start_frame and segment_index < len(transcription):
                    segment = transcription[segment_index]
                    segment_index += 1

                    # Get transcription segment start and end frame
                    segment_start_frame = self.convert_seconds_to_frames(segment.start, fps)
                    segment_end_frame = self.convert_seconds_to_frames(segment.end, fps)

                # Verify if the clip is inside transcription segment, which means it has speech
                if self.segment_is_inside_clip(
                    segment_start_frame,
                    segment_end_frame,
                    clip_start_frame,
                    clip_end_frame
                # Verify if the clip is not silent
                ) and not ave_silent:
                    added_clip = self.timeline.add_clip_to_timeline_based_on_clip(asset_clip)

                    # Update clip offset
                    added_clip.attrib.update({'offset': f"{current_offset}/{fps}s"})
                    current_offset += clip_attrib['num_frames']

                # Remove base clip from timeline
                self.timeline.remove_stored_video_asset(ref, 0)

        # Update timeline duration
        self.timeline.update_sequence_duration()
            