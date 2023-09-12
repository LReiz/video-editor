# Create one word subtitles
stable-ts --model small cortado.mov -o subtitles.srt --language Portuguese --word_level true --segment_level false --overwrite -y
