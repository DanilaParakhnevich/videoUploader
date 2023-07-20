version=$(python3.8 -V 2>&1 | grep -Po '(?<=Python )(.+)')

if ! hash python3.8; then
    echo "Installing python3.8"
    sudo apt-get install build-essential
    sudo apt install zlib1g-dev zlibc
    sudo apt install libssl-dev
    sudo apt-get install libsqlite3-dev
    sudo apt-get install libffi-dev
    sudo apt-get install zlib1g-dev
    sudo apt-get install libxcb-xinerama0
    sudo apt install libssl1.1 || sudo apt install libssl1.0
    sudo apt-get install libxcb-xinerama0
    sudo apt-get install libxcb-xinerama0
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

sudo apt-get install build-essential
sudo apt install zlib1g-dev zlibc
sudo apt install libssl-dev
sudo apt-get install libsqlite3-dev
sudo apt-get install libffi-dev
sudo apt-get install libxcb-xinerama0
sudo apt-get install libxcb-xinerama0
sudo apt install libssl1.1 || sudo apt install libssl1.0

# Создаем виртуальное окружение и активируем его
python3.8 -m venv myenv
source myenv/bin/activate

# Выполняем необходимые команды внутри виртуального окружения с использованием Python 3.6
python3.8 -m pip install --upgrade pip
python3.8 -m pip install -r requirements.txt
export QT_PLUGIN_PATH=$PWD/myenv/lib64/python3.8/site-packages/PyQt5/Qt/plugins/
pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp:./service/videohosting_service/tmp" --add-data "version.txt:." --add-data "icon.png:." --add-data "icon.ico:." --icon "icon.ico" Application.py

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

sudo rm -r usr
sudo rm data.tar.gz
sudo rm control.tar.gz

cd ../
rm -r myenv/
rm Application.spec

fi