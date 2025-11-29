"""
Рефакторированный класс DB с использованием миксинов
"""

from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, MetaData, inspect, UniqueConstraint, CheckConstraint, Boolean, Enum, ARRAY
from sqlalchemy import Table, Column, Integer, String, Numeric, Date, ForeignKey, text
import logging
from datetime import date
from typing import Optional, Dict, Any, List, Tuple

from .mixins import (
    ConnectionMixin,
    MetadataMixin,
    CrudMixin,
    TableOperationsMixin,
    ConstraintsMixin,
    SearchMixin,
    StringOperationsMixin,
    CustomTypesMixin
)


class DB(
    ConnectionMixin,
    MetadataMixin,
    CrudMixin,
    TableOperationsMixin,
    ConstraintsMixin,
    SearchMixin,
    StringOperationsMixin,
    CustomTypesMixin
):
    """
    Основной класс для работы с базой данных PostgreSQL.
    
    Использует миксины для организации функциональности:
    - ConnectionMixin: подключение и базовые операции
    - MetadataMixin: работа с метаданными и схемой
    - CrudMixin: CRUD операции
    - TableOperationsMixin: операции с таблицами
    - ConstraintsMixin: работа с ограничениями
    - SearchMixin: поиск и фильтрация
    - StringOperationsMixin: строковые операции
    - CustomTypesMixin: работа с пользовательскими типами
    """
    
    def __init__(self,
                 host: str = "localhost",
                 port: int = 5432,
                 dbname: str = "library_db",
                 user: str = "postgres",
                 password: str = "root",
                 sslmode: str = "prefer",
                 connect_timeout: int = 5,
                 log_file: str = "db_app.log"):
        """
        Инициализация класса DB.
        
        Args:
            host: Хост базы данных
            port: Порт базы данных
            dbname: Имя базы данных
            user: Имя пользователя
            password: Пароль
            sslmode: Режим SSL
            connect_timeout: Таймаут подключения
            log_file: Файл для логирования
        """
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.sslmode = sslmode
        self.connect_timeout = connect_timeout
        self.engine: Optional[Engine] = None
        self.metadata: Optional[MetaData] = None
        self.tables: Dict[str, Table] = {}
        
        # Настройка логирования - используем централизованный логгер
        self.logger = logging.getLogger("DB")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"Инициализация DB для {dbname} на {host}:{port}")

    def get_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о текущем состоянии подключения к БД.
        
        Returns:
            Словарь с информацией о подключении
        """
        return {
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
            "user": self.user,
            "connected": self.is_connected(),
            "tables_count": len(self.tables) if self.tables else 0,
            "engine_info": str(self.engine) if self.engine else None
        }

    def __enter__(self):
        """Поддержка контекстного менеджера для автоматического подключения."""
        if not self.is_connected():
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера для автоматического отключения."""
        self.disconnect()

    def __repr__(self) -> str:
        """Строковое представление объекта."""
        status = "подключен" if self.is_connected() else "отключен"
        return f"DB(host={self.host}, db={self.dbname}, status={status})"

    def __str__(self) -> str:
        """Строковое представление для пользователя."""
        return f"База данных {self.dbname} на {self.host}:{self.port} ({'подключена' if self.is_connected() else 'отключена'})"