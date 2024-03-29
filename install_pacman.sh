version=$(python3.8 -V 2>&1 | grep -Po '(?<=Python )(.+)')

yes | sudo pacman -S dpkg
yes | sudo pacman -S xcb-util
yes | sudo pacman -S xcb-util-keysyms
yes | sudo pacman -S xcb-util-cursor
yes | sudo pacman -S xcb-util-wm

if ! hash python3.8; then
    echo "Installing python3.8"
    wget https://www.python.org/ftp/python/3.8.14/Python-3.8.14.tar.xz
    tar -xf Python-3.8.14.tar.xz
    cd Python-3.8.14/
    sudo ./configure --enable-shared
    make
    sudo make altinstall
    sudo cp --no-clobber ./libpython3.8.so* /lib64/
    sudo chmod 755 /lib64/libpython3.8.so*
    cd ../
    sudo rm -r Python-3.8.14/ Python-3.8.14.tar.xz
    echo "Launch script again"
else
    echo "Python3.8 installed"
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/

# Создаем виртуальное окружение и активируем его
python3.8 -m venv myenv
source myenv/bin/activate

# Выполняем необходимые команды внутри виртуального окружения с использованием Python 3.6
python3.8 -m pip install --upgrade pip
python3.8 -m pip install -r requirements.txt
export QT_PLUGIN_PATH=$PWD/myenv/lib64/python3.8/site-packages/PyQt5/Qt/plugins/
pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp:./service/videohosting_service/tmp" --add-data "version.txt:." --add-data "icon.png:." --add-data "icon.ico:." --icon "icon.ico" Application.py

mv build debpack/usr/share/BuxarVideoUploader
mv dist debpack/usr/share/BuxarVideoUploader

rm -r myenv

fi
