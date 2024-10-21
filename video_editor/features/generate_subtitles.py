"""
This class is responsible for generating subtitles for the final video.
"""
import stable_whisper
import os


class GenerateSubtitles():
    def __init__(self, videos_folder, preview_video, model='small', language=None):
        self.model = stable_whisper.load_model(model)
        self.output_folder = os.path.join(videos_folder, 'timeline')
        self.subtitles_file = os.path.join(self.output_folder, 'subtitles.srt')
        self.preview_video = preview_video


    def generate_subtitles(self):
        """
        Add subtitles to the final video.
        """
        result = self.model.transcribe(self.preview_video)
        result.to_srt_vtt(self.subtitles_file, word_level=True, segment_level=False)
        print("Subtitles generated successfully!")
