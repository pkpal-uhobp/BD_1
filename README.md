**1. Связь 1:М** - одна запись в таблице А связана с несколькими в таблице Б
```sql
CREATE TABLE departments (id SERIAL PRIMARY KEY, name TEXT);
CREATE TABLE employees (id SERIAL PRIMARY KEY, name TEXT, department_id INTEGER REFERENCES departments(id));
```

**2. Таблица** - структура для хранения данных
```sql
CREATE TABLE users (id SERIAL, name VARCHAR(50));
```

**3. Блокировка строк**
```sql
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- обновление данных
COMMIT;
```

**4. Подключение через psql**
```bash
psql -h localhost -U username -d database_name
```

**5. LIKE/ILIKE**
```sql
SELECT * FROM users WHERE name LIKE 'J%'; -- начинается с J
SELECT * FROM users WHERE name ILIKE 'j%'; -- без учета регистра
```

**6. Восстановление из backup**
```bash
pg_restore -d database_name backup_file.dump
```

**7. Оконные функции**
```sql
SELECT name, salary, AVG(salary) OVER (PARTITION BY department_id) 
FROM employees;
```

**8. CHECK**
```sql
CREATE TABLE products (
    price NUMERIC CHECK (price > 0)
);
```

**9. Удаление таблицы**
```sql
DROP TABLE table_name;
```

**10. Права доступа**
```sql
GRANT SELECT, INSERT ON table_name TO user_name;
```

**11. VIEW**
```sql
CREATE VIEW active_users AS 
SELECT * FROM users WHERE is_active = true;
```

**12. Значение по умолчанию**
```sql
CREATE TABLE orders (
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**13. Обновление данных**
```sql
UPDATE users SET email = 'new@email.com' WHERE id = 1;
```

**14. Составной ключ**
```sql
CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    PRIMARY KEY (student_id, course_id)
);
```

**15. Извлечение из JSONB**
```sql
SELECT data->>'name' FROM users WHERE data @> '{"age": 25}';
```

**16. Первичный ключ**
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT
);
```

**17. Создание роли**
```sql
CREATE ROLE read_only WITH LOGIN PASSWORD 'password';
```

**18. NULL vs пустая строка**
```sql
SELECT NULL IS NULL; -- true
SELECT '' IS NULL; -- false
```

**19. Строка (кортеж)**
```sql
INSERT INTO users (name, age) VALUES ('John', 25); -- одна строка
```

**20. База данных** - организованная коллекция данных
```sql
CREATE DATABASE company;
```

**21. COPY**
```sql
COPY users TO '/tmp/users.csv' CSV HEADER;
COPY users FROM '/tmp/users.csv' CSV;
```

**22. 1NF** - атомарность значений, отсутствие повторяющихся групп
```sql
-- Плохо: phones TEXT '123,456'
-- Хорошо: отдельная таблица телефонов
```

**23. Столбец (атрибут)**
```sql
CREATE TABLE users (
    id INT,        -- столбец
    name VARCHAR   -- столбец
);
```

**24. Подзапрос в WHERE**
```sql
SELECT * FROM products 
WHERE price > (SELECT AVG(price) FROM products);
```

**25. RIGHT JOIN и FULL JOIN**
```sql
SELECT * FROM users RIGHT JOIN orders ON users.id = orders.user_id;
SELECT * FROM users FULL JOIN orders ON users.id = orders.user_id;
```

**26. Внешний ключ**
```sql
CREATE TABLE orders (
    user_id INTEGER REFERENCES users(id)
);
```

**27. Кардинальность связей** - 1:1, 1:М, М:М

**28. Поиск по JSONB**
```sql
SELECT * FROM products WHERE metadata @> '{"color": "red"}';
```

**29. Массивы**
```sql
CREATE TABLE posts (
    tags TEXT[]
);
INSERT INTO posts VALUES (ARRAY['tech', 'programming']);
```

**30. Функциональный индекс**
```sql
CREATE INDEX idx_lower_name ON users (LOWER(name));
```

