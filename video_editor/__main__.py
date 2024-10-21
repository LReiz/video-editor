"""
This script create the FCPXML file and adds default configuration to it.
"""
from lxml import etree
import argparse

from features.concatenate import Concatenate
from features.preprocess_videos import PreprocessVideos
from features.remove_silence import RemoveSilence
from entities.timeline import Timeline

def create_fcpxml():
    """
    Create the FCPXML tree element.
    """
    return etree.Element('fcpxml', version="1.11")


def add_default_configuration(file):
    """
    Add default configuration to the FCPXML file in the correct order.
    """
    file.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write(b'<!DOCTYPE fcpxml>\n')


def create_fcpxml_tree(fcpxml):
    """
    Create the FCPXML tree element.
    """
    return etree.ElementTree(fcpxml)


def main():
    print("Creating FCPXML file...")
    # Get arguments
    parser = argparse.ArgumentParser(description='Create FCPXML file.')
    parser.add_argument('videos_folder', type=str, help='Folder with the video files.')
    parser.add_argument('--skip-preprocess', '-sp', action='store_true', help='Skip the preprocessing step')

    # Parse the arguments
    args = parser.parse_args()

    # Create the FCPXML Element object
    fcpxml = create_fcpxml()

    # Create the Timeline object
    timeline = Timeline(fcpxml)

    # Preprocess videos
    preprocess = PreprocessVideos(args.videos_folder)
    if not args.skip_preprocess:
        preprocess.preprocess_all_videos_in_folder()

    # Concatenate files
    concatenate = Concatenate(timeline, preprocess.preprocessed_folder)
    concatenate.concatenate_video_files()

    # Remove silent parts
    remove_silence = RemoveSilence(timeline, preprocess.preprocessed_folder)
    remove_silence.remove_silence_from_videos()


    # Add subtitles


    # Insert fcpxml Element in the Tree object
    tree = create_fcpxml_tree(fcpxml)

    with open('my_project.fcpxml', 'wb') as file:
        # Write default configuration in file
        add_default_configuration(file)

        # Indent the tree to 4 spaces
        etree.indent(tree, space='    ')

        # Add FCPXML tree to the file
        tree.write(file, encoding='UTF-8', pretty_print=True)

    print("FCPXML file created successfully.")


if __name__ == "__main__":
    main()
