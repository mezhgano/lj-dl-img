<div align="center">

[![LJ-DL-IMG](https://raw.githubusercontent.com/mezhgano/lj-dl-img/main/assets/github_banner.svg)](#readme)

</div>

**lj-dl-img** is a parser for downloading image albums from [Livejournal.com](https://www.livejournal.com/).<br>
Download user albums in just few clicks.

* [INSTALLATION](#installation)
    * [Windows](#windows)
    * [Linux](#linux)
    * [macOS](#macos)
* [USAGE](#usage)
    * [Options](#options)
    * [URL](#url)
* [NOTES](#notes)
* [TODO](#todo)
* [DONATION](#donation)

# INSTALLATION

[![Windows](https://img.shields.io/badge/-Windows_x64-blue.svg?style=for-the-badge&logo=windows)](https://github.com/mezhgano/lj-dl-img)
[![Unix](https://img.shields.io/badge/-Linux/BSD-red.svg?style=for-the-badge&logo=linux)](https://github.com/mezhgano/lj-dl-img)
[![All versions](https://img.shields.io/badge/-All_Versions-lightgrey.svg?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp/releases)

File|Description
:---|:---
[lj-dl-img.exe](https://github.com/mezhgano/lj-dl-img/releases/latest/download/lj-dl-img.exe)|For **Windows**
[lj-dl-img](https://github.com/mezhgano/lj-dl-img/releases/latest/download/lj-dl-img_linux)|For **Linux/BSD**

## Windows
Download binary, add it to System Path and execute following in terminal:
```
lj-dl-img https://username.livejournal.com
```

You can read more about how to place anything to System Path on Windows here:
* [Add EXE to PATH in Windows 10.md](https://gist.github.com/ScribbleGhost/752ec213b57eef5f232053e04f9d0d54)
* [How to Edit Your System PATH for Easy Command Line Access in Windows](https://www.howtogeek.com/118594/how-to-edit-your-system-path-for-easy-command-line-access/)

If you don't want to setting up System Path just call it directly:
```
.\path\to\downloads\folder\lj-dl-img.exe https://username.livejournal.com
```

## Linux
Download binary, copy it to folder in System Path, mark the file as executable.<br> To do so execute following in terminal:
```
sudo mv lj-dl-img_linux /usr/local/bin/lj-dl-img
chmod u+x /usr/local/bin/lj-dl-img
lj-dl-img https://username.livejournal.com
```

## macOS
For now only Windows and Linux binaries are avaliable, i don't have Mac to compile it.

You can clone this repository and run `lj_dl_img.py`<br>
(This requires Python installed, i'm using 3.10.10):
```
git clone https://github.com/mezhgano/lj-dl-img.git
python -m pip install -r requirements.txt
python lj_dl_img.py https://username.livejournal.com
```


# USAGE

```
lj-dl-img [-h] [-v] [-d] URL
```

## Options:
```
-h, --help          Show this help message and exit.

-v, --version       Show script version and exit.

-d , --directory    Path where images should be downloaded.
                    Note that script will create a subfolder for each downloaded album.
                    Default: current working directory.

 URL                URL of Livejournal user or certain album to download. For example, specify:
                    https://username.livejournal.com - to download all avaliable albums.
                    https://username.livejournal.com/photo/album/1337 - to download just one certain album.
```

# NOTES
* For now only downloading public images available, all private images will be ignored.<br>
I'm planning to add a feature in future releases to use a cookies to download all images from your user, regardless of private settings.


# TODO

- [ ] Write additional README in Russian
- [ ] Add option to pass cookies (for downloading private images)
- [ ] Compile binary for macOS (i don't have mac, so any help apperticed)
- [ ] Add option to download video albums

# DONATION

If this parser saves your time and make life a little bit easier, consider donation:<br>
[https://yoomoney.ru/to/410011617547984](https://yoomoney.ru/to/410011617547984)
