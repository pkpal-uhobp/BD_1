"""
Миксин для работы с пользовательскими типами данных (ENUM, composite types)
"""

import logging
from sqlalchemy import text, inspect
from typing import List, Dict, Any, Optional, Tuple


class CustomTypesMixin:
    """Миксин для работы с пользовательскими типами PostgreSQL"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем логгер для этого миксина
        self.logger = logging.getLogger("DB")
    
    def create_enum_type(self, type_name: str, values: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Создаёт пользовательский ENUM тип.
        
        Args:
            type_name: Имя нового типа
            values: Список значений для ENUM
            
        Returns:
            Tuple[bool, Optional[str]]: (успех, сообщение об ошибке)
        """
        if not self.is_connected():
            return False, "Нет подключения к базе данных"
        
        if not type_name or not values:
            return False, "Имя типа и значения обязательны"
        
        try:
            # Проверяем, существует ли уже такой тип
            existing_types = self.get_custom_types()
            if any(t['type_name'] == type_name for t in existing_types):
                return False, f"Тип '{type_name}' уже существует"
            
            # Экранируем значения для SQL
            escaped_values = [f"'{v}'" for v in values]
            values_str = ', '.join(escaped_values)
            
            # Создаём ENUM тип
            sql = f"CREATE TYPE {type_name} AS ENUM ({values_str})"
            
            self.logger.info(f"Создание ENUM типа: {sql}")
            
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            self.logger.info(f"ENUM тип '{type_name}' успешно создан")
            return True, None
            
        except Exception as e:
            error_msg = f"Ошибка при создании ENUM типа: {self.format_db_error(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def create_composite_type(self, type_name: str, fields: List[Dict[str, str]]) -> Tuple[bool, Optional[str]]:
        """
        Создаёт составной (composite) тип.
        
        Args:
            type_name: Имя нового типа
            fields: Список словарей с полями {'name': 'field_name', 'type': 'data_type'}
            
        Returns:
            Tuple[bool, Optional[str]]: (успех, сообщение об ошибке)
        """
        if not self.is_connected():
            return False, "Нет подключения к базе данных"
        
        if not type_name or not fields:
            return False, "Имя типа и поля обязательны"
        
        try:
            # Проверяем, существует ли уже такой тип
            existing_types = self.get_custom_types()
            if any(t['type_name'] == type_name for t in existing_types):
                return False, f"Тип '{type_name}' уже существует"
            
            # Формируем список полей
            field_definitions = []
            for field in fields:
                field_name = field.get('name', '').strip()
                field_type = field.get('type', '').strip()
                if field_name and field_type:
                    field_definitions.append(f"{field_name} {field_type}")
            
            if not field_definitions:
                return False, "Необходимо указать хотя бы одно поле"
            
            fields_str = ', '.join(field_definitions)
            
            # Создаём составной тип
            sql = f"CREATE TYPE {type_name} AS ({fields_str})"
            
            self.logger.info(f"Создание составного типа: {sql}")
            
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            self.logger.info(f"Составной тип '{type_name}' успешно создан")
            return True, None
            
        except Exception as e:
            error_msg = f"Ошибка при создании составного типа: {self.format_db_error(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_custom_types(self) -> List[Dict[str, Any]]:
        """
        Получает список всех пользовательских типов в базе данных.
        
        Returns:
            List[Dict]: Список пользовательских типов с их свойствами
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к базе данных")
            return []
        
        try:
            # Запрос для получения пользовательских типов
            sql = """
            SELECT 
                t.typname as type_name,
                CASE 
                    WHEN t.typtype = 'e' THEN 'enum'
                    WHEN t.typtype = 'c' THEN 'composite'
                    WHEN t.typtype = 'd' THEN 'domain'
                    ELSE 'other'
                END as type_kind,
                pg_catalog.pg_get_userbyid(t.typowner) as owner,
                pg_catalog.obj_description(t.oid, 'pg_type') as description
            FROM pg_catalog.pg_type t
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid))
                AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_type el WHERE el.oid = t.typelem AND el.typarray = t.oid)
                AND n.nspname NOT IN ('pg_catalog', 'information_schema')
                AND t.typtype IN ('e', 'c', 'd')
            ORDER BY t.typname
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                
                types_list = []
                for row in rows:
                    type_dict = {
                        'type_name': row[0],
                        'type_kind': row[1],
                        'owner': row[2],
                        'description': row[3] if row[3] else ''
                    }
                    
                    # Для ENUM типов получаем значения
                    if row[1] == 'enum':
                        type_dict['values'] = self.get_enum_values(row[0])
                    
                    # Для составных типов получаем поля
                    elif row[1] == 'composite':
                        type_dict['fields'] = self.get_composite_fields(row[0])
                    
                    types_list.append(type_dict)
                
                self.logger.info(f"Найдено {len(types_list)} пользовательских типов")
                return types_list
                
        except Exception as e:
            self.logger.error(f"Ошибка при получении пользовательских типов: {self.format_db_error(e)}")
            return []
    
    def get_enum_values(self, type_name: str) -> List[str]:
        """
        Получает значения для ENUM типа.
        
        Args:
            type_name: Имя ENUM типа
            
        Returns:
            List[str]: Список значений ENUM
        """
        try:
            sql = """
            SELECT e.enumlabel
            FROM pg_enum e
            JOIN pg_type t ON e.enumtypid = t.oid
            WHERE t.typname = :type_name
            ORDER BY e.enumsortorder
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), {"type_name": type_name})
                rows = result.fetchall()
                return [row[0] for row in rows]
                
        except Exception as e:
            self.logger.error(f"Ошибка при получении значений ENUM: {self.format_db_error(e)}")
            return []
    
    def get_composite_fields(self, type_name: str) -> List[Dict[str, str]]:
        """
        Получает поля составного типа.
        
        Args:
            type_name: Имя составного типа
            
        Returns:
            List[Dict]: Список полей с их типами
        """
        try:
            sql = """
            SELECT 
                a.attname as field_name,
                pg_catalog.format_type(a.atttypid, a.atttypmod) as field_type
            FROM pg_catalog.pg_attribute a
            JOIN pg_catalog.pg_type t ON t.typrelid = a.attrelid
            WHERE t.typname = :type_name
                AND a.attnum > 0
                AND NOT a.attisdropped
            ORDER BY a.attnum
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), {"type_name": type_name})
                rows = result.fetchall()
                return [{'name': row[0], 'type': row[1]} for row in rows]
                
        except Exception as e:
            self.logger.error(f"Ошибка при получении полей составного типа: {self.format_db_error(e)}")
            return []
    
    def drop_custom_type(self, type_name: str, cascade: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Удаляет пользовательский тип.
        
        Args:
            type_name: Имя типа для удаления
            cascade: Каскадное удаление (удалит все зависимые объекты)
            
        Returns:
            Tuple[bool, Optional[str]]: (успех, сообщение об ошибке)
        """
        if not self.is_connected():
            return False, "Нет подключения к базе данных"
        
        if not type_name:
            return False, "Имя типа обязательно"
        
        try:
            cascade_clause = "CASCADE" if cascade else "RESTRICT"
            sql = f"DROP TYPE {type_name} {cascade_clause}"
            
            self.logger.info(f"Удаление типа: {sql}")
            
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            self.logger.info(f"Тип '{type_name}' успешно удалён")
            return True, None
            
        except Exception as e:
            error_msg = f"Ошибка при удалении типа: {self.format_db_error(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def add_enum_value(self, type_name: str, value: str, before: str = None, after: str = None) -> Tuple[bool, Optional[str]]:
        """
        Добавляет новое значение в существующий ENUM тип.
        
        Args:
            type_name: Имя ENUM типа
            value: Новое значение
            before: Вставить перед этим значением (опционально)
            after: Вставить после этого значения (опционально)
            
        Returns:
            Tuple[bool, Optional[str]]: (успех, сообщение об ошибке)
        """
        if not self.is_connected():
            return False, "Нет подключения к базе данных"
        
        try:
            position_clause = ""
            if before:
                position_clause = f" BEFORE '{before}'"
            elif after:
                position_clause = f" AFTER '{after}'"
            
            sql = f"ALTER TYPE {type_name} ADD VALUE '{value}'{position_clause}"
            
            self.logger.info(f"Добавление значения в ENUM: {sql}")
            
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            self.logger.info(f"Значение '{value}' добавлено в тип '{type_name}'")
            return True, None
            
        except Exception as e:
            error_msg = f"Ошибка при добавлении значения в ENUM: {self.format_db_error(e)}"
            self.logger.error(error_msg)
            return False, error_msg
