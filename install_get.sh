# Обновляем информацию о пакетах и устанавливаем необходимые пакеты
sudo apt-get update
sudo apt-get install -y python3.6 python3.6-venv

# Создаем виртуальное окружение и активируем его
python3.6 -m venv myenv
source myenv/bin/activate

# Выполняем необходимые команды внутри виртуального окружения с использованием Python 3.6
pip install -r requirements.txt
pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp:./service/videohosting_service/tmp" --add-data "version.txt:." Application.py
mkdir debpack
mkdir debpack/opt
mkdir debpack/opt/BuxarVideoUploader

sudo mv build debpack/opt/BuxarVideoUploader
sudo mv dist debpack/opt/BuxarVideoUploader

echo "Package: BuxarVideoUploader\nVersion:1.0.0\nIcon: /home/dendil/Documents/Projects/Own/BuxarVideoUploader/icon.png\nArchitecture: all\nDescription:Application for video downloading/uploading" > debpack/control
cd debpack

tar czf data.tar.gz opt
tar czf  control.tar.gz  control
echo 2.0 > debian-binary
ar -r ../BuxarVideoUploader.deb  debian-binary control.tar.gz data.tar.gz

cd ../
sudo rm -r myenv/
sudo rm -r debpack
sudo rm Application.spec

#sudo touch /usr/share/applications/BuxarVideoUploader.desktop
#
#echo "[Desktop Entry]
#Version=1.0
#Name=BuxarVideoUploader
#Comment=BuxarVideoUploader
#Exec=/opt/BuxarVideoUploader/dist/Application/Application %U
#Icon=/home/dendil/Documents/Projects/Own/BuxarVideoUploader/icon.png
#Terminal=false
#StartupWMClass=BuxarVideoUploader
#Type=Application
#Categories=VideoUploader>" > /usr/share/applications/BuxarVideoUploader.desktop
#
#sudo cp /usr/share/applications/BuxarVideoUploader.desktop /home/dendil/Desktop/