**31. Слабая сущность** - зависит от другой сущности (заказ без клика не существует)

**32. Запрет NULL**
```sql
CREATE TABLE users (
    name TEXT NOT NULL
);
```

**33. HAVING**
```sql
SELECT department_id, AVG(salary) 
FROM employees 
GROUP BY department_id 
HAVING AVG(salary) > 50000;
```

**34. VACUUM и ANALYZE**
```sql
VACUUM ANALYZE users; -- очистка и сбор статистики
```

**35. Ограничение строк**
```sql
SELECT * FROM users LIMIT 10;
```

**36. Удаление записи**
```sql
DELETE FROM users WHERE id = 1;
```

**37. CTE (WITH)**
```sql
WITH top_earners AS (
    SELECT * FROM employees WHERE salary > 100000
)
SELECT * FROM top_earners;
```

**38. INNER JOIN**
```sql
SELECT * FROM users INNER JOIN orders ON users.id = orders.user_id;
```

**39. Создание если отсутствует**
```sql
CREATE TABLE IF NOT EXISTS users (id SERIAL);
```

**40. Схема БД**
```sql
CREATE SCHEMA sales;
CREATE TABLE sales.orders (...);
```

**41. Возврат сгенерированного ключа**
```sql
INSERT INTO users (name) VALUES ('John') RETURNING id;
```

**42. Модели данных**:
- Концептуальная: ER-диаграммы
- Логическая: таблицы, связи
- Физическая: индексы, партиции

**43. Триггеры** - автоматические действия при событиях
```sql
CREATE TRIGGER log_changes BEFORE UPDATE ON users ...
```

**44. Переименование**
```sql
ALTER TABLE users RENAME COLUMN old_name TO new_name;
ALTER TABLE old_table RENAME TO new_table;
```

**45. Откат транзакции**
```sql
BEGIN;
-- операции
ROLLBACK;
```

**46. Строковые функции**
```sql
SELECT LENGTH('hello'), UPPER('hello'), SUBSTRING('hello' FROM 2 FOR 3);
```

**47. Вставка данных**
```sql
INSERT INTO users (name, age) VALUES ('John', 25);
```

**48. ER-диаграмма** - визуальное представление сущностей и связей

**49. Агрегатные функции**
```sql
SELECT COUNT(*), AVG(age), MAX(salary) FROM employees;
```

**50. Материализованное представление**
```sql
CREATE MATERIALIZED VIEW sales_summary AS 
SELECT product_id, SUM(quantity) FROM orders GROUP BY product_id;
```

**51. Метаданные таблицы**
```psql
\d table_name
```

**52. Ограничение доступа через VIEW**
```sql
CREATE VIEW public_users AS SELECT id, name FROM users;
GRANT SELECT ON public_users TO public_user;
```

**53. CROSS JOIN**
```sql
SELECT * FROM colors CROSS JOIN sizes;
```

**54. Дата и время**
```sql
SELECT NOW(), CURRENT_DATE, EXTRACT(YEAR FROM NOW());
```

**55. 3NF** - отсутствие транзитивных зависимостей

**56. Регулярные выражения**
```sql
SELECT * FROM users WHERE name ~ '^J.*n$';
```

**57. Суррогатный ключ** - искусственный (id) vs естественный (email)

**58. SEQUENCE**
```sql
CREATE SEQUENCE user_id_seq;
SELECT nextval('user_id_seq');
```

**59. Домен**
```sql
CREATE DOMAIN email AS TEXT CHECK (VALUE ~ '@');
```

**60. Сортировка**
```sql
SELECT * FROM users ORDER BY name DESC;
```

**61. Обновление VIEW** - через INSTEAD OF триггеры

**62. COALESCE и NULLIF**
```sql
SELECT COALESCE(NULL, 'default'); -- 'default'
SELECT NULLIF(5, 5); -- NULL
```

