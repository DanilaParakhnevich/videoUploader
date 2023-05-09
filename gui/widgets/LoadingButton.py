from PyQt5 import QtCore, QtGui, QtWidgets
import os


class LoadingButton(QtWidgets.QPushButton):
    @QtCore.pyqtSlot()
    def start(self):
        if hasattr(self, "_movie"):
            self._movie.start()

    @QtCore.pyqtSlot()
    def stop(self):
        if hasattr(self, "_movie"):
            self._movie.stop()
            self.setIcon(QtGui.QIcon())

    def setGif(self, filename):
        if not hasattr(self, "_movie"):
            self._movie = QtGui.QMovie(self)
            self._movie.setFileName(filename)
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

    @QtCore.pyqtSlot(int)
    def on_frameChanged(self, frameNumber):
        self.setIcon(QtGui.QIcon(self._movie.currentPixmap()))


class AnimatedButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # читаем части гифки из определенной папки
        folder_path = r"D:\Programs\BuxarVideoUploader-master\gui\widgets\button_icons"
        icons = []

        for filename in os.listdir(folder_path):
            if filename.endswith(".gif"):
                icon = QtGui.QIcon(os.path.join(folder_path, filename))
                icons.append(icon)

        # Загрузка иконок для каждого кадра GIF-анимации
        self.icons = icons

        # Инициализация переменных для управления анимацией
        self.current_frame = 0
        self.playing = False

        # Создание таймера для переключения иконок
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)  # Интервал в миллисекундах между кадрами
        self.timer.timeout.connect(self.update_icon)

    def start_animation(self):
        # Начало воспроизведения GIF-анимации
        self.playing = True
        self.timer.start()

    def stop_animation(self):
        # Остановка воспроизведения GIF-анимации
        self.playing = False

    def update_icon(self):
        if not self.playing:
            # Остановка таймера, если процесс завершен
            self.timer.stop()
            self.setIcon(QtGui.QIcon())
            return

        # Переключение на следующий кадр анимации
        self.current_frame = (self.current_frame + 1) % len(self.icons)
        self.setIcon(self.icons[self.current_frame])
