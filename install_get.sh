# Обновляем информацию о пакетах и устанавливаем необходимые пакеты
sudo apt-get update
sudo apt-get install -y python3.6 python3.6-venv

# Создаем виртуальное окружение и активируем его
python3.6 -m venv myenv
source myenv/bin/activate

# Выполняем необходимые команды внутри виртуального окружения с использованием Python 3.6
pip install -r requirements.txt
pyinstaller -y --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp:./service/videohosting_service/tmp" Application.py

tar -cvf BuxarVideoUploader.tar dist/ build/

sudo rm -r myenv/

# Деактивируем виртуальное окружение
deactivate