**63. Индекс** - ускорение поиска
```sql
CREATE INDEX idx_users_email ON users(email);
```

**64. Расширения**
```sql
CREATE EXTENSION postgis;
```

**65. SERIAL vs GENERATED AS IDENTITY**
```sql
-- SERIAL (устаревший)
-- GENERATED AS IDENTITY (современный)
```

**66. Создание/удаление БД**
```sql
CREATE DATABASE test;
DROP DATABASE test;
```

**67. JSONB** - бинарный JSON с индексацией
```sql
CREATE TABLE products (data JSONB);
```

**68. Первичный ключ** - уникальная идентификация строк

**69. Булевы условия**
```sql
SELECT * FROM users WHERE is_active = true AND age > 18;
```

**70. Пользовательская функция**
```sql
CREATE FUNCTION get_user_count() RETURNS INT AS $$
BEGIN
    RETURN COUNT(*) FROM users;
END;
$$ LANGUAGE plpgsql;

SELECT get_user_count();
```

**71. Системные каталоги**
```sql
SELECT * FROM pg_tables;
```

**72. search_path**
```sql
SET search_path TO schema1, public;
```

**73. Уникальность**
```sql
CREATE TABLE users (email TEXT UNIQUE);
```

**74. 2NF** - отсутствие частичных зависимостей

**75. План выполнения**
```sql
EXPLAIN SELECT * FROM users;
```

**76. CRUD** - Create, Read, Update, Delete

**77. Нормализация** - устранение избыточности и аномалий

**78. Выбор столбцов**
```sql
SELECT name, email FROM users;
```

**79. Когда индекс не помогает** - маленькие таблицы, частые обновления

**80. TRUNCATE**
```sql
TRUNCATE TABLE users;
```

**81. Базовые типы** - INTEGER, TEXT, BOOLEAN, TIMESTAMP, etc.

**82. Связь М:N**
```sql
CREATE TABLE students (id SERIAL);
CREATE TABLE courses (id SERIAL);
CREATE TABLE enrollments (student_id INT, course_id INT);
```

**83. Фильтрация строк**
```sql
SELECT * FROM users WHERE age > 18;
```

**84. Резервная копия**
```bash
pg_dump database_name > backup.sql
```

**85. Права на схему**
```sql
GRANT USAGE ON SCHEMA sales TO user_name;
```

**86. GROUP BY**
```sql
SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;
```

**87. Обязательность связи** - обязательная vs опциональная связь

**88. UUID как PK**
```sql
CREATE TABLE users (id UUID PRIMARY KEY DEFAULT gen_random_uuid());
```

**89. Уровни изоляции** - Read Uncommitted, Read Committed, Repeatable Read, Serializable

**90. Транзакция** - атомарная группа операций
```sql
BEGIN;
-- операции
COMMIT;
```

**91. PL/pgSQL функция**
```sql
CREATE FUNCTION add_user(name TEXT) RETURNS VOID AS $$
BEGIN
    INSERT INTO users (name) VALUES (name);
END;
$$ LANGUAGE plpgsql;
```

**92. Денормализация** - для производительности чтения

**93. Триггер на обновление**
```sql
CREATE TRIGGER update_timestamp BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_modified_column();
```

**94. LEFT JOIN**
```sql
SELECT * FROM users LEFT JOIN orders ON users.id = orders.user_id;
```

**95. DISTINCT**
```sql
SELECT DISTINCT department_id FROM employees;
```

**96. GIN/GiST vs B-Tree** - для составных типов данных (массивы, JSON, полнотекстовый поиск)

**97. ACID** - Atomicity, Consistency, Isolation, Durability

**98. ALTER TABLE**
```sql
ALTER TABLE users ADD COLUMN phone TEXT;
```

**99. UPSERT**
```sql
INSERT INTO users (id, name) VALUES (1, 'John')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
```

**100. Генерация тестовых данных**
```sql
INSERT INTO users (name) 
SELECT 'User' || n FROM generate_series(1, 1000) n;
```
