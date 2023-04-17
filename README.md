<div align="center">

[![LJ-DL-IMG](https://raw.githubusercontent.com/mezhgano/lj-dl-img/main/assets/github_banner.svg)](#readme)

</div>

**lj-dl-img** is a parser for downloading image albums from [Livejournal.com](https://www.livejournal.com/).
With it you can download all albums of user with just few clicks.

* [INSTALLATION](#installation)
    * [Windows](#windows)
    * [Linux](#linux)
    * [macOS](#macos)
* [USAGE](#usage)
    * [Options](#options)
    * [URL](#url)
* [NOTES](#notes)
* [TODO](#todo)

# INSTALLATION

[![Windows](https://img.shields.io/badge/-Windows_x64-blue.svg?style=for-the-badge&logo=windows)](https://github.com/mezhgano/lj-dl-img)
[![Unix](https://img.shields.io/badge/-Linux/BSD-red.svg?style=for-the-badge&logo=linux)](https://github.com/mezhgano/lj-dl-img)

File|Description
:---|:---
[lj-dl-img](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp)|For **Linux/BSD**
[lj-dl-img.exe](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe)|For **Windows**

## Windows
Download binary, add it to System Path and execute following in terminal:
```
lj-dl-img https://dimarcello.livejournal.com/photo/album/1683/
```

You can read more about how to place anything to System Path on Windows here:
* [Add EXE to PATH in Windows 10.md](https://gist.github.com/ScribbleGhost/752ec213b57eef5f232053e04f9d0d54)
* [How to Edit Your System PATH for Easy Command Line Access in Windows](https://www.howtogeek.com/118594/how-to-edit-your-system-path-for-easy-command-line-access/)

If you don't want to setting up System Path just call it directly executing following in terminal:
```
.\path\to\downloads\folder\lj-dl-img.exe https://dimarcello.livejournal.com/photo/album/1683/
```

## Linux
Download binary, copy it to folder in System Path, mark the file as executable. To do so execute following in terminal:
```
cp lj-dl-img //usr/bin/
chmod u+x //usr/bin/lj-dl-img
lj-dl-img https://dimarcello.livejournal.com/photo/album/1683/
```

## macOS
For now only Windows and Linux binaries are avaliable, i don't have Mac to compile it.

You can clone this repository and run `lj_dl_img.py` (you will need Python installation, i'm using 3.10.10):
```
git clone https://github.com/mezhgano/lj-dl-img.git
python -m pip install -r requirements.txt
python lj_dl_img.py https://dimarcello.livejournal.com/photo/album/1683/
```


# USAGE

```
lj-dl-img [-h] [-v] [-d] URL
```

## Options:
-h, --help          Show this help message and exit.

-v, --version       Show script version and exit.

-d , --directory    Path where images should be downloaded.
                    Note that script will create a subfolder for each downloaded album.
                    Default: current working directory.

## URL:
 URL                URL of Livejournal user or certain album to download. For example, specify:
                    https://dimarcello.livejournal.com - to download all avaliable albums.
                    https://dimarcello.livejournal.com/photo/album/1337 - to download just one certain album.

# NOTES
* For now lj-dl-img will download only public avaliable images, all private images will be ignored.
I'm planning to add a feature in future releases to use a cookies to download all images, regardless of private settings.


# TODO

- [ ] Add option to pass cookies (for downloading private images)
- [ ] Compile binary for macOS (i don't have mac, so any help apperticed)
- [ ] Add option to download video albums
