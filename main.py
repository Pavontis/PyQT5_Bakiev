import sys
import sqlite3  # Модуль для работы с базой данных SQLite
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QDateEdit, QMessageBox, QLabel, QInputDialog
)
from PyQt5.QtCore import QDate  # Импорт класса для работы с датами в PyQt6
import matplotlib.pyplot as plt  # Импорт библиотеки для построения графиков


class FinanceApp(QMainWindow):  # Основной класс приложения
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учет финансов")  # Установка заголовка окна
        self.setGeometry(100, 100, 800, 600)  # Установка размера и положения окна

        # Основной виджет и компоновка
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()

        # Поле выбора: тип транзакции (Расходы или Доходы)
        self.transaction_type = QComboBox(self)
        self.transaction_type.addItems(["Расходы", "Доходы"])  # Добавление вариантов
        self.transaction_type.currentTextChanged.connect(self.update_categories)
        self.layout.addWidget(QLabel("Выберите тип транзакции:"))  # Заголовок
        self.layout.addWidget(self.transaction_type)  # Виджет выбора типа транзакции

        # Поле выбора категории
        self.category_input = QComboBox(self)
        self.category_input.currentTextChanged.connect(self.toggle_custom_category_input)
        self.layout.addWidget(QLabel("Категория:"))  # Заголовок
        self.layout.addWidget(self.category_input)  # Виджет выбора категории

        # Поле для добавления пользовательской категории
        self.custom_category_input = QLineEdit(self)
        self.custom_category_input.setPlaceholderText(
            "Введите свою категорию (только для 'Прочее')"
        )  # Подсказка для ввода
        self.custom_category_input.setEnabled(False)  # Отключено по умолчанию
        self.layout.addWidget(self.custom_category_input)

        # Поле ввода суммы
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Введите сумму (например, 1000)")  # Подсказка
        self.layout.addWidget(QLabel("Сумма:"))  # Заголовок
        self.layout.addWidget(self.amount_input)

        # Поле ввода описания транзакции
        self.description_input = QLineEdit(self)
        self.description_input.setPlaceholderText("Введите описание (например, обед)")  # Подсказка
        self.layout.addWidget(QLabel("Описание:"))  # Заголовок
        self.layout.addWidget(self.description_input)

        # Поле выбора даты
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)  # Включение календаря
        self.date_input.setDate(QDate.currentDate())  # Установка текущей даты
        self.layout.addWidget(QLabel("Дата:"))  # Заголовок
        self.layout.addWidget(self.date_input)

        # Кнопка для добавления записи
        self.add_button = QPushButton("Добавить запись", self)
        self.add_button.clicked.connect(self.add_record)  # Привязка к методу
        self.layout.addWidget(self.add_button)

        # Кнопка для очистки полей ввода
        self.clear_button = QPushButton("Очистить поля", self)
        self.clear_button.clicked.connect(self.clear_fields)  # Привязка к методу
        self.layout.addWidget(self.clear_button)

        # Кнопка для удаления записи
        self.delete_button = QPushButton("Удалить запись", self)
        self.delete_button.clicked.connect(self.delete_record)  # Привязка к методу
        self.layout.addWidget(self.delete_button)

        # Кнопка для визуализации данных
        self.visualize_button = QPushButton("Визуализировать данные", self)
        self.visualize_button.clicked.connect(self.visualize_data)  # Привязка к методу
        self.layout.addWidget(self.visualize_button)

        # Таблица для отображения данных
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)  # Установка количества столбцов
        self.table.setHorizontalHeaderLabels(
            ["Тип", "Сумма", "Категория", "Описание", "Дата"]
        )  # Заголовки столбцов
        self.layout.addWidget(self.table)

        # Подключение основного виджета
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

        # Подключение к базе данных
        self.conn = sqlite3.connect("finance.db")  # Создание/подключение базы данных
        self.cursor = self.conn.cursor()  # Создание курсора для выполнения запросов
        self.create_table()  # Создание таблицы, если она отсутствует
        self.update_table_structure()  # Обновление структуры таблицы
        self.load_data()  # Загрузка данных из базы

        # Обновление категорий в зависимости от типа транзакции
        self.update_categories()

    def create_table(self):
        """Создание таблицы в базе данных."""
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS finance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                amount REAL,
                category TEXT,
                description TEXT,
                date TEXT
            )"""
        )
        self.conn.commit()

    def update_table_structure(self):
        """Обновление структуры таблицы."""
        self.cursor.execute("PRAGMA table_info(finance)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if "type" not in columns:
            self.cursor.execute("ALTER TABLE finance ADD COLUMN type TEXT")
            self.conn.commit()

    def load_data(self):
        """Загрузка данных из базы данных."""
        self.cursor.execute(
            "SELECT type, amount, category, description, date FROM finance"
        )
        records = self.cursor.fetchall()

        self.table.setRowCount(len(records))
        for row_index, row_data in enumerate(records):
            for col_index, col_data in enumerate(row_data):
                self.table.setItem(
                    row_index, col_index, QTableWidgetItem(str(col_data))
                )

        self.enable_sorting()

    def enable_sorting(self):
        """Включение сортировки таблицы по столбцам."""
        self.table.setSortingEnabled(True)

    def toggle_custom_category_input(self):
        """Включение или отключение ввода пользовательской категории."""
        if self.category_input.currentText() == "Прочее":
            self.custom_category_input.setEnabled(True)
        else:
            self.custom_category_input.setEnabled(False)
            self.custom_category_input.clear()

    def add_record(self):
        """Добавление новой записи в базу данных."""
        try:
            transaction_type = self.transaction_type.currentText()
            amount_text = self.amount_input.text().strip()
            if not amount_text:
                QMessageBox.warning(self, "Ошибка", "Поле суммы не может быть пустым!")
                return
            amount = float(amount_text)

            category = self.category_input.currentText()
            if category == "Прочее":
                custom_category = self.custom_category_input.text().strip()
                if not custom_category:
                    QMessageBox.warning(
                        self, "Ошибка", "Введите свою категорию для 'Прочее'!"
                    )
                    return
                category = custom_category

            description = self.description_input.text().strip()
            if not description:
                description = "Без описания"

            date = self.date_input.date().toString("yyyy-MM-dd")

            self.cursor.execute(
                "INSERT INTO finance (type, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                (transaction_type, amount, category, description, date),
            )
            self.conn.commit()
            self.load_data()

            QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
            self.clear_fields()

        except ValueError as e:
            QMessageBox.warning(
                self, "Ошибка", f"Сумма должна быть числом! Ошибка: {e}"
            )
        except sqlite3.Error as e:
            QMessageBox.critical(
                self, "Ошибка базы данных", f"Не удалось добавить запись: {e}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", f"Произошла ошибка: {e}")

    def clear_fields(self):
        """Очистка всех полей ввода."""
        self.amount_input.clear()
        self.description_input.clear()
        self.custom_category_input.clear()
        self.date_input.setDate(QDate.currentDate())

    def delete_record(self):
        """Удаление выбранной записи из базы данных."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        try:
            transaction_type = self.table.item(selected_row, 0).text()
            amount = float(self.table.item(selected_row, 1).text())
            category = self.table.item(selected_row, 2).text()
            description = self.table.item(selected_row, 3).text()
            date = self.table.item(selected_row, 4).text()

            self.cursor.execute(
                "DELETE FROM finance WHERE type = ? AND amount = ? AND category = ? AND description = ? AND date = ?",
                (transaction_type, amount, category, description, date),
            )
            self.conn.commit()
            self.load_data()

            QMessageBox.information(self, "Успех", "Запись успешно удалена!")

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Некорректные данные в строке: {e}")
        except sqlite3.Error as e:
            QMessageBox.critical(
                self, "Ошибка базы данных", f"Ошибка при выполнении запроса: {e}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", f"Произошла ошибка: {e}")

    def update_categories(self):
        """Обновление списка категорий в зависимости от типа транзакции."""
        transaction_type = self.transaction_type.currentText()
        self.category_input.clear()
        if transaction_type == "Расходы":
            self.category_input.addItems(
                [
                    "Кафе и рестораны",
                    "Развлечения",
                    "Образование",
                    "Подписки",
                    "Госплатежи и налоги",
                    "Супермаркеты",
                    "АЗС",
                    "Переводы людям",
                    "Прочее",
                ]
            )
        elif transaction_type == "Доходы":
            self.category_input.addItems(
                ["Зарплата", "Стипендия", "Проценты по банковскому вкладу", "Прочее"]
            )

    def visualize_data(self):
        """Выбор графика для визуализации."""
        choice, ok = QInputDialog.getItem(
            self,
            "Выбор графика",
            "Выберите график для визуализации:",
            [
                "Круговая диаграмма расходов по категориям",
                "Круговая диаграмма доходов по категориям",
                "График доходов и расходов по датам",
                "Сравнение доходов и расходов",
                "Показать все графики",
            ],
            editable=False,
        )

        if not ok or not choice:
            return

        if choice == "Круговая диаграмма расходов по категориям":
            self.plot_expenses_by_category()
        elif choice == "Круговая диаграмма доходов по категориям":
            self.plot_income_by_category()
        elif choice == "График доходов и расходов по датам":
            self.plot_income_expenses_by_date()
        elif choice == "Сравнение доходов и расходов":
            self.plot_income_vs_expenses()
        elif choice == "Показать все графики":
            self.plot_all_graphs()

    def plot_expenses_by_category(self):
        """Круговая диаграмма расходов по категориям."""
        self.cursor.execute(
            "SELECT category, SUM(amount) FROM finance WHERE type = 'Расходы' GROUP BY category"
        )
        data = self.cursor.fetchall()

        if not data:
            QMessageBox.warning(
                self, "Нет данных", "Нет данных для отображения расходов."
            )
            return

        categories, amounts = zip(*data)

        plt.figure(figsize=(6, 6))
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
        plt.title("Расходы по категориям")
        plt.show()

    def plot_income_by_category(self):
        """Круговая диаграмма доходов по категориям."""
        self.cursor.execute(
            "SELECT category, SUM(amount) FROM finance WHERE type = 'Доходы' GROUP BY category"
        )
        data = self.cursor.fetchall()

        if not data:
            QMessageBox.warning(
                self, "Нет данных", "Нет данных для отображения доходов."
            )
            return

        categories, amounts = zip(*data)

        plt.figure(figsize=(6, 6))
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
        plt.title("Доходы по категориям")
        plt.show()

    def plot_income_expenses_by_date(self):
        """График доходов и расходов по датам."""
        self.cursor.execute(
            "SELECT date, SUM(amount) FROM finance WHERE type = 'Доходы' GROUP BY date"
        )
        income_data = self.cursor.fetchall()

        self.cursor.execute(
            "SELECT date, SUM(amount) FROM finance WHERE type = 'Расходы' GROUP BY date"
        )
        expense_data = self.cursor.fetchall()

        if not income_data and not expense_data:
            QMessageBox.warning(
                self,
                "Нет данных",
                "Нет данных для отображения доходов и расходов по датам.",
            )
            return

        all_dates = sorted(set(date for date, _ in income_data + expense_data))
        income_dict = dict(income_data)
        expense_dict = dict(expense_data)

        income_values = [income_dict.get(date, 0) for date in all_dates]
        expense_values = [expense_dict.get(date, 0) for date in all_dates]

        plt.figure(figsize=(10, 6))
        plt.plot(
            all_dates,
            income_values,
            label="Доходы",
            marker="o",
            linestyle="-",
            color="green",
        )
        plt.plot(
            all_dates,
            expense_values,
            label="Расходы",
            marker="o",
            linestyle="-",
            color="red",
        )
        plt.title("Доходы и Расходы по датам")
        plt.xlabel("Дата")
        plt.ylabel("Сумма")
        plt.legend()
        plt.grid()
        plt.show()

    def plot_income_vs_expenses(self):
        """Сравнение доходов и расходов."""
        self.cursor.execute("SELECT SUM(amount) FROM finance WHERE type = 'Доходы'")
        income = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT SUM(amount) FROM finance WHERE type = 'Расходы'")
        expenses = self.cursor.fetchone()[0] or 0

        labels = ["Доходы", "Расходы"]
        values = [income, expenses]

        plt.figure(figsize=(6, 6))
        plt.bar(labels, values, color=["green", "red"])
        plt.title("Сравнение доходов и расходов")
        plt.ylabel("Сумма")
        plt.show()

    def plot_all_graphs(self):
        """Отображение всех графиков."""
        self.plot_expenses_by_category()
        self.plot_income_by_category()
        self.plot_income_expenses_by_date()
        self.plot_income_vs_expenses()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceApp()
    window.show()
    sys.exit(app.exec())
