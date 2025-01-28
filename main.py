import sys

from PyQt5.uic.Compiler.qtproxies import QtCore
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QBrush, QFont
from PyQt6.QtWidgets import *


def default_button_style():
    b = """
    QPushButton{
        background-color: rgb(150,100,100);
        font-size:20px;
        font-family: sans-serif;
        font-weight: bold;
        letter-spacing: 0.3em;
        }
    QPushButton:hover{
        color: rgb(50,50,100);
        }
    """
    return b

def default_linedit_style():
    b = """
    QLineEdit{
        font-family: sans-serif;
        font-size: 20px;
        font-weight:500;
        }
    """
    return b

class MainWindow(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.resize(1280,720)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setScene(MainScene())
        self.setStyleSheet("""
                background-color: rgb(0,0,0);
                margin: 0px;
                border: none;
                """)

    def resizeEvent(self, event):
        self.fitInView(QRectF(0,0,1920,1080),Qt.AspectRatioMode.KeepAspectRatio)


# class MainStakedWidget(QStackedWidget):
#     def __init__(self):
#         super().__init__()
#         self.setGeometry(0, 0, 1920, 1080)
#
#         self.registration_widget = RegistrationWidget(self)
#         self.addWidget(self.registration_widget)
#         self.start_widget = StartWidget(self)
#         self.addWidget(self.start_widget)
#         self.setCurrentWidget(self.start_widget)

class MainScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0,0,1920,1080)
        self.staked_widget = QStackedWidget()
        self.staked_widget.setGeometry(0, 0, 1920, 1080)
        self.addWidget(self.staked_widget)

        self.registration_widget = RegistrationWidget()
        self.registration_widget.back_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.start_widget))
        self.staked_widget.addWidget(self.registration_widget)

        self.start_widget = StartWidget()
        self.start_widget.registration_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.registration_widget))
        self.start_widget.exit_button.clicked.connect(lambda :sys.exit())
        self.staked_widget.addWidget(self.start_widget)

        self.staked_widget.setCurrentWidget(self.start_widget)

    def registration_button_click(self):
        return self.staked_widget.setCurrentWidget(self.registration_widget)


class StartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1920,1080)

        self.layout = QVBoxLayout(self)

        self.signin_button = self.signInButton()
        self.layout.addChildWidget(self.signin_button)
        self.exit_button = self.exitButton()
        self.layout.addChildWidget(self.exit_button)
        self.registration_button = self.registrationButton()
        self.layout.addChildWidget(self.registration_button)

        self.login_linedit = self.loginLineEdit()
        self.layout.addChildWidget(self.login_linedit)
        self.password_linedit = self.passwordLineEdit()
        self.layout.addChildWidget(self.password_linedit)


    def signInButton(self):
        button = QPushButton()
        button.setText("Войти")
        button.setGeometry(1600,900,150,50)
        button.setStyleSheet(default_button_style())
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def exitButton(self):
        button = QPushButton()
        button.setText("Выйти")
        button.setGeometry(100,900,150,50)
        button.setStyleSheet(default_button_style())
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def registrationButton(self):
        button = QPushButton()
        button.setText("Регистрация")
        button.setGeometry(1600,100,200,50)
        button.setStyleSheet(default_button_style())
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def loginLineEdit(self):
        field = QLineEdit()
        field.setPlaceholderText("Логин")
        field.setGeometry(100,300,400,30)
        field.setStyleSheet(default_linedit_style())
        field.setCursor(Qt.CursorShape.IBeamCursor)
        return field

    def passwordLineEdit(self):
        field = QLineEdit()
        field.setPlaceholderText("Пароль")
        field.setGeometry(100,400,400,30)
        field.setStyleSheet(default_linedit_style())
        field.setCursor(Qt.CursorShape.IBeamCursor)
        field.setEchoMode(QLineEdit.EchoMode.Password)
        return field



class RegistrationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1920,1080)

        self.layout = QVBoxLayout(self)

        self.back_button = self.backButton()
        self.layout.addChildWidget(self.back_button)
        self.registration_button = self.registrationButton()
        self.layout.addChildWidget(self.registration_button)

        self.lastname_linedit = self.lastNameLineEdit()
        self.layout.addChildWidget(self.lastname_linedit)
        self.firstname_linedit = self.firstNameLineEdit()
        self.layout.addChildWidget(self.firstname_linedit)
        self.midlename_linedit = self.midleNameLineEdit()
        self.layout.addChildWidget(self.midlename_linedit)
        self.login_linedit = self.loginLineEdit()
        self.layout.addChildWidget(self.login_linedit)
        self.password_linedit = self.passwordLineEdit()
        self.layout.addChildWidget(self.password_linedit)

    def registrationButton(self):
        button = QPushButton()
        button.setText("Регистрация")
        button.setGeometry(1600,900,200,50)
        button.setStyleSheet(default_button_style())
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def backButton(self):
        button = QPushButton()
        button.setText("Назад")
        button.setGeometry(100,900,200,50)
        button.setStyleSheet(default_button_style())
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def lastNameLineEdit(self):
        field = QLineEdit()
        field.setPlaceholderText("Фамилия")
        field.setGeometry(100,300,300,30)
        field.setStyleSheet(default_linedit_style())
        field.setCursor(Qt.CursorShape.IBeamCursor)
        return field

    def firstNameLineEdit(self):
        field = QLineEdit()
        field.setPlaceholderText("Имя")
        field.setGeometry(405,300,300,30)
        field.setStyleSheet(default_linedit_style())
        field.setCursor(Qt.CursorShape.IBeamCursor)
        return field

    def midleNameLineEdit(self):
        field = QLineEdit()
        field.setPlaceholderText("Отчество")
        field.setGeometry(710,300,300,30)
        field.setStyleSheet(default_linedit_style())
        field.setCursor(Qt.CursorShape.IBeamCursor)
        return field

    def loginLineEdit(self):
        field = QLineEdit()
        field.setPlaceholderText("Логин")
        field.setGeometry(100,400,400,30)
        field.setStyleSheet(default_linedit_style())
        field.setCursor(Qt.CursorShape.IBeamCursor)
        return field

    def passwordLineEdit(self):
        field = QLineEdit()
        field.setPlaceholderText("Пароль")
        field.setGeometry(100,500,400,30)
        field.setStyleSheet(default_linedit_style())
        field.setCursor(Qt.CursorShape.IBeamCursor)
        field.setEchoMode(QLineEdit.EchoMode.Password)
        return field




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())