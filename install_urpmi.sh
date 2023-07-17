# Обновляем информацию о доступных пакетах и устанавливаем Python 3.6 и пакеты для виртуального окружения
sudo urpmi build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

if ! hash python3.8; then
    echo "Installing python3.8"
    wget https://www.python.org/ftp/python/3.8.14/Python-3.8.14.tar.xz
    tar -xf Python-3.8.14.tar.xz
    cd Python-3.8.14/
    sudo ./configure --enable-shared
    sudo make install
    cd ../
    rm -r Python-3.8.14/ Python-3.8.14.tar.xz
else
    echo "Python3.6 installed"

python3.8 -m venv myenv
source myenv/bin/activate
python3.8 -m pip install --upgrade pip
python3.8 -m pip install -r requirements.txt
export QT_PLUGIN_PATH=$PWD/venv/lib64/python3.8/site-packages/PyQt5/Qt/plugins/
pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp:./service/videohosting_service/tmp" --add-data "version.txt:." --add-data "icon.png:." Application.py

#tar -cvf BuxarVideoUploader.tar dist/ build/

sudo rm -r myenv/
