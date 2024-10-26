"""
This class is responsible for generating subtitles for the final video.
"""
import stable_whisper
import os


class GenerateSubtitles():
    def __init__(
            self,
            videos_folder,
            preview_video,
            model='small',
            language=None,
            word_level=True,
            min_dur=0.01
        ):
        self.model = stable_whisper.load_model(model)
        self.output_folder = os.path.join(videos_folder, 'timeline')
        self.subtitles_file = os.path.join(self.output_folder, 'subtitles.srt')
        self.preview_video = preview_video
        self.word_level = word_level
        self.min_dur = min_dur


    def generate_subtitles(self):
        """
        Add subtitles to the final video.
        """
        # Create the output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

        # Generate subtitles
        result = self.model.transcribe(self.preview_video)
        result.to_srt_vtt(
            self.subtitles_file,
            word_level=self.word_level,
            segment_level=not self.word_level,
            min_dur=self.min_dur    
        )
        print("Subtitles generated successfully!")
