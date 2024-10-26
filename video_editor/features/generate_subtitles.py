"""
This class is responsible for generating subtitles for the final video.
"""
import stable_whisper
import os
import re
import srt


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
        self.transcribe_result = None

    def remove_punctuation(self):
        """
        Remove punctuation from the text. Ugly punctuation to remove: . , : ; !
        """
        # Read the original SRT content
        with open(self.subtitles_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()

        # Parse the SRT content into subtitle objects
        subtitles = list(srt.parse(srt_content))

        # Remove punctuation from each subtitle's text
        for subtitle in subtitles:
            subtitle.content = re.sub(r"[.,:;!]", "", subtitle.content)

        # Write the cleaned subtitles back to a new SRT file
        with open(self.subtitles_file, 'w', encoding='utf-8') as f:
            f.write(srt.compose(subtitles))

    def generate_subtitles(self):
        """
        Add subtitles to the final video.
        """
        # Create the output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

        # Generate subtitles
        self.transcribe_result = self.model.transcribe(self.preview_video)  

        # Save subtitles
        self.transcribe_result.to_srt_vtt(
            self.subtitles_file,
            word_level=self.word_level,
            segment_level=not self.word_level,
            min_dur=self.min_dur    
        )

        # Remove punctuation from srt file
        self.remove_punctuation()

        print("Subtitles generated successfully!")
