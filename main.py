import sys

import psycopg2
from PyQt5.uic.Compiler.qtproxies import QtCore
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QBrush, QFont
from PyQt6.QtWidgets import *
from psycopg2 import Error


current_relation_name = 'no'




def connect_to_db():
    try:
        with open("db_env.txt") as file:
            DB_USER = file.readline().strip().split('=')
            DB_USER = DB_USER[1]
            DB_PASSWORD = file.readline().strip().split('=')
            DB_PASSWORD = DB_PASSWORD[1]
            DB_HOST = file.readline().strip().split('=')
            DB_HOST = DB_HOST[1]
            DB_PORT = file.readline().strip().split('=')
            DB_PORT = DB_PORT[1]
            DB_NAME = file.readline().strip().split('=')
            DB_NAME = DB_NAME[1]
        connection = psycopg2.connect(
            user=f"{DB_USER}",
            password=f"{DB_PASSWORD}",
            host=f"{DB_HOST}",
            port=f"{DB_PORT}",
            database=f"{DB_NAME}"
        )
        print("Подключение к базе данных успешно установлено.")
        return connection
    except Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None

def print_relation_data(connection, table_name:str,qtable:QTableWidget):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name};")
        data = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]

        close_connection(connection)
        qtable.setRowCount(len(data))
        qtable.setColumnCount(len(column_names))
        qtable.setHorizontalHeaderLabels(column_names)

        for row_index, row_data in enumerate(data):
            for col_index, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                qtable.setItem(row_index, col_index, item)
        qtable.sortByColumn(0,Qt.SortOrder.AscendingOrder)
    except:
        print(f"Ошибка при выполнении запроса: {Error}")


def get_selected_row_text(qtable:QTableWidget):
    selected_items = qtable.selectedItems()
    if selected_items:
        row = selected_items[0].row()
        # column_count = qtable.columnCount()
        row_text = []

        # for col in range(column_count):
        item = qtable.item(row, 0)
        # print(item.text())
        if item is not None:
                row_text.append(item.text())
        return " ".join(row_text)


def add_new_row(table_name: str, qtable_name: QTableWidget): #мб сделать все id serial тогда не надо будет следить за ним, или можно в виде даты по секундно
    try:                                                      #  нежно сделать разграничение прав, типа если юзер такого сорта то тоакое доступно, и тд
        sql_command = f'INSERT INTO {table_name} VALUES ('
        for i in range(qtable_name.columnCount() - 1):
            sql_command = sql_command + f"'{qtable_name.item(0, i).text()}', "
        sql_command = sql_command + f"'{qtable_name.item(0, qtable_name.columnCount() - 1).text()}' )"
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute(sql_command)
        connection.commit()
        close_connection(connection)
    except Error as e:
        print(f"Ошибка при выполнении запроса: {e}")

def edit_row(table_name:str,qtable_name:QTableWidget):
    try:
        sql_command = f'UPDATE {table_name} SET '
        for i in range(1, qtable_name.columnCount() - 1):
            sql_command = sql_command + f"{qtable_name.horizontalHeaderItem(i).text()} = '{qtable_name.item(0, i).text()}', "
        sql_command = sql_command + f"{qtable_name.horizontalHeaderItem(qtable_name.columnCount() - 1).text()} = '{qtable_name.item(0, qtable_name.columnCount() - 1).text()}' "
        sql_command = sql_command + f"WHERE {qtable_name.horizontalHeaderItem(0).text()} = {qtable_name.item(0, 0).text()}"
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute(sql_command)
        connection.commit()
        close_connection(connection)
    except Error as e:
        print(f"Ошибка при выполнении запроса: {e}")


