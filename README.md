# Video Editor

Automatic video editor to create the most <s>addictive</s> professional videos in the market. This project is based on XML video editing, a format supported by the most recognized video editing software. The idea is to write an XML file that contains all video editing instructions, which the software will use to create a timeline with the edited video.

This program will primarily focus on the creation of `.fcpxml` (Final Cut Pro XML) files, which are supported by [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) and [Final Cut Pro](https://www.apple.com/br/final-cut-pro/), mainly because DaVinci Resolve's free version is one of the best video editing software options available. These instructions will focus on Windows users, although they can be adapted for other operating systems as well.

## Set Up Environment

For Windows users, it's **recommended** the installation of the following:
1. [Chocolatey](https://chocolatey.org/install#individual) (recommended to install other packages)

For MacOS users, it's **recommended** the installation of the following:
1. [Homebrew](https://brew.sh/)

It's necessary that you install:
1. [Python 3.12](https://www.python.org/downloads/release/python-3120/)
1. [Windows Pyenv](https://github.com/pyenv-win/pyenv-win?tab=readme-ov-file#quick-start)
    - I had to execute this line in Windows Powershell before installing pyenv-win `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
1. git
1. make (can be installed on Windows with `choco install make`)
1. grep (can be installed on Windows with `choco install grep`)
1. ffmpeg (can be installed on Windows with `choco install ffmpeg` or on MacOS with `brew install ffmpeg`)


Clone the repository:

```bash
git clone git@github.com:LReiz/video-editor.git
cd video-editor
```

Set python version to the correct one:

```bash
pyenv install 3.12
pyenv local 3.12
```

Create a python virtual environment and activate it:

```bash
python -m venv .venv
```

Activate venv

```bash
# for Windows
.venv\Scripts\activate

# for MacOS
source .venv/bin/activate
```

Install requirements:

```bash
# for Windows
make install-win

# for MacOS
make install-mac
```

## How to Use

### Automatically Edit Videos

After setting up your environment, you should create a folder anywhere in your computer with all the videos you want to edit. Keep in mind that the alphabetical order of the videos will determine the concatenation order of these videos in the final Timeline.

Finally, just run the following command on your terminal and let the magic happen:

```bash
python video_editor <path-to-your-videos-folder>
```

If all went right, you should see a folder structure like the following inside your videos folder:

    videos_folder/
    ├── <your_raw_video_files>
    └── preprocessed/
        ├── <preprocessed_video_files>
        ├── timeline/
        │   └── timeline.fcpxml
        └── remove_silence/
            └── <loud_maps_files>.json

Now, open Davinci Resolve and create a new project. Then go to `File > Import > Timeline...`, import the newly created `timeline.fcpxml` file and watch the magic happen!

### Add Subtitles

To add subtitles, you should render the video in Davinci Resolve first. Then, use the following command to create subtitles for the video.

```bash
python video_editor -js <path-to-your-video>
```

You should then see a folder called `timeline` with the `subtitles.srt` file in the same folder as your video. Simply open the Davinci Resolve project and import the subtitles file with `File > Import > Subtitle...`. Then, right-click the imported file and `Insert Selected Subtitles to Timeline Using Timecode`.
