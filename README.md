Для того, чтобы сделать сборку проекта, необходимо:<br>
1.Скачать все зависимости: "pip install -r requirements.txt"<br>
2.Соответственно собрать проект: "pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" Application.py
"