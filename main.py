from PySide6.QtCore import QLocale, Qt, QRect
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QLabel, QToolButton, QWidget, \
    QMessageBox, QDialog, QVBoxLayout, QCheckBox, QGroupBox, QHBoxLayout
import sys
import os
import configparser
import shutil
from translations import translations

from loc import process_files, PatchUrlNotFoundException

BASE_FONT = QFont("Arial", 10)
BUTTON_FONT = QFont("Arial", 10, QFont.Bold)
LABEL_LOGS_FONT = QFont("Arial", 18)

GRAY_DARK = "rgb(120, 120, 120)"
MEDIUM_BLACK = "rgb(100, 100, 100)"
BLACK_DARK = "rgb(30, 30, 30)"
LIGHT_BLUE = "rgb(0,191,255)"
WHITE_TEXT = "rgb(255, 255, 255)"

icon_path = os.path.join(sys._MEIPASS, 'assets', 'icon.ico')


class ui_main(object):

    def update_ui_language(self, language):
        self.localisationbox.setText(translations[language]["Start Localisation"])
        self.loc_deep.setText(translations[language]["Advanced translation (beta)"])
        self.fontbox.setText(translations[language]["Font"])
        self.loc_language.setText(translations[language]["Translation Language:"])
        self.contacts.setText(translations[language]["Contacts"])

    def open_front_window(self):
        self.new_window = QMainWindow()
        self.new_window.setWindowTitle("Front")
        self.new_window.setFixedSize(240, 350)
        self.new_window.setWindowIcon(QIcon(icon_path))

        self.button_ru = QGroupBox("Front: RU", self.new_window)
        self.button_ru.setGeometry(QRect(20, 20, 200, 65))
        layout_ru = QHBoxLayout(self.button_ru)
        button_ru_standard = QPushButton("Standard")
        button_ru_standard.clicked.connect(lambda: self.copy_font_file('RU'))
        button_ru_custom = QPushButton("Custom")
        button_ru_custom.setStyleSheet(f"background-color: {MEDIUM_BLACK};")
        layout_ru.addWidget(button_ru_standard)
        layout_ru.addWidget(button_ru_custom)

        self.button_eu = QGroupBox("Front: EU, DE, FR, SP, ES, PT, TR", self.new_window)
        self.button_eu.setGeometry(QRect(20, 100, 200, 65))
        layout_eu = QHBoxLayout(self.button_eu)
        button_eu_standard = QPushButton("Standard")
        button_eu_standard.clicked.connect(lambda: self.copy_font_file('EN'))
        button_eu_custom = QPushButton("Custom")
        button_eu_custom.setStyleSheet(f"background-color: {MEDIUM_BLACK};")
        layout_eu.addWidget(button_eu_standard)
        layout_eu.addWidget(button_eu_custom)

        self.button_jp = QGroupBox("Front: JP", self.new_window)
        self.button_jp.setGeometry(QRect(20, 180, 200, 65))
        layout_jp = QHBoxLayout(self.button_jp)
        button_jp_standard = QPushButton("Standard")
        button_jp_standard.clicked.connect(lambda: self.copy_font_file('JP'))
        button_jp_custom = QPushButton("Custom")
        button_jp_custom.setStyleSheet(f"background-color: {MEDIUM_BLACK};")
        layout_jp.addWidget(button_jp_standard)
        layout_jp.addWidget(button_jp_custom)

        self.button_tw = QGroupBox("Front: TW", self.new_window)
        self.button_tw.setGeometry(QRect(20, 260, 200, 65))
        layout_tw = QHBoxLayout(self.button_tw)
        button_tw_standard = QPushButton("Standard")
        button_tw_standard.clicked.connect(lambda: self.copy_font_file('TW'))
        button_tw_custom = QPushButton("Custom")
        button_tw_custom.setStyleSheet(f"background-color: {MEDIUM_BLACK};")
        layout_tw.addWidget(button_tw_standard)
        layout_tw.addWidget(button_tw_custom)

        self.new_window.show()

    def copy_font_file(self, region):
        src_path = os.path.join(sys._MEIPASS, 'font', region, 'pearl.ttf')
        dst_path = os.path.join('prestringtable', 'font', 'pearl.ttf')
        if not os.path.exists(os.path.dirname(dst_path)):
            os.makedirs(os.path.dirname(dst_path))
        shutil.copy(src_path, dst_path)

    def setupUi(self, ui_main):
        if not ui_main.objectName():
            ui_main.setObjectName(u"ui_main")
        ui_main.setStyleSheet(f""" QWidget {{ background-color: {GRAY_DARK}; }}
    QTextEdit, QPushButton, QToolButton {{ background-color: {MEDIUM_BLACK}; color: {WHITE_TEXT}; border: 2px solid #000000; border-radius: 8px; }}
    QTextEdit:hover, QPushButton:hover, QToolButton:hover, QComboBox:hover {{ background-color: {BLACK_DARK}; }}
    QCheckBox {{ background: transparent; color: {WHITE_TEXT}; border: none; border-radius: 4px; }}
    QComboBox {{ background-color: {MEDIUM_BLACK}; color: {WHITE_TEXT}; width: 25px; }}
    QAbstractItemView {{ background-color: {BLACK_DARK}; color: {WHITE_TEXT}; }}
""")

        self.centralwidget = QWidget(ui_main)
        self.centralwidget.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        ui_main.setCentralWidget(self.centralwidget)

        # Кнопка Start Localisation
        self.localisationbox = QPushButton(self.centralwidget)
        self.localisationbox.setGeometry(QRect(250, 135, 210, 80))
        self.localisationbox.setFont(BUTTON_FONT)

        # Рамка для regionbox, loc_deep, loc_language
        self.group_box = QGroupBox(self.centralwidget)
        self.group_box.setGeometry(QRect(20, 135, 210, 80))
        self.group_box.setStyleSheet(f"border: 2px solid #3A3A3A;")

        # Кнопка для выбора региона локализации
        self.regionbox = QComboBox(self.centralwidget)
        self.regionbox.setGeometry(QRect(160, 145, 50, 30))
        region_names = ["RU", "EN", "DE", "FR", "SP", "JP", "PT", "TR", "TW"]
        self.regionbox.setStyleSheet("QComboBox { border-radius: 0px; }")
        for i, region in enumerate(region_names):
            self.regionbox.addItem(region, region)

        # Установка региона по умолчанию на основе языка системы
        default_region = ui_main.get_system_language()
        index = self.regionbox.findText(default_region)
        if index >= 0:
            self.regionbox.setCurrentIndex(index)

        # кнопка Advanced translation
        self.loc_deep = QCheckBox(self.centralwidget)
        self.loc_deep.setGeometry(QRect(34, 185, 190, 20))

        # кнопка Front
        self.fontbox = QToolButton(self.centralwidget)
        self.fontbox.setGeometry(QRect(330, 80, 130, 30))
        self.fontbox.clicked.connect(self.open_front_window)

        # кнопка для отображения логов
        self.label_logs = QLabel(self.centralwidget)
        self.label_logs.setGeometry(QRect(20, 30, 280, 80))
        self.label_logs.setStyleSheet(f"background-color: {BLACK_DARK}; color: {LIGHT_BLUE};")
        self.label_logs.setFont(LABEL_LOGS_FONT)
        self.label_logs.setAlignment(Qt.AlignCenter)

        # текст Translation Language
        self.loc_language = QLabel(self.centralwidget)
        self.loc_language.setGeometry(QRect(35, 145, 120, 30))
        self.loc_language.setStyleSheet(f"background: transparent; color: {WHITE_TEXT};")

        # кнопка Contacts
        self.contacts = QPushButton(self.centralwidget)
        self.contacts.setGeometry(QRect(330, 30, 131, 31))


class contactsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contacts")
        self.setWindowIcon(QIcon(icon_path))
        layout = QVBoxLayout()
        text_label = QLabel(
            "My contacts<br><br>"
            "GitHub: <a href='https://github.com/PooROg'>github.com/PooROg</a><br>"
            "Discord: <a href='https://discordapp.com/users/182267097575981076'>pumbaa.</a>")
        text_label.setOpenExternalLinks(True)
        text_label.setTextFormat(Qt.RichText)
        layout.addWidget(text_label)
        self.setLayout(layout)


class MainWindow(QMainWindow, ui_main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("BDO Localisation")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(480, 230)
        self.localisationbox.clicked.connect(self.run_main_script)
        self.contacts.clicked.connect(self.open_contacts_window)
        self.check_resource_ini()
        self.regionbox.currentIndexChanged.connect(self.change_language)
        self.update_ui_language(self.get_system_language())
        self.regionbox.currentIndexChanged.connect(self.check_region_selection)

    def change_language(self):
        self.update_ui_language(self.regionbox.currentText())
        self.check_resource_ini()

    def get_system_language(self):
        locale = QLocale.system().name()[:2]
        if locale == 'ru':
            return 'RU'
        elif locale == 'de':
            return 'DE'
        elif locale == 'fr':
            return 'FR'
        elif locale == 'sp':
            return 'SP'
        elif locale == 'jp':
            return 'JP'
        elif locale == 'pt':
            return 'PT'
        elif locale == 'tr':
            return 'TR'
        elif locale == 'tw':
            return 'TW'
        else:
            return 'EN'

    def update_ui_language(self, language):
        super().update_ui_language(language)
        self.check_resource_ini()

    def check_resource_ini(self):
        resource_ini_path = 'resource.ini'
        if os.path.exists(resource_ini_path):
            config = configparser.ConfigParser()
            config.read(resource_ini_path)
            region = config.get('SERVICE', 'RES', fallback=None)
            region_info = region.replace('_', '')
            self.update_logs(translations[self.get_ui_language()]["Original region:"] + f" {region_info}")
        else:
            self.update_logs(translations[self.get_ui_language()]["resource.ini not found"])

    def get_ui_language(self):      # Меняем язык интерфейса с помощью regionbox
        return self.regionbox.currentText()

    def check_region_selection(self): # Блокируем ативацию loc_deep, если для региона не реализован функционал translated_txt_path
        selected_region = self.regionbox.currentText().lower()
        if selected_region != 'ru':
            self.loc_deep.setEnabled(False)
            self.loc_deep.setStyleSheet("color: rgb(60, 60, 60); text-decoration: line-through;")
        else:
            self.loc_deep.setEnabled(True)
            self.loc_deep.setStyleSheet("")

    def run_main_script(self):
        selected_region = self.regionbox.currentText().lower()
        loc_deep_active = self.loc_deep.isChecked()
        self.update_logs(translations[self.get_ui_language()]["Processing..."])

        try:
            process_files(selected_region, loc_deep_active)
            self.update_logs(translations[self.get_ui_language()]["Successfully"])
        except PatchUrlNotFoundException as e:
            self.update_logs(translations[self.get_ui_language()]["Error"] + f": {e}")
            QMessageBox.warning(self, translations[self.get_ui_language()]["Error"],
                                translations[self.get_ui_language()][
                                    "Could not find the PATCH_URL value in the service.ini file."])
        except Exception as e:
            self.update_logs(translations[self.get_ui_language()]["An error occurred:"] + f" {e}")
            QMessageBox.warning(self, translations[self.get_ui_language()]["Error"],
                                translations[self.get_ui_language()]["An error occurred:"] + f" {e}")

    def open_contacts_window(self):  # Окно для кнопки contacts
        contacts_window = contactsWindow()
        contacts_window.exec()

    def update_logs(self, message):  # Принудительно изменяем текст в label_logs
        self.label_logs.setText(message)
        self.label_logs.repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    app.exec()
