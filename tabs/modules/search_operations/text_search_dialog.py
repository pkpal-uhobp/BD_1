from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QTextEdit, QCheckBox,
    QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPalette, QColor
from plyer import notification
import re


class TextSearchDialog(QDialog):
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("Поиск по тексту")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1200, 900)
        self.resize(900, 700)  # Устанавливаем начальный размер
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Словари для валидации
        self.input_widgets = {}
        self.error_labels = {}
        self.field_validity = {}
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Создаем интерфейс
        self.setup_ui()
        self.apply_styles()
        
    def set_dark_palette(self):
        """Устанавливает тёмную цветовую палитру"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.ToolTipText, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(40, 40, 50))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.BrightText, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(18, 18, 24))
        self.setPalette(dark_palette)
        
    def setup_ui(self):
        """Создает пользовательский интерфейс"""
        
        # Заголовок
        header_label = QLabel("ПОИСК ПО ТЕКСТУ")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(header_label)
        
        # Группа настроек поиска
        search_group = QGroupBox("Настройки поиска")
        search_group.setObjectName("searchGroup")
        search_layout = QFormLayout()
        search_group.setLayout(search_layout)
        
        # Выбор таблицы
        self.table_combo = QComboBox()
        self.table_combo.setObjectName("tableCombo")
        search_layout.addRow("Таблица:", self.table_combo)
        
        # Выбор столбца
        self.column_combo = QComboBox()
        self.column_combo.setObjectName("columnCombo")
        search_layout.addRow("Столбец:", self.column_combo)
        
        # Подключаем обработчики изменения таблицы и столбца
        self.table_combo.currentTextChanged.connect(self.populate_columns)
        self.column_combo.currentTextChanged.connect(self.on_column_changed)
        
        # Тип поиска
        self.search_type_combo = QComboBox()
        self.search_type_combo.setObjectName("searchTypeCombo")
        self.search_type_combo.addItems([
            "LIKE - Шаблонный поиск (универсальный)",
            "~ - POSIX регулярное выражение (чувствительное к регистру)",
            "~* - POSIX регулярное выражение (нечувствительное к регистру)",
            "!~ - НЕ соответствует POSIX регулярному выражению (чувствительное к регистру)",
            "!~* - НЕ соответствует POSIX регулярному выражению (нечувствительное к регистру)"
        ])
        search_layout.addRow("Тип поиска:", self.search_type_combo)
        
        # Поле поиска с валидацией
        search_container = QWidget()
        search_container.setMinimumHeight(50)  # Устанавливаем минимальную высоту
        search_input_layout = QVBoxLayout(search_container)
        search_input_layout.setContentsMargins(0, 0, 0, 0)
        search_input_layout.setSpacing(5)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.setMinimumHeight(35)  # Устанавливаем минимальную высоту для поля
        search_input_layout.addWidget(self.search_input)
        
        # Метка ошибок для поискового запроса
        self.search_error = QLabel()
        self.search_error.setProperty("class", "error-label")
        self.search_error.hide()
        search_input_layout.addWidget(self.search_error)
        
        search_layout.addRow("Поисковый запрос:", search_container)
        
        # Регистрируем виджеты для валидации
        self.input_widgets['search'] = self.search_input
        self.error_labels['search'] = self.search_error
        self.field_validity['search'] = True
        
        # Валидация в реальном времени
        self.search_input.textChanged.connect(self._validate_search_query)
        
        # Чекбокс для учета регистра (только для LIKE)
        self.case_sensitive_check = QCheckBox("Учитывать регистр")
        self.case_sensitive_check.setObjectName("caseSensitiveCheck")
        self.case_sensitive_check.setChecked(False)
        search_layout.addRow("", self.case_sensitive_check)
        
        # Информационная метка о типе данных столбца
        self.column_type_label = QLabel("")
        self.column_type_label.setObjectName("columnTypeLabel")
        self.column_type_label.setWordWrap(True)
        search_layout.addRow("Тип данных:", self.column_type_label)
        
        # Информационная подсказка
        info_label = QLabel("Универсальный поиск: работает со всеми типами данных (строки, числа, даты, boolean, enum, array, json)")
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        search_layout.addRow("", info_label)
        
        # Подключаем обработчик изменения типа поиска
        self.search_type_combo.currentTextChanged.connect(self.on_search_type_changed)
        
        self.layout().addWidget(search_group)
        
        # Группа результатов
        results_group = QGroupBox("Результаты поиска")
        results_group.setObjectName("resultsGroup")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        # Область для отображения результатов
        self.results_text = QTextEdit()
        self.results_text.setObjectName("resultsText")
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Результаты поиска будут отображены здесь...")
        results_layout.addWidget(self.results_text)
        
        self.layout().addWidget(results_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.search_button = QPushButton("Найти")
        self.search_button.setObjectName("searchButton")
        self.search_button.clicked.connect(self.perform_search)
        
        self.clear_button = QPushButton("🗑 Очистить")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.clicked.connect(self.clear_results)
        
        self.close_button = QPushButton("Закрыть")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.search_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        
        self.layout().addLayout(buttons_layout)
        
        # Заполняем таблицы после создания всех виджетов
        self.populate_tables()
        
    def populate_tables(self):
        """Заполняет список таблиц"""
        try:
            if not self.db_instance or not self.db_instance.is_connected():
                return
                
            tables = self.db_instance.get_tables()
            self.table_combo.clear()
            self.table_combo.addItems(tables)
            
            # Заполняем столбцы для первой таблицы
            if tables:
                self.populate_columns(tables[0])
                
        except Exception as e:
            self.show_error(f"Ошибка при получении списка таблиц: {e}")
            
    def populate_columns(self, table_name):
        """Заполняет список столбцов для выбранной таблицы"""
        try:
            if not table_name or not self.db_instance or not self.db_instance.is_connected():
                self.column_combo.clear()
                return
                
            columns = self.db_instance.get_table_columns(table_name)
            self.column_combo.clear()
            
            # Отладочная информация
            print(f"Найдено столбцов в таблице '{table_name}': {len(columns)}")
            print(f"Столбцы: {columns}")
            
            # Показываем ВСЕ столбцы для поиска (убираем фильтрацию)
            print(f"Все столбцы таблицы '{table_name}': {columns}")
            
            # Добавляем все столбцы без фильтрации
            self.column_combo.addItems(columns)
            print(f"Добавлено {len(columns)} столбцов в combobox")
            
            # Обновляем информацию о типе данных для первого столбца
            if columns:
                self.on_column_changed(columns[0])
            
        except Exception as e:
            self.show_error(f"Ошибка при получении столбцов: {e}")
    
    def on_column_changed(self, column_name):
        """Обработчик изменения столбца - показывает тип данных"""
        try:
            if not column_name or not self.db_instance or not self.db_instance.is_connected():
                self.column_type_label.setText("")
                return
                
            table_name = self.table_combo.currentText()
            if not table_name:
                self.column_type_label.setText("")
                return
                
            # Получаем информацию о типе данных столбца
            try:
                # Сначала пробуем через SQLAlchemy ORM
                try:
                    table = self.db_instance.tables.get(table_name)
                    if table and hasattr(table.c, column_name):
                        column = getattr(table.c, column_name)
                        column_type = str(column.type).upper()
                        
                        # Определяем, является ли столбец числовым
                        is_numeric = any(num_type in column_type for num_type in ['INTEGER', 'BIGINT', 'SMALLINT', 'NUMERIC', 'DECIMAL', 'FLOAT', 'REAL', 'DOUBLE'])
                        
                        if is_numeric:
                            self.column_type_label.setText(f"Числовой ({column_type}) - универсальный поиск")
                        else:
                            self.column_type_label.setText(f"Текстовый ({column_type}) - универсальный поиск")
                        return
                except:
                    pass
                
                # Если не получилось через ORM, пробуем SQL запрос
                sql_query = f"""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = '{column_name}'
                """
                
                with self.db_instance.engine.connect() as conn:
                    result = conn.execute(sql_query)
                    row = result.fetchone()
                    
                    if row:
                        column_type = row[0].upper()
                        
                        # Определяем, является ли столбец числовым
                        is_numeric = any(num_type in column_type for num_type in ['INTEGER', 'BIGINT', 'SMALLINT', 'NUMERIC', 'DECIMAL', 'FLOAT', 'REAL', 'DOUBLE'])
                        
                        if is_numeric:
                            self.column_type_label.setText(f"Числовой ({column_type}) - универсальный поиск")
                        else:
                            self.column_type_label.setText(f"Текстовый ({column_type}) - универсальный поиск")
                    else:
                        self.column_type_label.setText("Столбец не найден")
            except Exception as e:
                # Если ничего не работает, показываем общую информацию
                self.column_type_label.setText("Универсальный поиск - работает с любыми типами данных")
                
        except Exception as e:
            self.column_type_label.setText(f"Ошибка: {e}")
            
    def on_search_type_changed(self, search_type):
        """Обработчик изменения типа поиска"""
        # Показываем/скрываем чекбокс учета регистра в зависимости от типа поиска
        if "LIKE" in search_type:
            self.case_sensitive_check.setVisible(True)
        else:
            self.case_sensitive_check.setVisible(False)
            
    def _validate_search_query(self):
        """Валидация поискового запроса в реальном времени"""
        search_query = self.search_input.text().strip()
        
        # Если поле пустое, не показываем ошибку, просто очищаем
        if not search_query:
            self.clear_field_error('search')
            return False
        
        # Проверяем длину запроса
        if len(search_query) < 1:
            self.set_field_error('search', "Поисковый запрос должен содержать хотя бы 1 символ")
            return False
        
        if len(search_query) > 1000:
            self.set_field_error('search', "Поисковый запрос не должен превышать 1000 символов")
            return False
        
        # Проверяем на специальные символы для регулярных выражений
        search_type = self.search_type_combo.currentText()
        if "LIKE" not in search_type:
            # Для регулярных выражений проверяем корректность
            try:
                import re
                re.compile(search_query)
            except re.error as e:
                self.set_field_error('search', f"Некорректное регулярное выражение: {str(e)}")
                return False
        
        # Если все проверки пройдены
        self.set_field_success('search', "✅ Поисковый запрос корректен")
        return True
    
    def set_field_error(self, field_name, error_message):
        """Устанавливает ошибку для поля"""
        if field_name in self.error_labels:
            if error_message:
                self.error_labels[field_name].setText(error_message)
                self.error_labels[field_name].setProperty("class", "error-label")
                self.error_labels[field_name].setStyleSheet("""
                    QLabel {
                        color: #ff6b6b;
                        font-size: 12px;
                        font-weight: bold;
                        font-family: 'Consolas', 'Fira Code', monospace;
                        margin-top: 5px;
                        padding: 5px 8px;
                        background: rgba(255, 107, 107, 0.1);
                        border-radius: 4px;
                        border-left: 3px solid #ff6b6b;
                    }
                """)
                self.error_labels[field_name].show()
                self.field_validity[field_name] = False
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "error")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)
    
    def set_field_success(self, field_name, success_message):
        """Устанавливает успешное состояние для поля"""
        if field_name in self.error_labels:
            if success_message:
                self.error_labels[field_name].setText(success_message)
                self.error_labels[field_name].setProperty("class", "success-label")
                self.error_labels[field_name].setStyleSheet("""
                    QLabel {
                        color: #50fa7b;
                        font-size: 12px;
                        font-weight: bold;
                        font-family: 'Consolas', 'Fira Code', monospace;
                        margin-top: 5px;
                        padding: 5px 8px;
                        background: rgba(80, 250, 123, 0.1);
                        border-radius: 4px;
                        border-left: 3px solid #50fa7b;
                    }
                """)
                self.error_labels[field_name].show()
                self.field_validity[field_name] = True
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "success")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)
    
    def clear_field_error(self, field_name):
        """Очищает ошибку для поля"""
        if field_name in self.error_labels:
            self.error_labels[field_name].hide()
            self.error_labels[field_name].setStyleSheet("")  # Очищаем стили метки
            self.field_validity[field_name] = True
            widget = self.input_widgets[field_name]
            widget.setProperty("class", "")
            widget.setStyleSheet(self.styleSheet())

    def perform_search(self):
        """Выполняет поиск"""
        try:
            # Получаем параметры поиска
            table_name = self.table_combo.currentText()
            column_name = self.column_combo.currentText()
            search_query = self.search_input.text().strip()
            search_type_full = self.search_type_combo.currentText()
            
            # Извлекаем только код типа поиска из полного описания
            search_type = self.extract_search_type_code(search_type_full)
            
            # Отладочная информация
            print(f"Параметры поиска:")
            print(f"   Таблица: {table_name}")
            print(f"   Столбец: {column_name}")
            print(f"   Запрос: {search_query}")
            print(f"   Тип поиска (полный): {search_type_full}")
            print(f"   Тип поиска (код): {search_type}")
            print(f"   Учитывать регистр: {self.case_sensitive_check.isChecked()}")
            
            # Валидация
            if not table_name:
                self.show_error("Выберите таблицу")
                return
                
            if not column_name:
                self.show_error("Выберите столбец")
                return
            
            # Проверяем валидность поискового запроса
            if not self._validate_search_query():
                return
                
            if not search_query:
                self.show_error("Введите поисковый запрос")
                return
                
            # Выполняем универсальный поиск с учетом типа поиска
            results = self.db_instance.text_search(
                table_name=table_name,
                column_name=column_name,
                search_query=search_query,
                search_type=search_type,
                case_sensitive=self.case_sensitive_check.isChecked()
            )
            
            # Отладочная информация о результатах
            print(f"Результаты поиска: найдено {len(results)} строк")
            if results:
                print(f"   Первая строка: {results[0]}")
            
            # Отображаем результаты
            self.display_results(results, table_name, column_name, search_query)
            
        except Exception as e:
            self.show_error(f"Ошибка при выполнении поиска: {e}")
    
    def extract_search_type_code(self, search_type_full):
        """Извлекает код типа поиска из полного описания"""
        if "LIKE" in search_type_full:
            return "LIKE"
        elif "!~*" in search_type_full:
            return "NOT_IREGEX"
        elif "~*" in search_type_full:
            return "IREGEX"
        elif "!~" in search_type_full:
            return "NOT_REGEX"
        elif "~" in search_type_full:
            return "REGEX"
        else:
            return "LIKE"  # По умолчанию
            
    def display_results(self, results, table_name, column_name, search_query):
        """Отображает результаты поиска"""
        if not results:
            self.results_text.setHtml("<p style='color: #ff6b6b;'>Поиск не дал результатов</p>")
            return
            
        # Формируем HTML для отображения результатов
        html = f"""
        <div style='color: #64ffda; font-weight: bold; margin-bottom: 10px;'>
            Результаты поиска в таблице "{table_name}" по столбцу "{column_name}"
        </div>
        <div style='color: #8892b0; margin-bottom: 15px;'>
            Поисковый запрос: <span style='color: #f8f8f2;'>{search_query}</span>
        </div>
        <div style='color: #50fa7b; margin-bottom: 10px;'>
            Найдено записей: {len(results)}
        </div>
        <hr style='border: 1px solid #44475a; margin: 15px 0;'>
        """
        
        # Добавляем результаты
        for i, result in enumerate(results, 1):
            html += f"""
            <div style='background: rgba(25, 25, 35, 0.8); padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #64ffda;'>
                <div style='color: #64ffda; font-weight: bold;'>Запись #{i}</div>
            """
            
            for key, value in result.items():
                # Подсвечиваем найденный текст
                if key == column_name and value:
                    highlighted_value = self.highlight_search_text(str(value), search_query)
                    html += f"<div style='margin: 5px 0;'><span style='color: #8892b0;'>{key}:</span> <span style='color: #f8f8f2;'>{highlighted_value}</span></div>"
                else:
                    html += f"<div style='margin: 5px 0;'><span style='color: #8892b0;'>{key}:</span> <span style='color: #f8f8f2;'>{value}</span></div>"
                    
            html += "</div>"
            
        self.results_text.setHtml(html)
        
    def highlight_search_text(self, text, search_query):
        """Подсвечивает найденный текст"""
        try:
            # Экранируем HTML символы
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            search_query = search_query.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Простое выделение (для LIKE поиска)
            if "LIKE" in self.search_type_combo.currentText():
                # Заменяем % на .* для регулярного выражения
                pattern = search_query.replace('%', '.*').replace('_', '.')
                highlighted = re.sub(f'({pattern})', r'<span style="background: #ffd700; color: #000;">\1</span>', text, flags=re.IGNORECASE)
            else:
                # Для регулярных выражений
                highlighted = re.sub(f'({search_query})', r'<span style="background: #ffd700; color: #000;">\1</span>', text, flags=re.IGNORECASE)
                
            return highlighted
        except:
            return text
            
    def clear_results(self):
        """Очищает результаты поиска"""
        self.results_text.clear()
        self.search_input.clear()
        # Очищаем валидацию
        self.clear_field_error('search')
    
    def show_error(self, message):
        """Показывает сообщение об ошибке"""
        self.results_text.setHtml(f"<p style='color: #ff6b6b;'>{message}</p>")
        
    def apply_styles(self):
        """Применяет стили"""
        self.setStyleSheet("""
            /* Основной диалог */
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
                border: 2px solid #44475a;
                border-radius: 10px;
            }
            
            /* Заголовок */
            #headerLabel {
                font-size: 20px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 15px;
                background: rgba(10, 10, 15, 0.7);
                border-radius: 8px;
                border: 1px solid #64ffda;
            }
            
            /* Группы */
            #searchGroup, #resultsGroup {
                font-size: 14px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                border: 2px solid #44475a;
                border-radius: 8px;
                margin: 10px 0;
                padding: 10px;
            }
            
            /* Метки (labels) */
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            /* Информационная подсказка */
            #infoLabel {
                color: #64ffda;
                font-size: 13px;
                font-weight: normal;
                font-style: italic;
                background: rgba(100, 255, 218, 0.15);
                border-radius: 6px;
                padding: 10px 12px;
                border-left: 4px solid #64ffda;
                margin: 5px 0;
            }
            
            #searchGroup::title, #resultsGroup::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background: rgba(10, 10, 15, 0.9);
            }
            
            /* Поля ввода */
            #searchInput {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                min-height: 20px;
            }
            
            #searchInput:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            #searchInput::placeholder {
                color: #6272a4;
                font-style: italic;
            }
            
            /* Стили валидации */
            .error-label {
                color: #ff6b6b !important;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                margin-top: 5px;
                padding: 5px 8px;
                background: rgba(255, 107, 107, 0.1);
                border-radius: 4px;
                border-left: 3px solid #ff6b6b;
            }
            
            .success-label {
                color: #50fa7b !important;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                margin-top: 5px;
                padding: 5px 8px;
                background: rgba(80, 250, 123, 0.1);
                border-radius: 4px;
                border-left: 3px solid #50fa7b;
            }
            
            QLabel[class="error-label"] {
                color: #ff6b6b !important;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                margin-top: 5px;
                padding: 5px 8px;
                background: rgba(255, 107, 107, 0.1);
                border-radius: 4px;
                border-left: 3px solid #ff6b6b;
            }
            
            QLabel[class="success-label"] {
                color: #50fa7b !important;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                margin-top: 5px;
                padding: 5px 8px;
                background: rgba(80, 250, 123, 0.1);
                border-radius: 4px;
                border-left: 3px solid #50fa7b;
            }
            
            QLineEdit.error {
                border: 2px solid #ff6b6b !important;
                background: rgba(255, 107, 107, 0.15) !important;
            }
            
            QLineEdit.success {
                border: 2px solid #50fa7b !important;
                background: rgba(80, 250, 123, 0.15) !important;
            }
            
            #searchInput.error {
                border: 2px solid #ff6b6b !important;
                background: rgba(255, 107, 107, 0.15) !important;
            }
            
            #searchInput.success {
                border: 2px solid #50fa7b !important;
                background: rgba(80, 250, 123, 0.15) !important;
            }
            
            /* Выпадающие списки */
            #tableCombo, #columnCombo, #searchTypeCombo {
                background: rgba(25, 25, 35, 0.9);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #ffffff;
                min-height: 20px;
            }
            
            #tableCombo:hover, #columnCombo:hover, #searchTypeCombo:hover {
                background: rgba(35, 35, 45, 0.9);
                border: 2px solid #6272a4;
                color: #64ffda;
            }
            
            #tableCombo:focus, #columnCombo:focus, #searchTypeCombo:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            #tableCombo::drop-down, #columnCombo::drop-down, #searchTypeCombo::drop-down {
                border: none;
                background: #64ffda;
                width: 20px;
            }
            
            #tableCombo::down-arrow, #columnCombo::down-arrow, #searchTypeCombo::down-arrow {
                image: none;
                border: 2px solid #ffffff;
                width: 6px;
                height: 6px;
                background: #ffffff;
            }
            
            /* Стили для выпадающего списка */
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95);
                border: 2px solid #64ffda;
                border-radius: 6px;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 13px;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-bottom: 1px solid #44475a;
                color: #f8f8f2;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background: rgba(100, 255, 218, 0.2);
                color: #64ffda;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background: #64ffda;
                color: #0a0a0f;
            }
            
            /* Чекбокс */
            #caseSensitiveCheck {
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 13px;
            }
            
            #caseSensitiveCheck::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #44475a;
                border-radius: 3px;
                background: rgba(15, 15, 25, 0.8);
            }
            
            #caseSensitiveCheck::indicator:checked {
                background: #64ffda;
                border: 2px solid #64ffda;
            }
            
            /* Текстовая область результатов */
            #resultsText {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }
            
            #resultsText:focus {
                border: 2px solid #64ffda;
            }
            
            /* Кнопки */
            #searchButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
                border: none;
                border-radius: 6px;
                color: #0a0a0f;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px 20px;
                min-width: 100px;
            }
            
            #searchButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
                border: 2px solid #64ffda;
            }
            
            #searchButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3bc1a8, 
                                          stop: 1 #00838f);
            }
            
            #clearButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
                border: none;
                border-radius: 6px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px 20px;
                min-width: 100px;
            }
            
            #clearButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff5252, 
                                          stop: 1 #f44336);
                border: 2px solid #ff6b6b;
            }
            
            #closeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: none;
                border-radius: 6px;
                color: #f8f8f2;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px 20px;
                min-width: 100px;
            }
            
            #closeButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #44475a, 
                                          stop: 1 #2a2a3a);
                border: 2px solid #6272a4;
            }
            
            /* Скроллбары */
            QScrollBar:vertical {
                border: none;
                background: #1a1a2e;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #64ffda;
                border-radius: 6px;
                min-height: 25px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #50e3c2;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
