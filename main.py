import sys, json, ast, traceback

import psycopg2
from PyQt6.QtCore import QRectF, Qt, QRect,QTime, QTimer 
from PyQt6.QtGui import QColor, QBrush, QFont,QTextOption
from PyQt6.QtWidgets import *
from psycopg2 import sql
from psycopg2.errorcodes import NULL_VALUE_NOT_ALLOWED



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
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None

def close_connection(connection):
    if connection:
        connection.close()
        print("Соединение с базой данных закрыто.")

def print_exception_info(exception:Exception):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    last_traceback = traceback.extract_tb(exc_traceback)[-1]
    
    filename = last_traceback.filename
    lineno = last_traceback.lineno
    funcname = last_traceback.name
    line = last_traceback.line
    
    print(f"Произошло исключение: {exception}")
    print(f"Файл: {filename}")
    print(f"Строка: {lineno} (в функции {funcname})")
    print(f"Код: {line}")

def set_last_global_message(message:str):
    global last_global_message
    last_global_message = f'Последнее сообщение: {message}'

def get_row_data(table: QTableWidget, row_index: int) -> dict:
    row_data = {}
    for col in range(table.columnCount()):
        header = table.horizontalHeaderItem(col).text()
        if isinstance(table.cellWidget(row_index,col), QComboBox):
            item = table.cellWidget(row_index,col)
            row_data[header]= item.currentText() if item else None
        else:
            item = table.item(row_index, col)
            row_data[header] = item.text() if item else None
    return row_data


def add_new_row(table_name: str, data:dict):
    connection = connect_to_db()
    try:
        cursor = connection.cursor()
        columns = sql.SQL(', ').join(map(sql.Identifier, data.keys()))
        values = sql.SQL(', ').join(map(sql.Literal, data.values()))
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({});").format(
            sql.Identifier(table_name),
            columns,
            values
        )
        cursor.execute(query)
        connection.commit()
        print(f"Данные успешно добавлены в таблицу {table_name}.")
        set_last_global_message(f"Данные успешно добавлены в таблицу {table_name}.")
        close_connection(connection)
        return True
    except Exception as e:
        print_exception_info(e)
        close_connection(connection)

def edit_row(table_name:str,set_values:dict,where_id_name:str,where_id_eq:str):
    connection = connect_to_db()
    try:
        cursor = connection.cursor()

        # Преобразуем значения 'None' в None (NULL в SQL)
        for key in set_values:
            if set_values[key] == 'None':
                set_values[key] = None

        # Формируем SET-часть запроса
        set_clause = sql.SQL(', ').join(
            sql.SQL("{} = {}").format(sql.Identifier(key), sql.Literal(value))
            for key, value in set_values.items()
        )
        where_id = sql.SQL("{} = {}").format(sql.Identifier(where_id_name),sql.Literal(where_id_eq))
        # Формируем полный запрос
        query = sql.SQL("UPDATE {} SET {} WHERE {} RETURNING *").format(
            sql.Identifier(table_name),
            set_clause, 
            where_id
        )
        cursor.execute(query)

        updated_row = cursor.fetchone()

        connection.commit()
        print(f"Данные в таблице {table_name} успешно обновлены.")
        set_last_global_message(f"Данные в таблице {table_name} успешно обновлены.")
        # Закрываем соединение
        close_connection(connection)
        return True

    except Exception as e:
        print_exception_info(e)
        close_connection(connection)
        return False
    

def del_row(table_name:str,where_id:str):
    connection = connect_to_db()
    try:    
        cursor = connection.cursor()
        query = sql.SQL("UPDATE {} SET удален = TRUE, дата_удаления = DATE_TRUNC('second', NOW()) WHERE {}").format(
            sql.Identifier(table_name),
            sql.SQL(where_id)
        )
        cursor.execute(query)
        connection.commit()
        close_connection(connection)
        print(f"Данные в таблице {table_name} успешно помечены удаленными.")
        set_last_global_message(f"Данные в таблице {table_name} успешно помечены удаленными.")
        return True
    except Exception as e:
        print_exception_info(e)
        close_connection(connection)

def del_row_from_db(table_name:str,where_id:str):
    connection = connect_to_db()
    try:    
        cursor = connection.cursor()
        query = sql.SQL("DELETE FROM {} WHERE {}").format(
            sql.Identifier(table_name),
            sql.SQL(where_id)
        )
        cursor.execute(query)
        connection.commit()
        close_connection(connection)
        print(f"Данные в таблице {table_name} успешно удалены.")
        set_last_global_message(f"Данные в таблице {table_name} успешно удалены.")
        return True
    except Exception as e:
        print_exception_info(e)
        close_connection(connection)


