<h1>
Для того, чтобы сделать сборку проекта, необходимо:<br></h1>
<h2>
1.Создать venv: "virtualenv --python=python3 venv"<br>
2.Для того чтобы работать в venv: "source venv/bin/activate"<br>
3.Скачать все зависимости: "pip install -r requirements.txt"<br>
4.Соответственно собрать проект: "pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" --add-data "service/videohosting_service/tmp:./service/videohosting_service/tmp" --add-data "version.txt:." --add-data "icon.png:." Application.py"
<br>
</h2>
<h1>
Required: python 3.6+, virtualenv
</h1>