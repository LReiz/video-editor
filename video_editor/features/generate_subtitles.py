"""
This class is responsible for generating subtitles for the final video.
"""
import stable_whisper
import os
import re
import srt
from datetime import timedelta


class GenerateSubtitles():
    def __init__(
            self,
            videos_folder,
            preview_video,
            model='small',
            language=None,
            word_level=True,
            words_by_group=1,
            min_dur=0.01
        ):
        self.model = stable_whisper.load_model(model)
        self.output_folder = os.path.join(videos_folder, 'timeline')
        self.subtitles_file = os.path.join(self.output_folder, 'subtitles.srt')
        self.preview_video = preview_video
        self.word_level = word_level
        self.min_dur = min_dur
        self.transcribe_result = None
        self.words_by_group = words_by_group
        self.pause_between_sentences = 0.2  # in seconds
    
    def group_subtitles_by_number_of_words(self):
        """
        Group subtitles by number of words.
        """
        # If the number of words by group is 1, do nothing
        if self.words_by_group == 1:
            return

        # Read the original SRT content
        with open(self.subtitles_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        # Group subtitles by number of words
        subtitles = list(srt.parse(srt_content))
        new_subtitles = []
        current_subtitle = None
        current_subtitle_words = 0
        start_time = None
        end_time = None

        # Iterave over the subtitles
        for subtitle in subtitles:

            # If space between substitles is too long or if a new sentence is starting, create a new subtitle group
            if (
                end_time is not None
                and current_subtitle_words > 0
                and subtitle.start - end_time > timedelta(seconds=self.pause_between_sentences)
                ) \
                or (
                    current_subtitle is not None
                    and current_subtitle[-1] in ['.', '!', '?', '...']
                ):

                new_subtitles.append(srt.Subtitle(
                    index=len(new_subtitles) + 1,
                    start=start_time,
                    end=subtitle.end,
                    content=current_subtitle
                ))
                current_subtitle = None
                current_subtitle_words = 0

            # Get current subtitle data
            word = subtitle.content
            current_subtitle = ' '.join(filter(None, [current_subtitle, word]))
            current_subtitle_words += 1

            if current_subtitle_words == 1:
                start_time = subtitle.start
            end_time = subtitle.end

            # If the number of words by group is reached, add subtitle group to the list
            if current_subtitle_words == self.words_by_group:
                new_subtitles.append(srt.Subtitle(
                    index=len(new_subtitles) + 1,
                    start=start_time,
                    end=subtitle.end,
                    content=current_subtitle
                ))
                current_subtitle = None
                current_subtitle_words = 0
            
        
        # If there are still subtitles to be added
        if current_subtitle is not None:
            new_subtitles.append(srt.Subtitle(
                index=len(new_subtitles) + 1,
                start=start_time,
                end=subtitle.end,
                content=current_subtitle
            ))
        
        # Write the grouped subtitles back to a new SRT file
        with open(self.subtitles_file, 'w', encoding='utf-8') as f:
            f.write(srt.compose(new_subtitles))

    def remove_punctuation(self):
        """
        Remove punctuation from the text. Ugly punctuation to remove: . , : ; !
        """
        # Read the original SRT content
        with open(self.subtitles_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()

        # Parse the SRT content into subtitle objects
        subtitles = list(srt.parse(srt_content))

        # Iterave over subtitle groups
        for subtitle in subtitles:

            # Remove punctuation from each subtitle's text, except when it is followed by a digit
            """NOTE: This logic is needed to remove ugly punctuation and avoid removing puctuation from float numbers. E.g.: 2.5"""
            subtitle.content = re.sub(r"[.,:;!](?!\d)", "", subtitle.content)
            
            # When a punctuation is immediately followed by a character, remove the leading space
            """NOTE: This is needed to avoid breaking float numbers in the middle. E.g.: 2 .5"""
            subtitle.content = re.sub(r" \.(?=\S)| ,(?=\S)", lambda m: m.group().strip(), subtitle.content)

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

        # Group subtitles by number of words
        self.group_subtitles_by_number_of_words()

        # Remove punctuation from srt file
        self.remove_punctuation()

        print("Subtitles generated successfully!")