def close_connection(connection):
    if connection:
        connection.close()
        print("Соединение с базой данных закрыто.")


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
        font-family: sans-serif;
        font-size: 20px;
        font-weight:500;
    """
    return b

def resize_columns_to_content(qtable_name:QTableWidget):
    qtable_name.resizeColumnsToContents()

class def_TableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(default_linedit_style())
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.horizontalScrollBar().setSingleStep(20)
        self.verticalScrollBar().setSingleStep(20)

class def_Button(QPushButton):
    def __init__(self):
        super().__init__()
        self.resize(150,50)
        self.setStyleSheet(default_button_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class def_LineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.resize(400,30)
        self.setStyleSheet(default_linedit_style())
        self.setCursor(Qt.CursorShape.IBeamCursor)


class RelationManipulationPopup(QDialog):
    def __init__(self,qrelation_name):
        super().__init__()
        self.setFixedSize(800, 300)
        self.show()
        self.main_layout = QVBoxLayout(self)

        self.row_table_widget = self.rowTableWidget(qrelation_name)
        self.main_layout.addChildWidget(self.row_table_widget)

        self.cancel_button = self.cancelButton()
        self.cancel_button.clicked.connect(lambda: self.close())
        self.main_layout.addChildWidget(self.cancel_button)
        self.confirm_button = self.confirmButton()
        self.confirm_button.clicked.connect(lambda: self.close())
        self.main_layout.addChildWidget(self.confirm_button)

    def cancelButton(self):
        button = def_Button()
        button.setText("Отмена")
        button.setGeometry(25, 225, 150, 50)
        return button

    def confirmButton(self):
        button = def_Button()
        button.setText("Создать")
        button.setGeometry(625, 225, 150, 50)
        return button

    def rowTableWidget(self,qrelation_name:QTableWidget):
        widget = def_TableWidget()
        widget.setGeometry(25, 50, 750, 100)
        widget.setRowCount(1)
        widget.setColumnCount(qrelation_name.columnCount())
        self.column_names_qtable = []
        for i in range(qrelation_name.columnCount()):
            self.column_names_qtable.append(qrelation_name.horizontalHeaderItem(i).text())
            widget.setHorizontalHeaderLabels(self.column_names_qtable)
        resize_columns_to_content(widget)
        return widget

    def add_new_row(self,table_name: str, qtable_name: QTableWidget):
        try:
            sql_command = f'INSERT INTO {table_name} VALUES ('
            for i in range(qtable_name.columnCount() - 1):
                sql_command = sql_command + f"'{qtable_name.item(0, i).text()}', "
            sql_command = sql_command + f"'{qtable_name.item(0, qtable_name.columnCount() - 1).text()}' )"
            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute(sql_command)
            connection.commit()
            close_connection(connection)
        except Error as e:
            print(f"Ошибка при выполнении запроса: {e}")

    def edit_row(self,table_name: str, qtable_name: QTableWidget):
        try:
            sql_command = f'UPDATE {table_name} SET '
            for i in range(1, qtable_name.columnCount() - 1):
                sql_command = sql_command + f"{qtable_name.horizontalHeaderItem(i).text()} = '{qtable_name.item(0, i).text()}', "
            sql_command = sql_command + f"{qtable_name.horizontalHeaderItem(qtable_name.columnCount() - 1).text()} = '{qtable_name.item(0, qtable_name.columnCount() - 1).text()}' "
            sql_command = sql_command + f"WHERE {qtable_name.horizontalHeaderItem(0).text()} = {qtable_name.item(0, 0).text()}"
            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute(sql_command)
            connection.commit()
            close_connection(connection)
        except :
            print(f"Ошибка при выполнении запроса: {Error}")


class AddRowPopup(RelationManipulationPopup):
    def __init__(self,curr_table_name, qrelation_name):
        super().__init__(qrelation_name)
        self.setWindowTitle('Добавить запись')
        self.confirm_button.setText('Создать')
        self.confirm_button.clicked.connect(lambda checked=False,tbl_name=curr_table_name,qtbl_name=self.row_table_widget:self.add_new_row(tbl_name,qtbl_name))


class EditRowPopup(RelationManipulationPopup):
    def __init__(self,curr_table_name,qrelation_name):
        super().__init__(qrelation_name)
        self.setWindowTitle('Изменить Строку')
        self.confirm_button.setText('Изменить')
        self.confirm_button.clicked.connect(lambda checked=False,tbl_name=curr_table_name,qtbl_name=self.row_table_widget: self.edit_row(tbl_name,qtbl_name))

        try:
            row_id = qrelation_name.selectedItems()[0].row()
            for col_id in range(len(self.column_names_qtable)):
                self.row_table_widget.setItem(0, col_id, QTableWidgetItem(qrelation_name.item(row_id, col_id)))
        except:
            print(f"Ошибка при выполнении запроса: {Error}")
        resize_columns_to_content(self.row_table_widget)



class MainWindow(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.resize(1280,720)
        self.setWindowTitle("MVP Manik")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setScene(MainScene())
        self.setStyleSheet("""
                background-color: rgb(0,0,0);
                margin: 0px;
                border: none;
                """)

    def resizeEvent(self, event):
        self.fitInView(QRectF(0,0,1920-5,1080-5),Qt.AspectRatioMode.KeepAspectRatio)

def set_current_relation_name(name:str):
    global current_relation_name
    current_relation_name = name

class MainScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0,0,1920,1080)
        self.staked_widget = QStackedWidget()
        self.staked_widget.setGeometry(0, 0, 1920, 1080)
        self.addWidget(self.staked_widget)

        self.relative_view_widget = RelativeViewWidget()
        self.relative_view_widget.menu_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.menu_widget))
        def create_popup():
            create_popupp = AddRowPopup(current_relation_name,self.relative_view_widget.table_widget)
            create_popupp.confirm_button.clicked.connect(lambda: self.relative_view_widget.update_relation_data())
        self.relative_view_widget.create_button.clicked.connect(lambda :create_popup())
        def edit_popup():
            edit_popupp = EditRowPopup(current_relation_name,self.relative_view_widget.table_widget)
            # edit_popupp.setWindowTitle('Изменить запись')
            # edit_popupp.show()
            # edit_popupp.confirm_button.clicked.connect(lambda checked=False, tbl_name=current_relation_name, qtbl_name=edit_popupp.selected_row_table_widget: edit_row(tbl_name, qtbl_name))
            edit_popupp.confirm_button.clicked.connect(lambda :self.relative_view_widget.update_relation_data())
        self.relative_view_widget.edit_button.clicked.connect(lambda: edit_popup())
        # def del_popup():
        #     del_popupp = DeleteRowPopup(current_relation_name,self.relative_view_widget.table_widget)
        #     del_popupp.setWindowTitle('Изменить запись')
            # del_popupp.show()
            # del_popupp.confirm_button.clicked.connect(lambda :self.relative_view_widget.update_relation_data())
        # self.relative_view_widget.delete_button.clicked.connect(lambda :del_popup())
        self.staked_widget.addWidget(self.relative_view_widget)

        self.menu_widget = MenuWidget()
        self.menu_widget.logout_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.start_widget))
        self.menu_widget.close_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.relative_view_widget))
        for button in self.menu_widget.objects_scroll_area_widget.buttons:
            # button.clicked.connect(lambda :set_current_relation_name())
            button.clicked.connect(lambda :self.relative_view_widget.update_relation_data())
            button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.relative_view_widget))
        self.staked_widget.addWidget(self.menu_widget)

        self.registration_widget = RegistrationWidget()
        self.registration_widget.back_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.start_widget))
        self.staked_widget.addWidget(self.registration_widget)

        self.start_widget = StartWidget()
        self.start_widget.registration_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.registration_widget))
        self.start_widget.signin_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.menu_widget))
        self.start_widget.exit_button.clicked.connect(lambda :sys.exit())
        self.staked_widget.addWidget(self.start_widget)

        self.staked_widget.setCurrentWidget(self.start_widget)


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
        button = def_Button()
        button.setText("Войти")
        button.setGeometry(1600,900,150,50)
        return button

    def exitButton(self):
        button = def_Button()
        button.setText("Выйти")
        button.setGeometry(100,900,150,50)
        return button

    def registrationButton(self):
        button = def_Button()
        button.setText("Регистрация")
        button.setGeometry(1600,100,200,50)
        return button

    def loginLineEdit(self):
        field = def_LineEdit()
        field.setPlaceholderText("Логин")
        field.setGeometry(100,300,400,30)
        return field

    def passwordLineEdit(self):
        field = def_LineEdit()
        field.setPlaceholderText("Пароль")
        field.setGeometry(100,400,400,30)
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
        button = def_Button()
        button.setText("Регистрация")
        button.setGeometry(1600,900,200,50)
        return button

    def backButton(self):
        button = def_Button()
        button.setText("Назад")
        button.setGeometry(100,900,200,50)
        return button

    def lastNameLineEdit(self):
        field = def_LineEdit()
        field.setPlaceholderText("Фамилия")
        field.setGeometry(100,300,300,30)
        return field

    def firstNameLineEdit(self):
        field =def_LineEdit()
        field.setPlaceholderText("Имя")
        field.setGeometry(405,300,300,30)
        return field

    def midleNameLineEdit(self):
        field = def_LineEdit()
        field.setPlaceholderText("Отчество")
        field.setGeometry(710,300,300,30)
        return field

    def loginLineEdit(self):
        field = def_LineEdit()
        field.setPlaceholderText("Логин")
        field.setGeometry(100,400,400,30)
        return field

    def passwordLineEdit(self):
        field = def_LineEdit()
        field.setPlaceholderText("Пароль")
        field.setGeometry(100,500,400,30)
        field.setEchoMode(QLineEdit.EchoMode.Password)
        return field


class MenuWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1920,1080)
        self.layout = QVBoxLayout(self)

        self.close_button = self.closeButton()
        self.layout.addChildWidget(self.close_button)
        self.logout_button = self.logOutButton()
        self.layout.addChildWidget(self.logout_button)

        self.search_linedit = self.searchLineEdit()
        self.layout.addChildWidget(self.search_linedit)

        self.objects_scroll_area_widget = ObjectsScrollAreaWidget()
        self.objects_scroll_area_widget.setGeometry(50, 100, 1500, 800)
        self.layout.addChildWidget(self.objects_scroll_area_widget)

    def searchLineEdit(self):
        field = def_LineEdit()
        field.setPlaceholderText("Поиск")
        field.setGeometry(50,50,400,30)
        return field

    def closeButton(self):
        button = def_Button()
        button.setText("Закрыть")
        button.setGeometry(1600,50,200,50)
        return button

    def logOutButton(self):
        button = def_Button()
        button.setText("Выйти из\nсистемы")
        button.setGeometry(1600,900,200,75)
        return button


class ObjectsScrollAreaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.container)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.scroll_area)

        # for i in range(20):  # Создаем 20 кнопок для примера
        #     button = QPushButton(f"Кнопка {i + 1}")
        #     button.setStyleSheet(default_button_style())
        #     self.container_layout.addWidget(button)
        connection = connect_to_db()
        self.relation_names = []
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')")
            data = cursor.fetchall()
            self.relation_names = [str(name[0]) for name in data]
            close_connection(connection)
        except Error as e:
            print(f"Ошибка при выполнении запроса: {e}")

        self.buttons = []
        for i in range(len(self.relation_names)):
            button = QPushButton(f"{self.relation_names[i]}",self)
            button.clicked.connect(lambda checked=False, idx=int(i):set_current_relation_name(f'{self.relation_names[idx]}'))
            button.setStyleSheet(default_button_style())
            self.container_layout.addWidget(button)
            self.buttons.append(button)


class RelativeViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1920, 1080)
        self.layout = QVBoxLayout(self)

        self.menu_button = self.menuButton()
        self.layout.addChildWidget(self.menu_button)
        self.create_button = self.createButton()
        self.layout.addChildWidget(self.create_button)
        self.edit_button = self.editButton()
        self.layout.addChildWidget(self.edit_button)
        self.delete_button = self.deleteButton()
        self.layout.addChildWidget(self.delete_button)

        self.search_linedit = self.searchLineEdit()
        self.layout.addChildWidget(self.search_linedit)

        self.table_widget = self.tableWidget()
        self.layout.addChildWidget(self.table_widget)

    def searchLineEdit(self):
        field = def_LineEdit()
        field.setPlaceholderText("Поиск")
        field.setGeometry(1500, 50, 400, 30)
        return field

    def menuButton(self):
        button = def_Button()
        button.setText("Меню")
        button.setGeometry(50, 50, 200, 50)
        return button

    def createButton(self):
        button = def_Button()
        button.setText("Создать")
        button.setGeometry(305, 50, 200, 50)
        return button

    def editButton(self):
        button = def_Button()
        button.setText("Редактировать")
        button.setGeometry(510, 50, 210, 50)
        return button

    def deleteButton(self):
        button = def_Button()
        button.setText("Удалить")
        button.setGeometry(725, 50, 200, 50)
        return button

    def tableWidget(self):
        widget = def_TableWidget()
        widget.setGeometry(0,100,1920,980)
        return widget

    def update_relation_data(self):
        self.table_widget.clear()
        connection = connect_to_db()
        print(current_relation_name)
        print_relation_data(connection,current_relation_name,self.table_widget)
        resize_columns_to_content(self.table_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())