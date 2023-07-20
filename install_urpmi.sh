# Обновляем информацию о доступных пакетах и устанавливаем Python 3.6 и пакеты для виртуального окружения
sudo urpmi rpmdev build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

if ! hash python3.8; then
    echo "Installing python3.8"
    wget https://www.python.org/ftp/python/3.8.14/Python-3.8.14.tar.xz
    tar -xf Python-3.8.14.tar.xz
    cd Python-3.8.14/
    sudo ./configure --enable-shared
    sudo make install
    cd ../
    rm -r Python-3.8.14/ Python-3.8.14.tar.xz
    echo "Launch script again"
else
    echo "Python3.8 installed"

python3.8 -m venv myenv
source myenv/bin/activate
python3.8 -m pip install --upgrade pip
python3.8 -m pip install -r requirements.txt
sudo chmod -R 777 myenv
export QT_PLUGIN_PATH=$PWD/myenv/lib64/python3.8/site-packages/PyQt5/Qt/plugins/
pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp:./service/videohosting_service/tmp" --add-data "version.txt:." --add-data "icon.png:." --add-data "icon.ico:." Application.py

mkdir BuxarVideoUploader

mv dist/ BuxarVideoUploader/
mv build/ BuxarVideoUploader/

tar -czf BuxarVideoUploader.tar.gz BuxarVideoUploader/
mv BuxarVideoUploader.tar.gz rpmbuild/SOURCES

cd rpmbuild

rpmbuild --define "_topdir $PWD" -bb SPECS/BuxarVideoUploader.spec

cd ../
sudo rm -r myenv/
fi