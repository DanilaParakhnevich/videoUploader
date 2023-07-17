version=$(python3.6 -V 2>&1 | grep -Po '(?<=Python )(.+)')


if ! hash python3.6; then
    echo "Installing python3.6"
    sudo apt-get update
    sudo apt-get install -y python3.6 python3.6-venv
else
    echo "Python3.6 installed"

# Создаем виртуальное окружение и активируем его
python3.6 -m venv myenv
source myenv/bin/activate

# Выполняем необходимые команды внутри виртуального окружения с использованием Python 3.6
pip install -r requirements.txt
pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp:./service/videohosting_service/tmp" --add-data "version.txt:." --add-data "icon.png:." --icon "icon.png" Application.py

mkdir debpack/usr/
mkdir debpack/usr/share/
mkdir debpack/usr/share/BuxarVideoUploader

mv build debpack/usr/share/BuxarVideoUploader
mv dist debpack/usr/share/BuxarVideoUploader

cd debpack

tar czf data.tar.gz usr/share/
tar czf  control.tar.gz control postinst postrm
echo 2.0 > debian-binary
ar -r ../BuxarVideoUploader.deb  debian-binary control.tar.gz data.tar.gz

rm -r usr
rm data.tar.gz
rm control.tar.gz

cd ../
rm -r myenv/
rm Application.spec

fi
