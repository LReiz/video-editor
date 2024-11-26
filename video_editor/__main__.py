"""
This script create the FCPXML file and adds default configuration to it.
"""
from orchestrator import Orchestrator


def main():
    # Create the Orchestrator object
    orchestrator = Orchestrator()

    # Parse the arguments
    orchestrator.parse_arguments()

    # Preprocess videos
    orchestrator.preprocess_videos()

    # Determine input folder
    orchestrator.determine_input_folder()
    
    # Create the Timeline object
    orchestrator.create_timeline()

    # Concatenate files
    orchestrator.concatenate_files()

    # Remove silent parts
    orchestrator.remove_silence()

    # Remove Wordless clips
    orchestrator.remove_wordless_clips()

    # Apply J-Cut to the timeline
    orchestrator.jcut_timeline()

    # Add Subway Surfers to the video
    orchestrator.add_subway_surfers()

    # Add subtitles
    orchestrator.determine_subtitles_video()
    orchestrator.add_subtitles()

    # Create the FCPXML file
    orchestrator.generate_fcpxml_file()


if __name__ == "__main__":
    main()
