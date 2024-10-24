# Video Editor

Automatic video editor to create the most <s>addicting</s> professional videos in the market. This project is based on XML video editing, a format supported by the most recognized video editing software. The idea is to write an XML file that contains all video editing instructions, which the software will use to create a timeline with the edited video.

This program will primarily focus on the creation of `.fcpxml` (Final Cut Pro XML) files, which are supported by [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) and [Final Cut Pro](https://www.apple.com/br/final-cut-pro/), mainly because DaVinci Resolve's free version is one of the best video editing software options available. These instructions will focus on Windows users, although they can be adapted for other operating systems as well.

## Set Up Environment

For Windows users, it's **recommended** the installation of the following:
1. [Chocolatey](https://chocolatey.org/install#individual) (recommended to install other packages)

It's necessary that you install:
1. [Python 3.12](https://www.python.org/downloads/release/python-3120/)
1. [Windows Pyenv](https://github.com/pyenv-win/pyenv-win?tab=readme-ov-file#quick-start)
    - I had to execute this line in Windows Powershell before installing pyenv-win `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
1. git
1. make (can be installed with `choco install make`)
1. grep (can be installed with `choco install grep`)


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
.venv\Scripts\activate
```

Install requirements:

```bash
make install
```

## How to Use

to do
