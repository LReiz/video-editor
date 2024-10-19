# Create list of videos to concatenate
(for %%i in (*.mp4) do @if %%i neq concatenado.mp4 (@echo file '%%i')) > videolist.txt

# Concatenate videos
echo y | ffmpeg -f concat -safe 0 -i videolist.txt -c copy concatenado.mp4

# Remove list
del videolist.txt
