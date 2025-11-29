"""
Виджет для работы с NULL-значениями через функции COALESCE и NULLIF
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QLineEdit, QPushButton, QGroupBox, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QColor


class NullHandlerWidget(QWidget):
    """Виджет для работы с NULL-значениями через COALESCE и NULLIF"""
    
    # Сигнал, который испускается при изменении значения
    valueChanged = Signal(object)
    
    def __init__(self, field_name: str = "", parent=None):
        super().__init__(parent)
        self.field_name = field_name
        self._use_null_handling = False
        self._null_handling_mode = "none"  # none, coalesce, nullif, set_null
        self._actual_value = None
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Создает UI виджета"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)
        
        # Основной контейнер с чекбоксом для включения обработки NULL
        main_container = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_container.setLayout(main_layout)
        
        # Чекбокс для включения обработки NULL
        self.null_check = QCheckBox("NULL обработка")
        self.null_check.setObjectName("nullCheck")
        self.null_check.stateChanged.connect(self._on_null_check_changed)
        main_layout.addWidget(self.null_check)
        
        # Комбобокс выбора режима
        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("modeCombo")
        self.mode_combo.addItems([
            "Установить NULL",
            "COALESCE (замена NULL)",
            "NULLIF (сделать NULL если...)"
        ])
        self.mode_combo.setEnabled(False)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        main_layout.addWidget(self.mode_combo, 1)
        
        layout.addWidget(main_container)
        
        # Контейнер для параметров (изначально скрыт)
        self.params_container = QWidget()
        self.params_container.setObjectName("paramsContainer")
        params_layout = QVBoxLayout()
        params_layout.setContentsMargins(10, 5, 10, 5)
        params_layout.setSpacing(5)
        self.params_container.setLayout(params_layout)
        
        # Поле для COALESCE - значение по умолчанию
        self.coalesce_container = QWidget()
        coalesce_layout = QHBoxLayout()
        coalesce_layout.setContentsMargins(0, 0, 0, 0)
        self.coalesce_container.setLayout(coalesce_layout)
        
        coalesce_label = QLabel("Значение по умолчанию:")
        coalesce_label.setObjectName("paramLabel")
        coalesce_layout.addWidget(coalesce_label)
        
        self.coalesce_value = QLineEdit()
        self.coalesce_value.setObjectName("coalesceInput")
        self.coalesce_value.setPlaceholderText("Значение если NULL")
        self.coalesce_value.textChanged.connect(self._on_value_changed)
        coalesce_layout.addWidget(self.coalesce_value, 1)
        
        params_layout.addWidget(self.coalesce_container)
        
        # Поле для NULLIF - значение для сравнения
        self.nullif_container = QWidget()
        nullif_layout = QHBoxLayout()
        nullif_layout.setContentsMargins(0, 0, 0, 0)
        self.nullif_container.setLayout(nullif_layout)
        
        nullif_label = QLabel("NULL если равно:")
        nullif_label.setObjectName("paramLabel")
        nullif_layout.addWidget(nullif_label)
        
        self.nullif_value = QLineEdit()
        self.nullif_value.setObjectName("nullifInput")
        self.nullif_value.setPlaceholderText("Значение для сравнения")
        self.nullif_value.textChanged.connect(self._on_value_changed)
        nullif_layout.addWidget(self.nullif_value, 1)
        
        params_layout.addWidget(self.nullif_container)
        
        # Инфо-лейбл
        self.info_label = QLabel()
        self.info_label.setObjectName("infoLabel")
        self.info_label.setWordWrap(True)
        params_layout.addWidget(self.info_label)
        
        self.params_container.hide()
        layout.addWidget(self.params_container)
        
        # Обновляем отображение
        self._update_visibility()
    
    def apply_styles(self):
        """Применяет стили"""
        self.setStyleSheet("""
            #nullCheck {
                color: #bd93f9;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #nullCheck::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #44475a;
                border-radius: 4px;
                background: rgba(15, 15, 25, 0.8);
            }
            
            #nullCheck::indicator:checked {
                background: #bd93f9;
                border: 2px solid #bd93f9;
            }
            
            #modeCombo {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                min-height: 25px;
            }
            
            #modeCombo:enabled {
                border: 2px solid #bd93f9;
            }
            
            #modeCombo:focus {
                border: 2px solid #ff79c6;
            }
            
            #paramsContainer {
                background: rgba(189, 147, 249, 0.1);
                border: 1px solid #bd93f960;
                border-radius: 6px;
                padding: 8px;
            }
            
            #paramLabel {
                color: #8892b0;
                font-size: 11px;
                font-family: 'Consolas', 'Fira Code', monospace;
                min-width: 140px;
            }
            
            #coalesceInput, #nullifInput {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            
            #coalesceInput:focus, #nullifInput:focus {
                border: 2px solid #bd93f9;
            }
            
            #infoLabel {
                color: #6272a4;
                font-size: 10px;
                font-style: italic;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 3px;
            }
        """)
    
    def _on_null_check_changed(self, state):
        """Обработчик изменения состояния чекбокса"""
        self._use_null_handling = state == Qt.Checked
        self.mode_combo.setEnabled(self._use_null_handling)
        self._update_visibility()
        self._on_value_changed()
    
    def _on_mode_changed(self, index):
        """Обработчик изменения режима"""
        modes = ["set_null", "coalesce", "nullif"]
        self._null_handling_mode = modes[index] if index < len(modes) else "none"
        self._update_visibility()
        self._on_value_changed()
    
    def _update_visibility(self):
        """Обновляет видимость элементов в зависимости от режима"""
        if not self._use_null_handling:
            self.params_container.hide()
            return
        
        self.params_container.show()
        mode = self._null_handling_mode
        
        # Показываем/скрываем соответствующие контейнеры
        self.coalesce_container.setVisible(mode == "coalesce")
        self.nullif_container.setVisible(mode == "nullif")
        
        # Обновляем информационный текст
        info_texts = {
            "set_null": "Значение поля будет установлено в NULL",
            "coalesce": "COALESCE заменит NULL на указанное значение при выборке",
            "nullif": "NULLIF установит NULL, если значение равно указанному"
        }
        self.info_label.setText(info_texts.get(mode, ""))
    
    def _on_value_changed(self):
        """Испускает сигнал об изменении значения"""
        self.valueChanged.emit(self.get_value())
    
    def get_value(self):
        """
        Возвращает значение с учётом обработки NULL.
        
        Returns:
            dict с ключами:
            - 'use_null_handling': bool - используется ли обработка NULL
            - 'mode': str - режим обработки (set_null, coalesce, nullif)
            - 'value': any - значение для обработки
            - 'actual_value': any - исходное значение поля
        """
        result = {
            'use_null_handling': self._use_null_handling,
            'mode': self._null_handling_mode if self._use_null_handling else "none",
            'value': None,
            'actual_value': self._actual_value
        }
        
        if self._use_null_handling:
            if self._null_handling_mode == "set_null":
                result['value'] = None
            elif self._null_handling_mode == "coalesce":
                result['value'] = self.coalesce_value.text().strip() or None
            elif self._null_handling_mode == "nullif":
                result['value'] = self.nullif_value.text().strip() or None
        
        return result
    
    def set_actual_value(self, value):
        """Устанавливает исходное значение поля"""
        self._actual_value = value
    
    def is_null_handling_enabled(self):
        """Проверяет, включена ли обработка NULL"""
        return self._use_null_handling
    
    def get_mode(self):
        """Возвращает текущий режим обработки NULL"""
        return self._null_handling_mode if self._use_null_handling else "none"
    
    def get_sql_expression(self, column_name: str, value):
        """
        Генерирует SQL выражение для обработки NULL.
        
        Args:
            column_name: Имя столбца
            value: Значение для использования
            
        Returns:
            tuple: (sql_expression, params_dict)
        """
        if not self._use_null_handling:
            return None, {}
        
        mode = self._null_handling_mode
        
        if mode == "set_null":
            return f'"{column_name}" = NULL', {}
        elif mode == "coalesce":
            coalesce_val = self.coalesce_value.text().strip()
            if coalesce_val:
                return f'COALESCE("{column_name}", :coalesce_val)', {'coalesce_val': coalesce_val}
        elif mode == "nullif":
            nullif_val = self.nullif_value.text().strip()
            if nullif_val:
                return f'NULLIF("{column_name}", :nullif_val)', {'nullif_val': nullif_val}
        
        return None, {}
    
    def reset(self):
        """Сбрасывает виджет в начальное состояние"""
        self.null_check.setChecked(False)
        self.mode_combo.setCurrentIndex(0)
        self.coalesce_value.clear()
        self.nullif_value.clear()
        self._actual_value = None
        self._use_null_handling = False
        self._null_handling_mode = "none"
        self._update_visibility()


class NullValueDisplay(QWidget):
    """Виджет для отображения NULL значений с подсветкой"""
    
    def __init__(self, value=None, parent=None):
        super().__init__(parent)
        self.setup_ui(value)
    
    def setup_ui(self, value):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        if value is None:
            self.label = QLabel("NULL")
            self.label.setStyleSheet("""
                QLabel {
                    color: #ff79c6;
                    font-style: italic;
                    font-weight: bold;
                    background: rgba(255, 121, 198, 0.1);
                    border-radius: 4px;
                    padding: 2px 6px;
                }
            """)
        else:
            self.label = QLabel(str(value))
            self.label.setStyleSheet("""
                QLabel {
                    color: #f8f8f2;
                }
            """)
        
        layout.addWidget(self.label)
