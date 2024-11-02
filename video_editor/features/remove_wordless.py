"""
This class is used to remove all wordless clips from video timeline.
"""
import stable_whisper
import os


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
        self.cumulative_duration = 0
        self.right_margin = 0.3
        self.left_margin = 0.3

    def convert_seconds_to_frames(self, seconds, fps):
        """
        Convert seconds to frames.
        """
        return int(seconds * fps)

    def remove_wordless_clips(self):
        """
        Remove wordless clips from the video timeline.
        """
        video_files = [
            os.path.join(os.path.abspath(self.videos_folder), f) for f in sorted(os.listdir(self.videos_folder))
        ]

        for video in sorted(video_files):
            if not os.path.isfile(video):
                continue

            transcription = self.model.transcribe(video)
            self.transcriptions.append(transcription)
        
        for i, ref in enumerate(self.timeline.video_assets_refs):
            base_asset_clip = self.timeline.get_stored_video_asset(ref, 0)
            base_clip_attrib = self.timeline.get_clip_attributes(base_asset_clip)
            fps = base_clip_attrib['fps']
            num_frames = base_clip_attrib['num_frames']

            transcription = self.transcriptions[i]
            start_frame = 0
            end_frame = 0

            for segment in transcription:
                print(segment)
                start_frame = max(
                    end_frame,
                    self.convert_seconds_to_frames(segment.start, fps) - self.convert_seconds_to_frames(self.left_margin, fps)
                )
                end_frame = min(
                    num_frames,
                    self.convert_seconds_to_frames(segment.end, fps) + self.convert_seconds_to_frames(self.right_margin, fps)
                )
                duration_frames = end_frame - start_frame
                

                self.timeline.add_clip_to_timeline(
                    video_ref=base_asset_clip.get('ref'),
                    num_frames=duration_frames,
                    start=start_frame,
                    offset=self.cumulative_duration,
                    fps=fps,
                    filename=base_asset_clip.get('name')
                )

                self.cumulative_duration += duration_frames
            
            self.timeline.remove_stored_video_asset(ref, 0)
        
        # Update sequence duration
        self.timeline.update_sequence_duration()
