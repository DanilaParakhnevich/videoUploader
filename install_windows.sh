#!/bin/bash
py -m venv myenv
.\myenv\Scripts\activate.bat
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
pyinstaller --add-data "service/locale/*.json;./service/locale/" --add-data "gui/widgets/button_icons/*.gif;./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp;./service/videohosting_service/tmp" --add-data "version.txt;." --add-data "icon.png;." -w Application.py
mkdir BuxarVideoUploader
move dist BuxarVideoUploader
move build BuxarVideoUploader
del myenv