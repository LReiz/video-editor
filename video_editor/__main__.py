"""
This script create the FCPXML file and adds default configuration to it.
"""
import argparse

from features.concatenate import Concatenate
from features.generate_subtitles import GenerateSubtitles
from features.preprocess_videos import PreprocessVideos
from features.remove_silence import RemoveSilence

from entities.timeline import Timeline


def main():
    print("Creating FCPXML file...")
    # Get arguments
    parser = argparse.ArgumentParser(description='Create FCPXML file.')
    parser.add_argument('videos_folder', type=str, help='Folder with the video files.')
    parser.add_argument('--skip-preprocess', '-sp', action='store_true', help='Skip the preprocessing step')

    # Parse the arguments
    args = parser.parse_args()

    # Preprocess videos
    preprocess = PreprocessVideos(args.videos_folder)
    if not args.skip_preprocess:
        preprocess.preprocess_all_videos_in_folder()

    # Create the Timeline object
    timeline = Timeline(preprocess.preprocessed_folder)

    # Concatenate files
    concatenate = Concatenate(timeline, preprocess.preprocessed_folder)
    concatenate.concatenate_video_files()

    # Remove silent parts
    remove_silence = RemoveSilence(timeline, preprocess.preprocessed_folder)
    remove_silence.remove_silence_from_videos()

    # Add subtitles
    remove_silence.generate_final_preview_video()
    generate_subtitles = GenerateSubtitles(preprocess.preprocessed_folder, remove_silence.preview_final_video)
    generate_subtitles.generate_subtitles()

    # Create the FCPXML file
    timeline.generate_fcpxml_file()


if __name__ == "__main__":
    main()
