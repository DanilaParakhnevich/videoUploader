#!/bin/bash
py -m venv myenv
.\myenv\Scripts\activate.bat
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
pyinstaller --uac-admin --add-data "service/locale/*.json;./service/locale/" --add-data "gui/widgets/button_icons/*.gif;./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp;./service/videohosting_service/tmp" --add-data "version.txt;." --add-data "icon.png;." --add-data "icon.ico;." -w Application.py
mkdir BuxarVideoUploader
rm -r BuxarVideoUploader/dist
rm -r BuxarVideoUploader/build
mv dist BuxarVideoUploader
mv build BuxarVideoUploader
rm -r myenv