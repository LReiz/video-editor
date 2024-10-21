"""
This class preprocess the videos to standardize the video files to be used in the Timeline.
"""
import ffmpeg
import os


class PreprocessVideos:
    def __init__(self, videos_folder):
        self.videos_folder = videos_folder
        self.preprocessed_folder = os.path.join(self.videos_folder, 'preprocessed')


    def get_average_fps(self, video_path):
        """Extract and calculate the average frame rate (FPS) of a video."""
        try:
            # Probe the video to get stream info
            probe = ffmpeg.probe(video_path, select_streams='v:0')
            fps_info = probe['streams'][0]['avg_frame_rate']

            # Handle fractional FPS (e.g., '30000/1001')
            num, denom = map(int, fps_info.split('/'))
            avg_fps = num / denom
            return avg_fps
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error: {e.stderr}")


    def convert_to_cfr(self, video_path, output_path, target_fps):
        """Convert a VFR video to CFR using the specified target FPS."""
        try:
            """
            Note:
                Is better to make this preprocessing in async mode to make it faster. We must use run_async() instead of run()
                and create a while loop to check the end of each process execution.
            """
            (
                ffmpeg
                .input(video_path)
                .output(output_path, fps_mode='cfr', r=target_fps)  # Convert to CFR
                .run(overwrite_output=True)
            )
            print(f"Successfully converted to {target_fps} FPS CFR. Video path: {video_path}")
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error: {e.stderr}")

    def preprocess_video(self, video_path, output_path, lowest_avg_fps):
        # Round to the closest common frame rate (e.g., 30, 60, 24)
        target_fps = round(lowest_avg_fps / 10) * 10  # Round to nearest multiple of 10
        print(f"Converting to {target_fps} FPS CFR...")

        self.convert_to_cfr(video_path, output_path, target_fps)
    

    def preprocess_all_videos_in_folder(self):
        # Create output folder for preprocessed videos
        os.makedirs(os.path.join(self.videos_folder, 'preprocessed'), exist_ok=True)
        self.preprocessed_folder = os.path.join(self.videos_folder, 'preprocessed')

        # Get lowest avg_fps from all videos
        lowest_avg_fps = float('inf')
        for video_file in os.listdir(self.videos_folder):
            # Skip non-video files
            if not os.path.isfile(os.path.join(self.videos_folder, video_file)):
                continue

            # Get average FPS of video
            video_path = os.path.join(self.videos_folder, video_file)
            lowest_avg_fps = min(lowest_avg_fps, self.get_average_fps(video_path))

        print(f"Lowest Average FPS: {lowest_avg_fps}\nEncoding all videos to {lowest_avg_fps} FPS CFR...")

        # Preprocess all videos in the input folder
        for video_file in os.listdir(self.videos_folder):
            # Skip non-video files
            if not os.path.isfile(os.path.join(self.videos_folder, video_file)):
                continue

            # Preprocess video
            video_path = os.path.join(self.videos_folder, video_file)
            output_path = os.path.join(self.videos_folder, 'preprocessed', f"preprocessed_{video_file}")
            self.preprocess_video(video_path, output_path, lowest_avg_fps)