def default_button_style():
    b = """
    QPushButton{
        background-color:darkolivegreen;
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
def default_font_style():
    b = """
        font-family: sans-serif;
        font-size: 20px;
        font-weight:500;
    """
    return b

def default_linedit_style():
    b = """
        font-family: sans-serif;
        font-size: 20px;
        font-weight:500;
        background-color:greenyellow;
    """
    return b

def resize_columns_to_content(qtable_name:QTableWidget):
    qtable_name.resizeColumnsToContents()


class def_TableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f'{default_font_style()} background-color:darkgray;')
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
    def __init__(self,source_table):
        super().__init__()
        self.setFixedSize(800, 300)
        self.setModal(True)
        self.show()
        self.main_layout = QVBoxLayout(self)

        self.row_table_widget = self.rowTableWidget(source_table)
        self.main_layout.addChildWidget(self.row_table_widget)

        self.cancel_button = self.cancelButton()
        self.cancel_button.clicked.connect(lambda: self.close())
        self.cancel_button.clicked.connect(lambda: self.deleteLater())
        self.main_layout.addChildWidget(self.cancel_button)
        self.confirm_button = self.confirmButton()
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

    def rowTableWidget(self,source_table:QTableWidget):
        col_count = source_table.columnCount()
        widget = def_TableWidget()
        widget.setGeometry(25, 50, 750, 100)
        widget.setRowCount(1)
        widget.setColumnCount(col_count)
        for col in range(col_count):
            header = source_table.horizontalHeaderItem(col)
            if header:
                widget.setHorizontalHeaderItem(col, QTableWidgetItem(header.text()))
        resize_columns_to_content(widget)
        return widget

    def remove_columns(self, table: QTableWidget, columns_to_remove: list):
        column_count = table.columnCount()
        for col in sorted(columns_to_remove, reverse=True):
            if 0 <= col < column_count:
                table.removeColumn(col)
            else:
                print(f"Предупреждение: столбец с индексом {col} не существует и будет пропущен.")

    def get_column_index_by_header(self, table: QTableWidget, header: str) -> int:
        for col in range(table.columnCount()):
            if table.horizontalHeaderItem(col).text() == header:
                return col
        return -1

class AddRowPopup(RelationManipulationPopup):
    def __init__(self,source_table):
        super().__init__(source_table)
        self.setWindowTitle('Добавить cтроку')
        connection = connect_to_db()
        try:    
            cursor = connection.cursor()
            query = sql.SQL("""
                SELECT * FROM {rela_name}
            """).format(
                rela_name = sql.Identifier(f'Регулирование_{current_relation_name}')
            )
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                result = {}
                for row in rows:
                    key = row[0]
                    values = list(row[1:])
                    result[key] = values
                columns_to_remove = []
                for res in result:
                    if str(result[res][1]) not in ['все','создание']:
                        columns_to_remove.append(res)
                indices_to_remove = [self.get_column_index_by_header(self.row_table_widget, header) for header in columns_to_remove]
                self.remove_columns(self.row_table_widget, indices_to_remove)
            except:
                print(f"Отношения Регулирование_{current_relation_name} нет")
            self.confirm_button.setText('Создать')
            def conf_butt():
                try:
                    row_data = get_row_data(self.row_table_widget,0)
                    result =add_new_row(current_relation_name,row_data)
                    if result:
                        self.close()
                except Exception as e:
                    print_exception_info(e)
            self.confirm_button.clicked.connect(lambda :conf_butt())
            close_connection(connection)
        except Exception as e:
            print_exception_info(e)
            close_connection(connection)


class EditRowPopup(RelationManipulationPopup):
    def __init__(self,source_table:QTableWidget):
        super().__init__(source_table)
        self.setWindowTitle('Изменить cтроку')
        self.confirm_button.setText('Изменить')
        row_id = source_table.currentRow()
        try:
            for col_id in range(source_table.columnCount()):
                item = source_table.item(row_id, col_id)
                new_item = QTableWidgetItem(item.text() if item is not None else None)
                self.row_table_widget.setItem(0, col_id, new_item)
        except Exception as e:
          print_exception_info(e)
        resize_columns_to_content(self.row_table_widget)
        connection = connect_to_db()
        try:     
            cursor = connection.cursor()
            query = sql.SQL("""
                SELECT * FROM {rela_name}
            """).format(
                rela_name = sql.Identifier(f'Регулирование_{current_relation_name}')
            )
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                result = {}
                for row in rows:
                    key = row[0]
                    values = list(row[1:])
                    result[key] = values
                columns_to_remove = []
                for res in result:
                    if str(result[res][1]) not in ['все','обновление']:
                        columns_to_remove.append(res)
                indices_to_remove = [self.get_column_index_by_header(self.row_table_widget, header) for header in columns_to_remove]
                self.remove_columns(self.row_table_widget, indices_to_remove)
            except Exception as e:
                print(f"Отношения Регулирование_{current_relation_name} нет")
                print_exception_info(e)
            def conf_butt():
                try:
                    row_data = get_row_data(self.row_table_widget,0)
                    result = edit_row(current_relation_name,row_data,source_table.horizontalHeaderItem(0).text(),source_table.item(row_id,0).text())
                    if result:
                        self.close()
                except Exception as e:
                    print_exception_info(e)
            self.confirm_button.clicked.connect(lambda :conf_butt())
            close_connection(connection)
        except Exception as e:
            print_exception_info(e)
            close_connection(connection)


class DeleteRowPopup(RelationManipulationPopup):
    def __init__(self,source_table:QTableWidget):
        super().__init__(source_table)
        self.setWindowTitle('Удалить cтроку')
        self.confirm_button.setText('Удалить')
        are_you_sure = QLabel("")
        are_you_sure.setStyleSheet(default_font_style())
        are_you_sure.setGeometry(50,20,600,30)
        self.main_layout.addChildWidget(are_you_sure) 
        row_id = source_table.currentRow()
        try:
            for col_id in range(source_table.columnCount()):
                item = source_table.item(row_id, col_id)
                new_item = QTableWidgetItem(item.text())
                self.row_table_widget.setItem(0, col_id, new_item)
        except Exception as e:
            print_exception_info(e)
        where_pk_eq = source_table.horizontalHeaderItem(0).text()+' = '+source_table.item(row_id,0).text()  
        resize_columns_to_content(self.row_table_widget)  
        if current_user_role !='админ':
            are_you_sure.setText("Вы уверены, что хотите пометить на удаление эту строку?")
            def conf_butt(where_id:str):
                try:
                    result = del_row(current_relation_name,str(where_id))
                    if result:
                        self.close()
                except Exception as e:
                    print_exception_info(e)
        else:
            are_you_sure.setText("АДМИН, вы уверенны, что необходимо удалить эту строку?")
            def conf_butt(where_id:str):
                try:
                    result = del_row_from_db(current_relation_name,str(where_id))
                    if result:
                        self.close()
                except Exception as e:
                    print_exception_info(e)
        self.confirm_button.clicked.connect(lambda :conf_butt(where_pk_eq))


class GraphManipulationPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 300)
        self.setModal(True)
        self.show()
        self.main_layout = QVBoxLayout(self)

        self.start_timedit = self.startTimeEdit()
        self.main_layout.addChildWidget(self.start_timedit)
        self.end_timedit = self.endTimeEdit()
        self.main_layout.addChildWidget(self.end_timedit)
        self.duty_textedit = self.dutyTextEdit()
        self.main_layout.addChildWidget(self.duty_textedit)
        self.cancel_button = self.cancelButton()
        self.cancel_button.clicked.connect(lambda: self.close())
        self.cancel_button.clicked.connect(lambda: self.deleteLater())
        self.main_layout.addChildWidget(self.cancel_button)
        self.confirm_button = self.confirmButton()
        self.main_layout.addChildWidget(self.confirm_button)

    def startTimeEdit(self):
        timedit = QTimeEdit()
        timedit.setDisplayFormat("HH:mm")
        timedit.setGeometry(10,10,100,30)
        return timedit
    
    def endTimeEdit(self):
        timedit = QTimeEdit()
        timedit.setDisplayFormat("HH:mm")
        timedit.setGeometry(115,10,100,30)
        return timedit

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

    def dutyTextEdit(self):
        linedit = QTextEdit()
        linedit.setStyleSheet("font-size:20px")
        linedit.setGeometry(25, 50, 750, 100)
        linedit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        return linedit


class AddTimeIntervalPopup(GraphManipulationPopup):
    def __init__(self,employee_fio:str,employee_role:str,picked_calendar_date:str):
        super().__init__()
        self.setWindowTitle("Добавить временной промежуток")
        self.confirm_button.setText("Добавить")
        def conf_butt(time_interval:str,duty_desc:str):
            connection = connect_to_db()
            try:
                cursor = connection.cursor()
                query = sql.SQL("""
                    SELECT номер_сотрудника FROM Сотрудники WHERE фио = %s AND роль = %s
                """)
                cursor.execute(query, (employee_fio,employee_role))
                employee_num = cursor.fetchall()[0][0]
                query = sql.SQL("""
                    UPDATE Графики_работы
                    SET временные_промежутки = jsonb_insert(
                        временные_промежутки,
                        {time_slot},
                        {description},
                        true
                    )
                    WHERE сотрудник = %s
                    AND дата_начала::date <= {pick_date}::date
                    AND дата_конца::date >= {pick_date}::date
                    RETURNING *
                """).format(
                    time_slot=sql.Literal(time_interval),
                    description=sql.Literal(f'"{duty_desc}"'),
                    pick_date = sql.Literal(picked_calendar_date)
                )
                cursor.execute(query,(employee_num,))
                result = cursor.fetchall()
                connection.commit()
                close_connection(connection)
                if result:
                    print(f"Новый временной промежуток: \n{result};\n ..успешно добавлен")
                    set_last_global_message(f"Новый временной промежуток: \n{result};\n ..успешно добавлен")
                else:
                    print("Новый временной промежуток не был добавлен") 
                    set_last_global_message("Новый временной промежуток не был добавлен") 
                self.close()
            except Exception as e:
               print_exception_info(e)
               close_connection(connection)
        self.confirm_button.clicked.connect(lambda :conf_butt(f'{{{self.start_timedit.text()} - {self.end_timedit.text()}}}', self.duty_textedit.toPlainText()))


class EditTimeIntervalPopup(GraphManipulationPopup):
    def __init__(self, employee_fio: str, employee_role: str, table_widget: QTableWidget, selected_row: int):
        super().__init__()
        self.setWindowTitle("Изменить временной промежуток")
        self.confirm_button.setText("Изменить")
        
        # Сохраняем ссылку на таблицу и выбранную строку
        self.table_widget = table_widget
        self.selected_row = selected_row

        # Заполняем поля из выбранной строки таблицы
        if self.selected_row >= 0 and self.selected_row is not None:
            time_slot = self.table_widget.item(self.selected_row, 0).text()  # "9:00 - 17:00"
            description = self.table_widget.item(self.selected_row, 1).text()  # Описание
            
            start_time, end_time = time_slot.split(" - ")
            self.start_timedit.setTime(QTime.fromString(start_time))
            self.end_timedit.setTime(QTime.fromString(end_time))
            self.duty_textedit.setPlainText(description)

        def conf_butt(time_interval: str, duty_desc: str):
            connection = connect_to_db()
            try:
                
                cursor = connection.cursor()

                # Получаем номер сотрудника
                query = sql.SQL("""
                    SELECT номер_сотрудника FROM Сотрудники WHERE фио = %s AND роль = %s
                """)
                cursor.execute(query, (employee_fio, employee_role))
                employee_num = cursor.fetchall()[0][0]

                # Исходный и новый временной промежуток
                old_time_slot = self.table_widget.item(self.selected_row, 0).text()
                new_time_slot = time_interval.strip("{}")  # Убираем лишние скобки
                description = duty_desc

                # Проверяем текущее значение временные_промежутки
                query = sql.SQL("""
                    SELECT временные_промежутки FROM Графики_работы WHERE сотрудник = %s
                """)
                cursor.execute(query, (employee_num,))
                current_schedule = cursor.fetchone()[0] or '{}'

                # Если старый временной промежуток отличается, удаляем его
                if old_time_slot != new_time_slot and old_time_slot in current_schedule:
                    query = sql.SQL("""
                        UPDATE Графики_работы
                        SET временные_промежутки = временные_промежутки - %s
                        WHERE сотрудник = %s
                    """)
                    cursor.execute(query, (f'{{{old_time_slot}}}', employee_num))

                # Обновляем или добавляем новый временной промежуток
                query = sql.SQL("""
                   UPDATE Графики_работы
                    SET временные_промежутки = jsonb_set(
                        временные_промежутки,
                        %s,
                        %s,
                        true
                    )
                    WHERE сотрудник = %s
                """)
                cursor.execute(query, (f'{{{new_time_slot}}}', f'"{description}"', employee_num))

                connection.commit()
                close_connection(connection)
                print("Временной промежуток успешно обновлен")
                set_last_global_message("Временной промежуток успешно обновлен")
                self.close()
            except Exception as e:
                print_exception_info(e)
                close_connection(connection)

        self.confirm_button.clicked.connect(
            lambda: conf_butt(
                f"{{{self.start_timedit.text()} - {self.end_timedit.text()}}}",
                self.duty_textedit.toPlainText()
            )
        )

class DeleteTimeIntervalPopup(GraphManipulationPopup):
    def __init__(self, employee_fio: str, employee_role: str, table_widget: QTableWidget, selected_row: int):
        super().__init__()
        self.setWindowTitle("Удалить временной промежуток")
        self.confirm_button.setText("Удалить")
        
        # Сохраняем ссылку на таблицу и выбранную строку
        self.table_widget = table_widget
        self.selected_row = selected_row

        # Заполняем поля из выбранной строки таблицы
        if self.selected_row >= 0 and self.selected_row is not None:
            time_slot = self.table_widget.item(self.selected_row, 0).text()
            start_time, end_time = time_slot.split(" - ")
            self.start_timedit.setTime(QTime.fromString(start_time))
            self.end_timedit.setTime(QTime.fromString(end_time))
            self.duty_textedit.setEnabled(False)

        def delete_time_interval():
            connection = connect_to_db()
            try:
              
                cursor = connection.cursor()

                # Получаем номер сотрудника
                query = sql.SQL("""
                    SELECT номер_сотрудника FROM Сотрудники WHERE фио = %s AND роль = %s
                """)
                cursor.execute(query, (employee_fio, employee_role))
                result = cursor.fetchall()
                if not result:
                    print(f"Сотрудник с ФИО '{employee_fio}' и ролью '{employee_role}' не найден")
                    set_last_global_message(f"Сотрудник с ФИО '{employee_fio}' и ролью '{employee_role}' не найден")
                    return
                employee_num = result[0][0]

                # Временной промежуток из таблицы
                time_slot = self.table_widget.item(self.selected_row, 0).text().strip('{}')
                print(f"Удаляемый временной промежуток: '{time_slot}'")  # Отладка

                # Проверяем текущие данные в базе
                check_query = sql.SQL("""
                    SELECT временные_промежутки FROM Графики_работы WHERE сотрудник = %s
                """)
                cursor.execute(check_query, (employee_num,))
                current_intervals = cursor.fetchall()
                print(f"Текущие временные промежутки: {current_intervals}")  # Отладка

                # Удаляем ключ из jsonb
                query = sql.SQL("""
                    UPDATE Графики_работы
                    SET временные_промежутки = временные_промежутки - %s
                    WHERE сотрудник = %s
                """)
                cursor.execute(query, (time_slot, employee_num))

                # Проверяем, сколько строк обновлено
                if cursor.rowcount == 0:
                    print("Ни одна строка не обновлена. Возможно, сотрудник или ключ не найдены.")
                    set_last_global_message("Ни одна строка не обновлена. Возможно, сотрудник или ключ не найдены.")
                else:
                    print(f"Временной промежуток '{time_slot}' удален")
                    set_last_global_message(f"Временной промежуток '{time_slot}' удален")

                connection.commit()
                close_connection(connection)

                # Удаляем строку из таблицы в интерфейсе
                self.table_widget.removeRow(self.selected_row)
                self.close()

            except Exception as e:
                print_exception_info(e)
                connection.rollback()  # Откатываем изменения при ошибке
                close_connection(connection)

        self.confirm_button.clicked.connect(delete_time_interval)

class MainWindow(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.resize(1280,720+30)
        self.setWindowTitle("MVP Manik")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setScene(MainScene())
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setStyleSheet("""
                background-color: rgb(0,0,0);
                margin: 0px;
                border: none;
                """)

    def resizeEvent(self, event):
        self.fitInView(QRectF(-1,0,1920-10,1080-10+35),Qt.AspectRatioMode.IgnoreAspectRatio)

def set_current_relation_name(name:str):
    global current_relation_name
    current_relation_name = name

class MainScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0,0,1920,1080)
        self.staked_widget = QStackedWidget()
        self.staked_widget.setStyleSheet('background-color:darkgrey;')
        self.staked_widget.setGeometry(0, 0, 1920, 1080)
        self.addWidget(self.staked_widget)

        self.global_message = QLabel('Добро пожаловать!')
        self.global_message.setStyleSheet(f'{default_font_style()} background-color:gray; color:lightgray; ')
        self.global_message.setGeometry(0,1080,1920,30)
        self.addWidget(self.global_message)
        self.update_global_message_timer = QTimer()
        self.update_global_message_timer.timeout.connect(lambda: self.global_message.setText(last_global_message))
        self.update_global_message_timer.start(1000)

        self.graphic_view_widget = GraphViewWidget()
        self.graphic_view_widget.menu_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.menu_widget))
        def prof_pick():
            connection = connect_to_db()
            try:
                
                cursor = connection.cursor()
                query = sql.SQL("SELECT фио FROM Сотрудники WHERE роль = %s")
                cursor.execute(query, (self.graphic_view_widget.employee_combobox.currentText(),))
                fios=cursor.fetchall()
                self.graphic_view_widget.FIO.clear()
                for fio in fios:
                    self.graphic_view_widget.FIO.addItem(fio[0])
                close_connection(connection)
            except Exception as e:
                    print_exception_info(e)
                    close_connection(connection)
        self.graphic_view_widget.employee_combobox.activated.connect(lambda: prof_pick())
        self.graphic_view_widget.table_widget.setColumnCount(2)
        self.graphic_view_widget.table_widget.setHorizontalHeaderLabels(["Не найдено","Не найдено"])
        self.graphic_view_widget.table_widget.setColumnWidth(0,400)
        self.graphic_view_widget.table_widget.setColumnWidth(1,600)
        self.graphic_view_widget.check_box.hide()
        def graph_create_popup():
            graph_create_popupp = AddTimeIntervalPopup(self.graphic_view_widget.FIO.currentText(),self.graphic_view_widget.employee_combobox.currentText(),self.graphic_view_widget.calendar.selectedDate().toString())
        self.graphic_view_widget.create_button.clicked.connect(lambda :graph_create_popup())
        def graph_edit_popup():
            try:
                graph_create_popupp = EditTimeIntervalPopup(self.graphic_view_widget.FIO.currentText(),self.graphic_view_widget.employee_combobox.currentText(),self.graphic_view_widget.table_widget,self.graphic_view_widget.table_widget.selectedItems()[0].row())
            except Exception as e:
                    print_exception_info(e)
        def graph_delete_popup():
            try:
                graph_create_popupp = DeleteTimeIntervalPopup(self.graphic_view_widget.FIO.currentText(),self.graphic_view_widget.employee_combobox.currentText(),self.graphic_view_widget.table_widget,self.graphic_view_widget.table_widget.selectedItems()[0].row())
            except Exception as e:
                    print_exception_info(e)
        self.graphic_view_widget.edit_button.clicked.connect(lambda :graph_edit_popup())
        self.graphic_view_widget.delete_button.clicked.connect(lambda :graph_delete_popup())
        self.staked_widget.addWidget(self.graphic_view_widget)

        class ChangedRelativeViewWidget(RelativeViewWidget):
            def update_relation_data(self):
                super().update_relation_data()
                connection = connect_to_db()
                try:
                    if current_user_role != 'админ':
                        
                        cursor = connection.cursor()
                        query = sql.SQL("""
                            SELECT * FROM Регулирование_Отношений
                        """)
                        cursor.execute(query)
                        result = cursor.fetchall()
                        dict_result = {}
                        for res in result:
                            key = res[0]
                            values = list(res[1:])
                            dict_result[key]=values
                        self.create_button.setDisabled(True) if dict_result[current_relation_name][1] != 'все' else self.create_button.setDisabled(False)
                        self.edit_button.setDisabled(True) if dict_result[current_relation_name][2] != 'все' else self.edit_button.setDisabled(False)
                        self.delete_button.setDisabled(True) if dict_result[current_relation_name][3] != 'все' else self.delete_button.setDisabled(False)
                        try:
                            query = sql.SQL("""
                                SELECT * FROM {rela_name}
                            """).format(
                                rela_name = sql.Identifier(f'Регулирование_{current_relation_name}')
                            )
                            cursor.execute(query)
                            result = cursor.fetchall()
                            dict_result = {}
                            for res in result:
                                key = res[0]
                                values = list(res[1:])
                                dict_result[key]=values
                            col = 0
                            col_count = self.table_widget.columnCount()
                            while col < col_count:
                                col_name=self.table_widget.horizontalHeaderItem(col).text()
                                if dict_result[col_name][0] != 'все':
                                    self.table_widget.removeColumn(col)
                                    col_count-=1
                                else:
                                    col+=1                                
                        except Exception as e:
                            print(f"Отношения Регулирование_{current_relation_name} нет")
                        close_connection(connection)
                except Exception as e:
                    print_exception_info(e)
                    close_connection(connection)

        self.relative_view_widget = ChangedRelativeViewWidget()
        self.relative_view_widget.menu_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.menu_widget))
        def create_popup():
            create_popupp = AddRowPopup(self.relative_view_widget.table_widget)
            create_popupp.confirm_button.clicked.connect(lambda: self.relative_view_widget.update_relation_data())
        self.relative_view_widget.create_button.clicked.connect(lambda :create_popup())
        def edit_popup():
            edit_popupp = EditRowPopup(self.relative_view_widget.table_widget)
            edit_popupp.confirm_button.clicked.connect(lambda :self.relative_view_widget.update_relation_data())
        self.relative_view_widget.edit_button.clicked.connect(lambda: edit_popup())
        def del_popup():
            del_popup = DeleteRowPopup(self.relative_view_widget.table_widget)
            del_popup.confirm_button.clicked.connect(lambda :self.relative_view_widget.update_relation_data())
        self.relative_view_widget.delete_button.clicked.connect(lambda :del_popup())
        self.staked_widget.addWidget(self.relative_view_widget)

        self.menu_widget = MenuWidget()
        self.menu_widget.logout_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.start_widget))
        self.menu_widget.close_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.relative_view_widget))
        def set_abilities(create_button:QPushButton,edit_button:QPushButton,delete_button:QPushButton):
            connection = connect_to_db()
            try: 
                
                cursor = connection.cursor()
                query = sql.SQL("""
                    SELECT * FROM Регулирование_Отношений
                """)
                cursor.execute(query)
                rows = cursor.fetchall()
                result = {}
                for row in rows:
                    key = row[0]
                    values = list(row[1:])
                    result[key] = values
                if current_user_role != 'админ':
                    create_button.setDisabled(True) if result[current_relation_name][1] == 'админ' else create_button.setDisabled(False)
                    edit_button.setDisabled(True) if result[current_relation_name][2] == 'админ' else edit_button.setDisabled(False)     
                    delete_button.setDisabled(True) if result[current_relation_name][3] == 'админ' else delete_button.setDisabled(False)  
                close_connection(connection)
            except Exception as e:
                print_exception_info(e)
                close_connection(connection)
        for button in self.menu_widget.objects_scroll_area_widget.buttons:
            button.clicked.connect(lambda: set_abilities(self.relative_view_widget.create_button,self.relative_view_widget.edit_button,self.relative_view_widget.delete_button))
            button.clicked.connect(lambda :self.relative_view_widget.update_relation_data())
            button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.relative_view_widget))
        graph_view_button = QPushButton("Графики работы")
        graph_view_button.setStyleSheet(f"{default_button_style()}; text-align:left")
        self.menu_widget.objects_scroll_area_widget.container_layout.addWidget(graph_view_button)
        graph_view_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.graphic_view_widget))
        self.menu_widget.objects_scroll_area_widget.buttons.append(graph_view_button)
        self.staked_widget.addWidget(self.menu_widget)

        self.registration_widget = RegistrationWidget()
        def registrate_employee (FIO:str,login:str,password:str):
            if len(FIO) > 0 and len(login) > 0 and len(password) > 0:
                connection = connect_to_db()
                try:
                    
                    cursor = connection.cursor()
                    query = sql.SQL("""
                                INSERT INTO Сотрудники (фио, логин, пароль)
                                VALUES (%s, %s, %s)
                                RETURNING номер_сотрудника;
                            """)
                    cursor.execute(query, (FIO,login, password))
                    connection.commit()
                    close_connection(connection)
                    self.registration_widget.lastname_linedit.clear()
                    self.registration_widget.firstname_linedit.clear()
                    self.registration_widget.midlename_linedit.clear()
                    self.registration_widget.login_linedit.clear()
                    self.registration_widget.password_linedit.clear()
                    self.staked_widget.setCurrentWidget(self.start_widget)
                except Exception as e:
                    print_exception_info(e)
                    close_connection(connection)
            else:
                set_last_global_message("Что-то не введено")
                return print("Что-то не введено")
        self.registration_widget.registration_button.clicked.connect(lambda :
            registrate_employee(f"""{self.registration_widget.lastname_linedit.text()} {self.registration_widget.firstname_linedit.text()} {self.registration_widget.midlename_linedit.text()}""",self.registration_widget.login_linedit.text(),self.registration_widget.password_linedit.text()))
        self.registration_widget.back_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.start_widget))
        self.staked_widget.addWidget(self.registration_widget)

        self.start_widget = StartWidget()
        self.start_widget.registration_button.clicked.connect(lambda :self.staked_widget.setCurrentWidget(self.registration_widget))
        def privileges():
            connection = connect_to_db()
            try:
                
                cursor = connection.cursor()
                query = sql.SQL("""
                    SELECT * FROM Регулирование_Отношений
                """)
                cursor.execute(query)
                result = cursor.fetchall()
                relation_visibility = {}
                for res in result:
                    key = res[0]
                    values = list(res[1:])
                    relation_visibility[key] = values
                print(relation_visibility) 
                for button in self.menu_widget.objects_scroll_area_widget.buttons:
                    button_text = str(button.text()).replace('Отношение: ','')
                    if button_text in relation_visibility.keys():
                        if relation_visibility[button_text][0] == 'админ' and current_user_role != 'админ':
                            button.hide()
                        else:
                            button.show() 
                close_connection(connection)       
            except Exception as e:
                print_exception_info(e)
                close_connection(connection)
            
            
        def sign_in(login:str,password:str):
            if len(login) > 0 and len(password) > 0:
                connection = connect_to_db()
                try:
                    
                    cursor = connection.cursor()
                    query = sql.SQL("""
                                SELECT номер_сотрудника
                                FROM Сотрудники
                                WHERE логин = %s AND пароль = %s AND удален = FALSE AND статус = 'активен';
                            """)
                    cursor.execute(query, (login, password))
                    result = cursor.fetchone()
                    if result:
                        self.start_widget.login_linedit.clear()
                        self.start_widget.password_linedit.clear()
                        self.staked_widget.setCurrentWidget(self.menu_widget) 
                        query = sql.SQL("""
                        SELECT роль FROM Сотрудники WHERE логин = %s;
                        """)
                        global current_user_login, current_user_role
                        current_user_login = login
                        cursor.execute(query, (current_user_login,))
                        current_user_role = cursor.fetchone()[0]
                        print(current_user_login,current_user_role)
                        privileges()
                    else:
                        print("Возможно ошибка в пароле, логине, пользователь не зарегистрирован, пользователь не подтвержден")
                        set_last_global_message("Возможно ошибка в пароле, логине, пользователь не зарегистрирован, пользователь не подтвержден")
                    close_connection(connection)
                except Exception as e:
                    print_exception_info(e)
                    close_connection(connection)
            else:
                set_last_global_message("Что-то не введено")
                return print("Что-то не введено")
        self.start_widget.signin_button.clicked.connect(lambda :
            sign_in(self.start_widget.login_linedit.text(),self.start_widget.password_linedit.text()))            
        self.start_widget.exit_button.clicked.connect(lambda :sys.exit())

        
        self.staked_widget.addWidget(self.start_widget)

        self.staked_widget.setCurrentWidget(self.start_widget)

class UsualWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1920, 1080)
        self.main_layout = QVBoxLayout(self)

    def usualButton(self,name="",x=0,y=0,w=200,h=50):
        button = def_Button()
        button.setText(f"{name}")
        button.setGeometry(x,y,w,h)
        return button

    def usualLineEdit(self,place_holder_name="",x=0,y=0,w=200,h=50):
        field = def_LineEdit()
        field.setPlaceholderText(f"{place_holder_name}")
        field.setGeometry(x,y,w,h)
        return field

    def usualTableWidget(self,x=0,y=0,w=300,h=300):
        widget = def_TableWidget()
        widget.setGeometry(x,y,w,h)
        return widget

class StartWidget(UsualWidget):
    def __init__(self):
        super().__init__()
        self.signin_button = self.usualButton("Войти",1600,900,150,50)
        self.main_layout.addChildWidget(self.signin_button)
        self.exit_button = self.usualButton("Выйти",100,900,150,50)
        self.main_layout.addChildWidget(self.exit_button)
        self.registration_button = self.usualButton("Регистрация",1600,100,200,50)
        self.main_layout.addChildWidget(self.registration_button)

        self.login_linedit = self.usualLineEdit("Логин",100,300,400,30)
        self.main_layout.addChildWidget(self.login_linedit)
        self.password_linedit = self.usualLineEdit("Пароль",100,400,400,30)
        self.password_linedit.setEchoMode(QLineEdit.EchoMode.Password)
        self.main_layout.addChildWidget(self.password_linedit)



class RegistrationWidget(UsualWidget):
    def __init__(self):
        super().__init__()
        self.back_button = self.usualButton("Назад",100,900,200,50)
        self.main_layout.addChildWidget(self.back_button)
        self.registration_button = self.usualButton("Регистрация",1600,900,200,50)
        self.main_layout.addChildWidget(self.registration_button)

        self.lastname_linedit = self.usualLineEdit("Фамилия",100,300,300,30)
        self.main_layout.addChildWidget(self.lastname_linedit)
        self.firstname_linedit = self.usualLineEdit("Имя",405,300,300,30)
        self.main_layout.addChildWidget(self.firstname_linedit)
        self.midlename_linedit = self.usualLineEdit("Отчество",710,300,300,30)
        self.main_layout.addChildWidget(self.midlename_linedit)
        self.login_linedit = self.usualLineEdit("Логин",100,400,400,30)
        self.main_layout.addChildWidget(self.login_linedit)
        self.password_linedit = self.usualLineEdit("Пароль",100,500,400,30)
        self.password_linedit.setEchoMode(QLineEdit.EchoMode.Password)
        self.main_layout.addChildWidget(self.password_linedit)


class MenuWidget(UsualWidget):
    def __init__(self):
        super().__init__()

        self.close_button = self.usualButton("Закрыть",1600,50,200,50)
        self.main_layout.addChildWidget(self.close_button)
        self.logout_button = self.usualButton("Выйти из\nсистемы",1600,900,200,75)
        self.main_layout.addChildWidget(self.logout_button)

        self.search_linedit = self.usualLineEdit("Поиск",50,50,400,30)
        self.search_linedit.textChanged.connect(self.filter_buttons)
        self.main_layout.addChildWidget(self.search_linedit)

        self.objects_scroll_area_widget = ObjectsScrollAreaWidget()
        self.objects_scroll_area_widget.setGeometry(50, 100, 1500, 800)
        self.main_layout.addChildWidget(self.objects_scroll_area_widget)
    
    def filter_buttons(self):
        search_text = self.search_linedit.text().strip().lower()
        for button in self.objects_scroll_area_widget.buttons:
            button_text = button.text().lower()  
            if search_text in button_text:  
                button.show() 
            else:
                button.hide() 


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
        connection = connect_to_db()
        self.relation_names = []
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')")
            data = cursor.fetchall()
            self.relation_names = [str(name[0]) for name in data]
            close_connection(connection)
        except Exception as e:
           print_exception_info(e)
           close_connection(connection)

        self.buttons = []
        for i in range(len(self.relation_names)):
            button = QPushButton(f"Отношение: {self.relation_names[i]}",self)
            button.clicked.connect(lambda checked=False, idx=int(i):set_current_relation_name(f'{self.relation_names[idx]}'))
            button.setStyleSheet(f"{default_button_style()}; text-align:left")
            self.container_layout.addWidget(button)
            self.buttons.append(button)
    


class RelativeViewWidget(UsualWidget):
    def __init__(self):
        super().__init__()

        self.menu_button = self.usualButton("Меню",50,50,200,50)
        self.main_layout.addChildWidget(self.menu_button)
        self.create_button = self.usualButton("Создать",305,50,200,50)
        self.main_layout.addChildWidget(self.create_button)
        self.edit_button = self.usualButton("Изменить",510,50,210,50)
        self.main_layout.addChildWidget(self.edit_button)
        self.delete_button = self.usualButton("Удалить",725,50,200,50)
        self.main_layout.addChildWidget(self.delete_button)

        self.search_linedit = self.usualLineEdit("Поиск",1500,50,400,30)
        self.search_linedit.textChanged.connect(lambda:self.filter_table())
        self.main_layout.addChildWidget(self.search_linedit)

        self.curr_rel_name = QLabel(f"Отношение: {current_relation_name}",self)
        self.curr_rel_name.setGeometry(300,120,1500,30)
        self.curr_rel_name.setStyleSheet(default_font_style())
        self.main_layout.addChildWidget(self.curr_rel_name)

        self.table_widget = self.usualTableWidget(0,150,1900,930)
        self.main_layout.addChildWidget(self.table_widget)

    def update_relation_data(self):
        self.table_widget.clear()
        print(current_relation_name)
        self.print_relation_data(current_relation_name,self.table_widget)
        resize_columns_to_content(self.table_widget)
        self.curr_rel_name.setText(f"Отношение: {current_relation_name}")
        if current_user_role !='админ':
            col_id = -1
            for col in range(self.table_widget.columnCount()):
                if self.table_widget.horizontalHeaderItem(col).text() == 'удален':
                    col_id = col
                    break
                print(self.table_widget.horizontalHeaderItem(col).text())
            for row in range(self.table_widget.rowCount(),0,-1):
                deleted_item = False
                if self.table_widget.item(row,col_id) is not None:
                    deleted_item = self.table_widget.item(row,col_id).text()
                if bool(deleted_item) is True:
                    self.table_widget.removeRow(row)

    def print_relation_data(self, table_name:str,qtable:QTableWidget):
        connection = connect_to_db()
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
                    item = QTableWidgetItem(str(col_data))
                    qtable.setItem(row_index, col_index, item)
            qtable.sortByColumn(0,Qt.SortOrder.AscendingOrder)
        except Exception as e:
            print_exception_info(e)
            close_connection(connection)
             

    def filter_table(self):
        search_text = self.search_linedit.text().strip().lower()
        for row in range(self.table_widget.rowCount()):
            match = False
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table_widget.setRowHidden(row,not match)
    
class FixedComboBox(QComboBox):
    def showPopup(self):
        super().showPopup()
        popup = self.view()

        popup_rect = QRect(
            self.rect().x(),
            self.rect().bottom(),
            self.width(),
            popup.sizeHintForRow(0) * min(self.maxVisibleItems(), self.count())
        )
        global_pos = self.mapToGlobal(popup_rect.topLeft())
        popup.window().setGeometry(QRect(global_pos, popup_rect.size()))

class GraphViewWidget(UsualWidget):
    def __init__(self):
        super().__init__()
        self.menu_button = self.usualButton("Меню",50,50,200,50)
        self.main_layout.addChildWidget(self.menu_button)
        self.employee_combobox = FixedComboBox(self)
        self.employee_combobox.addItems(['мастер','оператор','админ'])
        self.employee_combobox.setGeometry(300,55,400,30)
        self.employee_combobox.setStyleSheet(default_font_style())
        self.main_layout.addChildWidget(self.employee_combobox)
        self.FIO = FixedComboBox(self)
        self.FIO.setEditable(True)
        self.FIO.setPlaceholderText("ФИО")
        self.FIO.setStyleSheet(default_font_style())
        self.FIO.setGeometry(705,55,400,30)
        self.main_layout.addChildWidget(self.FIO)
        self.create_button = self.usualButton("Создать",300,131,200,50)
        self.main_layout.addChildWidget(self.create_button)
        self.edit_button = self.usualButton("Изменить",501,131,200,50)
        self.main_layout.addChildWidget(self.edit_button)
        self.delete_button = self.usualButton("Удалить",702,131,200,50)
        self.main_layout.addChildWidget(self.delete_button)
        self.check_box = QCheckBox("явка")
        self.check_box.setFont(QFont("Arial",20))
        self.check_box.setGeometry(50,200,500,30)
        self.main_layout.addChildWidget(self.check_box)
        self.table_widget = self.usualTableWidget(0,230,1380,830)
        self.main_layout.addChildWidget(self.table_widget)
        self.calendar = QCalendarWidget(self)
        self.calendar.setStyleSheet(default_font_style())
        self.calendar.setGeometry(1401,200,519,880)
        self.main_layout.addChildWidget(self.calendar)

        self.employee_combobox.editTextChanged.connect(lambda:self.update_intervals(self.FIO.currentText(),self.employee_combobox.currentText()))
        self.FIO.editTextChanged.connect(lambda:self.update_intervals(self.FIO.currentText(),self.employee_combobox.currentText()))
        self.calendar.selectionChanged.connect(lambda:self.update_intervals(self.FIO.currentText(),self.employee_combobox.currentText()))

        def set_yavka():
            connection = connect_to_db()
            try:
                
                cursor = connection.cursor()
                query = sql.SQL("""
                SELECT номер_сотрудника FROM Сотрудники WHERE фио = {fio} AND роль = {role}
                """).format(
                    fio=sql.Literal(self.FIO.currentText()),
                    role=sql.Literal(self.employee_combobox.currentText())
                )
                cursor.execute(query)
                employee_num_ = cursor.fetchall()[0][0]
                
                query = sql.SQL("""
                    UPDATE Графики_работы
                    SET явка = {yavka_m}
                    WHERE сотрудник = {employee_num}
                    AND дата_начала::date <= {pick_date}::date
                    AND дата_конца::date >= {pick_date}::date
                    RETURNING *
                """).format(
                    yavka_m = sql.Literal(self.check_box.isChecked()),
                    employee_num = sql.Literal(employee_num_),
                    pick_date = sql.Literal(self.calendar.selectedDate().toString())
                )
                cursor.execute(query)
                connection.commit()
                close_connection(connection)
                print("Явка обновлена")
                set_last_global_message("Явка обновлена")
            except Exception as e:
                print_exception_info(e)
                close_connection(connection)
        self.check_box.checkStateChanged.connect(set_yavka)

        def set_FIOs_with_role():
            connection = connect_to_db()
            try:
                
                cursor = connection.cursor()
                query = sql.SQL("""
                    SELECT фио FROM Сотрудники WHERE роль = {}                
                """).format(
                    sql.Literal(self.employee_combobox.currentText())
                )
                cursor.execute(query)
                result = cursor.fetchall()[0]
                self.FIO.addItems(result)
                close_connection(connection)
                print("Сотрудники выставлены")
            except Exception as e:
                print_exception_info(e)
                close_connection(connection)
        self.employee_combobox.editTextChanged.connect(set_FIOs_with_role)

    def update_intervals(self,em_fio,em_role):
        connection = connect_to_db()
        try:
            
            cursor = connection.cursor()

            # Получаем номер_сотрудника
            query = sql.SQL("""
                SELECT номер_сотрудника FROM Сотрудники WHERE фио = {fio} AND роль = {role}
            """).format(
                fio=sql.Literal(em_fio),
                role=sql.Literal(em_role)
            )
            cursor.execute(query)
            employee_num_result = cursor.fetchall()

            if employee_num_result:
                

                employee_num = employee_num_result[0][0]
                print(f"Номер сотрудника: {employee_num}")

                # Получаем выбранную дату
                curr_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                print(f"Выбранная дата: {curr_date}")

                # Получаем явку и временные промежутки
                query = sql.SQL("""
                    SELECT явка, временные_промежутки
                    FROM Графики_работы
                    WHERE сотрудник = {employee_num}
                    AND дата_начала::date <= {pick_date}::date
                    AND дата_конца::date >= {pick_date}::date
                """).format(
                    employee_num=sql.Literal(employee_num),
                    pick_date=sql.Literal(curr_date)  # Не добавляем лишние кавычки
                )

                cursor.execute(query)
                result = cursor.fetchone()
                close_connection(connection)
                if result:
                    yavka = bool(result[0])  # Преобразуем явку в bool
                    time_intervals = result[1]  # Получаем временные промежутки

                    # Преобразуем time_intervals в словарь, если это строка
                    if isinstance(time_intervals, str):
                        try:
                            temp_dict = ast.literal_eval(time_intervals)  # Парсим как Python-словарь
                            time_intervals = json.dumps(temp_dict)  # Преобразуем в JSON-строку
                            time_intervals = json.loads(time_intervals)  # Парсим обратно в словарь
                        except (ValueError, SyntaxError) as e:
                            print(f"Ошибка при парсинге строки: {e}")
                            time_intervals = {}
                    elif not isinstance(time_intervals, dict):
                        print("time_intervals не является словарем или строкой.")
                        time_intervals = {}  # Если это не словарь и не строка, используем пустой словарь

                    # Устанавливаем значение чекбокса
                    self.check_box.setChecked(yavka)
                    self.check_box.show()

                    # Очищаем таблицу и заполняем ее данными
                    self.table_widget.setRowCount(0)  # Очищаем все строки
                    self.table_widget.setColumnCount(2)  # Устанавливаем два столбца
                    self.table_widget.setHorizontalHeaderLabels(["Временной промежуток", "Описание"])

                    for row, (time_slot, description) in enumerate(time_intervals.items()):
                        self.table_widget.insertRow(row)
                        self.table_widget.setItem(row, 0, QTableWidgetItem(time_slot))
                        self.table_widget.setItem(row, 1, QTableWidgetItem(description))
                else:
                    print(f"Данные для сотрудника {employee_num} на дату {curr_date} не найдены.")
                    set_last_global_message(f"Данные для сотрудника {employee_num} на дату {curr_date} не найдены.")
                    self.table_widget.setRowCount(0)
                    self.table_widget.setColumnCount(2)
                    self.check_box.hide()
                    self.table_widget.setHorizontalHeaderLabels(["Не найдено", "Не найдено"])
            else:
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(2)
                self.check_box.hide()
                self.table_widget.setHorizontalHeaderLabels(["Не найдено", "Не найдено"])
                print(f"Сотрудник с ФИО '{em_fio}' и ролью '{em_role}' не найден.")
                set_last_global_message(f"Сотрудник с ФИО '{em_fio}' и ролью '{em_role}' не найден.")
                close_connection(connection)
                return

        except Exception as e:
            print_exception_info(e)
            close_connection(connection)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    current_relation_name = 'no'
    current_user_login = None
    current_user_role = None
    last_global_message = 'сообщений нет'
    print(current_user_login,current_user_role)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())