"""
Миксин для подключения к базе данных
"""

import logging
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional


class ConnectionMixin:
    """Миксин для работы с подключением к базе данных"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем логгер для этого миксина
        self.logger = logging.getLogger("DB")
    
    def format_db_error(self, error: Exception) -> str:
        """Преобразует ошибки БД в человеко-понятные сообщения."""
        error_msg = str(error)
        if "could not connect to server" in error_msg:
            return "Не удалось подключиться к серверу БД. Проверьте хост, порт и доступность сервера."
        if "password authentication failed" in error_msg:
            return "Неверное имя пользователя или пароль. Проверьте учётные данные."
        if "database" in error_msg and "does not exist" in error_msg:
            return "Указанная база данных не существует. Проверьте имя БД."
        if "timeout" in error_msg.lower():
            return "Превышено время ожидания подключения. Проверьте настройки сети или сервера."
        if "Connection refused" in error_msg:
            return "Соединение отклонено. Проверьте, запущен ли PostgreSQL."
        # Общее сообщение, если не распознали конкретную ошибку
        return f"Ошибка подключения: {error_msg[:200]}..."

    def connect(self) -> bool:
        """Подключается к базе данных и инициализирует метаданные."""
        self.logger.info("Попытка подключения к БД...")
        try:
            url = (
                f"postgresql+psycopg2://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.dbname}"
                f"?sslmode={self.sslmode}&connect_timeout={self.connect_timeout}"
            )

            self.engine = create_engine(url, future=True, pool_pre_ping=True)
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            self.logger.info(f"✅ Подключено: {self.dbname}@{self.host}:{self.port}")
            self._build_metadata()
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка подключения: {self.format_db_error(e)}")
            self.engine = None
            return False

    def disconnect(self):
        """Закрывает соединение с БД и очищает метаданные."""
        if not self.engine:
            self.logger.info("🔌 Соединение уже закрыто или не было установлено.")
            return

        try:
            self.engine.dispose()
            self.engine = None
            self.metadata = None
            self.tables.clear()
            self.logger.info("✅ Соединение с БД успешно закрыто.")
        except Exception as e:
            self.logger.error(f"❌ Ошибка при закрытии соединения: {e}")

    def is_connected(self) -> bool:
        """Проверяет, активно ли соединение с БД (логирует только при ошибке)."""
        if self.engine is None:
            self.logger.warning("⚠️ Проверка подключения: соединение не активно.")
            return False
        return True
