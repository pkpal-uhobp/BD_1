## 1. Как использовать ALL для проверки условия для всех значений набора? Пример реализации.
**Теория:**  
`ALL` сравнивает выражение с каждым значением из набора. Условие выполняется, если сравнение истинно для всех.

**Пример реализации:**
```sql
SELECT * FROM employees
WHERE salary > ALL (SELECT salary FROM employees WHERE department_id = 1);
```

---

## 2. Как документировать пользовательские типы и изменять их без потери данных? Пример реализации.
**Теория:**  
Комментарии через `COMMENT ON TYPE`. Изменения (например, добавление значения в ENUM) не теряют данных.

**Пример реализации:**
```sql
CREATE TYPE mood AS ENUM ('happy', 'sad');
COMMENT ON TYPE mood IS 'Настроение пользователя';
ALTER TYPE mood ADD VALUE 'neutral';
```

---

## 3. Как использовать агрегаты в подзапросах для расчёта показателей? Пример реализации.
**Теория:**  
Агрегатные функции (`SUM`, `AVG` и др.) можно использовать в подзапросах для вычисления показателей.

**Пример реализации:**
```sql
SELECT * FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

---

## 4. Как упорядочить результаты запроса с ORDER BY и указать направление сортировки? Пример реализации.
**Теория:**  
`ORDER BY` сортирует результат; направление задается `ASC` (по возрастанию) или `DESC` (по убыванию).

**Пример реализации:**
```sql
SELECT * FROM employees
ORDER BY salary DESC;
```

---

## 5. Как считать агрегаты по группам с GROUP BY? Пример реализации.
**Теория:**  
`GROUP BY` группирует строки по столбцу(ам) для агрегирования.

**Пример реализации:**
```sql
SELECT department_id, SUM(salary)
FROM employees
GROUP BY department_id;
```

---

## 6. Как сгруппировать по вычисляемому значению (например, дата → год/месяц)? Пример реализации.
**Теория:**  
Можно группировать по выражению или функции.

**Пример реализации:**
```sql
SELECT EXTRACT(YEAR FROM order_date) AS year, COUNT(*)
FROM orders
GROUP BY year;
```

---

## 7. Чем COALESCE отличается от NVL/IFNULL в других СУБД? Пример реализации.
**Теория:**  
`COALESCE` — стандарт SQL, принимает список аргументов. `NVL`, `IFNULL` — аналоги в Oracle, MySQL (2 аргумента).

**Пример реализации:**
```sql
SELECT COALESCE(name, 'N/A') FROM users;
```

---

## 8. Как избегать N+1 подзапросов и заменить их одним набором JOIN/CTE? Пример реализации.
**Теория:**  
Вместо многократных подзапросов используйте JOIN или CTE для объединения данных за один проход.

**Пример реализации:**
```sql
SELECT e.*, d.name
FROM employees e
JOIN departments d ON e.department_id = d.id;
```

---

## 9. Как писать безопасные подзапросы, избегающие NULL‑ловушек с IN/NOT IN? Пример реализации.
**Теория:**  
`NOT IN` с NULL даёт неожиданный результат. Используйте `NOT EXISTS`.

**Пример реализации:**
```sql
SELECT * FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.id
);
```

---

## 10. Как экранировать спецсимволы в SIMILAR TO? Пример реализации.
**Теория:**  
В шаблонах спецсимволы экранируются обратным слэшем `\`.

**Пример реализации:**
```sql
SELECT * FROM test
WHERE name SIMILAR TO '%\\+%';
```

---

## 11. Как выбирать только уникальные строки с DISTINCT и когда это уместно? Пример реализации.
**Теория:**  
`DISTINCT` исключает повторяющиеся строки.

**Пример реализации:**
```sql
SELECT DISTINCT department_id FROM employees;
```

---

## 12. Как использовать квантификаторы в SIMILAR TO (+, *, ?, {m,n})? Пример реализации.
**Теория:**  
Квантификаторы задают количество повторений.

**Пример реализации:**
```sql
SELECT * FROM test
WHERE name SIMILAR TO '%[0-9]{2,}%';
```

---

## 13. Как проверить формат email/телефона на базовом уровне с SIMILAR TO? Пример реализации.
**Теория:**  
SIMILAR TO позволяет задать шаблон для проверки.

**Пример реализации:**
```sql
SELECT * FROM users
WHERE email SIMILAR TO '%@%.%';

SELECT * FROM users
WHERE phone SIMILAR TO '\\+[0-9]+%';
```

---

## 14. Как фильтровать группы с HAVING и в чём разница с WHERE? Пример реализации.
**Теория:**  
WHERE — до группировки, HAVING — после.

**Пример реализации:**
```sql
SELECT department_id, SUM(salary)
FROM employees
GROUP BY department_id
HAVING SUM(salary) > 10000;
```

---

## 15. Как проверить существование записей через подзапрос вместо подсчёта COUNT(*)? Пример реализации.
**Теория:**  
`EXISTS` быстрее, чем подсчёт.

**Пример реализации:**
```sql
SELECT * FROM customers c
WHERE EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.id
);
```

---

## 16. Как использовать составной тип как тип столбца? Пример реализации.
**Теория:**  
В PostgreSQL можно создать составной тип и использовать его как тип столбца.

**Пример реализации:**
```sql
CREATE TYPE address_type AS (city TEXT, zip TEXT);
CREATE TABLE users (
  id SERIAL,
  address address_type
);
```

---

## 17. Как использовать подзапрос в списке SELECT для вычисления агрегата по связанной таблице? Пример реализации.
**Теория:**  
В SELECT можно вычислять агрегаты по связанной таблице.

**Пример реализации:**
```sql
SELECT id,
  (SELECT SUM(amount) FROM orders o WHERE o.customer_id = c.id) AS total_orders
FROM customers c;
```

---

## 18. Как использовать подзапрос в FROM как временную таблицу (derived table)? Пример реализации.
**Теория:**  
Подзапрос в FROM создаёт временную таблицу.

**Пример реализации:**
```sql
SELECT dt.department_id, dt.avg_salary
FROM (
  SELECT department_id, AVG(salary) AS avg_salary
  FROM employees
  GROUP BY department_id
) dt
WHERE dt.avg_salary > 5000;
```

---

## 19. Как написать условие «существует хотя бы одна связанная запись» с EXISTS? Пример реализации.
**Теория:**  
`EXISTS` возвращает TRUE, если подзапрос вернул хотя бы одну строку.

**Пример реализации:**
```sql
SELECT * FROM employees e
WHERE EXISTS (
  SELECT 1 FROM orders o WHERE o.employee_id = e.id
);
```

---

## 20. Как упорядочить результат группировки по агрегатным столбцам? Пример реализации.
**Теория:**  
В ORDER BY можно использовать агрегатные столбцы после группировки.

**Пример реализации:**
```sql
SELECT department_id, SUM(salary) AS total_salary
FROM employees
GROUP BY department_id
ORDER BY total_salary DESC;
```

---

## 21. Как группировать сразу по нескольким столбцам и выражениям? Пример реализации.
**Теория:**  
GROUP BY поддерживает несколько столбцов и выражений.

**Пример реализации:**
```sql
SELECT department_id, EXTRACT(YEAR FROM hire_date) AS year, COUNT(*)
FROM employees
GROUP BY department_id, year;
```

---

## 22. Как выбирать конкретные столбцы вместо звёздочки и давать им псевдонимы? Пример реализации.
**Теория:**  
Указывайте столбцы явно, используйте псевдонимы через AS.

**Пример реализации:**
```sql
SELECT name AS employee_name, salary AS monthly_salary
FROM employees;
```

---

## 23. Как ограничить результаты подзапроса и передать их во внешний запрос? Пример реализации.
**Теория:**  
LIMIT в подзапросе ограничивает результат; далее используйте как источник.

**Пример реализации:**
```sql
SELECT * FROM (
  SELECT * FROM orders ORDER BY amount DESC LIMIT 3
) AS top_orders;
```

---

## 24. Как комбинировать агрегаты с оконными функциями (но без группировки результатов)? Пример реализации.
**Теория:**  
Оконные функции позволяют вычислять агрегаты без группировки.

**Пример реализации:**
```sql
SELECT id, department_id, salary,
  SUM(salary) OVER (PARTITION BY department_id) AS dept_total
FROM employees;
```

---

## 25. Как правильно выбирать столбцы в SELECT при GROUP BY? Пример реализации.
**Теория:**  
В SELECT при GROUP BY можно использовать только столбцы из GROUP BY и агрегатные функции.

**Пример реализации:**
```sql
SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;
```

---

## 26. Что такое ENUM и когда он полезен для ограниченного набора значений? Пример реализации.
**Теория:**  
ENUM — тип для хранения ограниченного набора значений.

**Пример реализации:**
```sql
CREATE TYPE mood AS ENUM ('happy', 'sad', 'neutral');
CREATE TABLE person (
  id SERIAL,
  mood mood
);
```

---

## 27. Как использовать NULLIF, чтобы избежать деления на ноль или конфликтов? Пример реализации.
**Теория:**  
NULLIF возвращает NULL, если значения равны.

**Пример реализации:**
```sql
SELECT SUM(amount) / NULLIF(COUNT(*), 0) FROM orders;
```

---

## 28. Как объединять результаты нескольких запросов через UNION и UNION ALL? Пример реализации.
**Теория:**  
UNION — только уникальные строки, UNION ALL — все.

**Пример реализации:**
```sql
SELECT name FROM employees
UNION
SELECT name FROM customers;

SELECT name FROM employees
UNION ALL
SELECT name FROM customers;
```

---

## 29. Как оптимизировать GROUP BY индексами и предварительной фильтрацией? Пример реализации.
**Теория:**  
Индексы на группируемых столбцах и фильтрация строк до группировки ускоряют запрос.

**Пример реализации:**
```sql
CREATE INDEX idx_department_id ON employees(department_id);

SELECT department_id, COUNT(*)
FROM employees
WHERE active = true
GROUP BY department_id;
```

---

## 30. Что такое запрос SELECT и какова его базовая форма (SELECT … FROM …)? Пример реализации.
**Теория:**  
SELECT … FROM … — основа любого SQL-запроса.

**Пример реализации:**
```sql
SELECT * FROM employees;
```

---

## 31. Как использовать COALESCE для подстановки значений по умолчанию? Пример реализации.
**Теория:**  
COALESCE возвращает первое ненулевое значение.

**Пример реализации:**
```sql
SELECT COALESCE(email, 'нет email') FROM users;
```

---

## 32. Как заменить NULL или код ошибки на понятную метку через CASE? Пример реализации.
**Теория:**  
CASE позволяет возвращать метку вместо NULL или ошибки.

**Пример реализации:**
```sql
SELECT name, CASE WHEN salary IS NULL THEN 'нет данных' ELSE salary::text END AS salary_info
FROM employees;
```

---

## 33. Как ограничить количество строк в результате с LIMIT и OFFSET? Пример реализации.
**Теория:**  
LIMIT ограничивает количество строк, OFFSET — пропускает строки.

**Пример реализации:**
```sql
SELECT * FROM employees LIMIT 10 OFFSET 20;
```

---

## 34. Как объединить агрегат в подзапросе с деталями во внешнем запросе? Пример реализации.
**Теория:**  
Внешний запрос получает детали, подзапрос — агрегат по связанным данным.

**Пример реализации:**
```sql
SELECT c.id, c.name,
  (SELECT SUM(amount) FROM orders o WHERE o.customer_id = c.id) AS total_amount
FROM customers c;
```

---

## 35. Чем DOMAIN отличается от базового типа и зачем он нужен? Пример реализации.
**Теория:**  
DOMAIN — пользовательский тип с ограничениями на базе простого типа.

**Пример реализации:**
```sql
CREATE DOMAIN email AS TEXT CHECK (VALUE ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$');

CREATE TABLE users (
  id SERIAL,
  email email
);
```

---

## 36. Как работает оператор EXISTS и чем он отличается от IN? Пример реализации.
**Теория:**  
EXISTS проверяет наличие хотя бы одной строки, IN — сравнивает с набором значений.

**Пример реализации:**
```sql
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

SELECT * FROM customers WHERE id IN (SELECT customer_id FROM orders);
```

---

## 37. Как вычислять выражения и функции прямо в списке SELECT? Пример реализации.
**Теория:**  
Можно вычислять выражения и применять функции к столбцам.

**Пример реализации:**
```sql
SELECT ROUND(salary, 0) AS salary_rounded, LENGTH(name) AS name_length
FROM employees;
```

---

## 38. Как агрегировать строки в одну строку с string_agg? Пример реализации.
**Теория:**  
string_agg объединяет значения группы в одну строку с разделителем.

**Пример реализации:**
```sql
SELECT department_id, string_agg(name, ', ')
FROM employees
GROUP BY department_id;
```

---

## 39. Как хранить и выбирать поля составного типа? Пример реализации.
**Теория:**  
Составной тип хранит связанные поля; выбирать их можно через точку.

**Пример реализации:**
```sql
CREATE TYPE address_type AS (city TEXT, zip TEXT);
CREATE TABLE users (
  id SERIAL,
  address address_type
);

SELECT address.city FROM users;
```

---

## 40. Как сделать сводку с несколькими показателями (COUNT, SUM, AVG) за раз? Пример реализации.
**Теория:**  
В одном запросе можно вычислять несколько агрегатов для группы.

**Пример реализации:**
```sql
SELECT department_id,
  COUNT(*) AS employees_count,
  SUM(salary) AS total_salary,
  AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id;
```

---

## 41. Как использовать подзапросы для проверки ссылочной целостности нестандартных правил? Пример реализации.
**Теория:**  
Подзапрос позволяет проверить наличие связанных записей по сложному правилу.

**Пример реализации:**
```sql
SELECT o.*
FROM orders o
WHERE NOT EXISTS (
  SELECT 1 FROM customers c
  WHERE c.id = o.customer_id AND c.active = true
);
```

---

## 42. Что такое выражение CASE и какие формы оно имеет (simple, searched)? Пример реализации.
**Теория:**  
CASE бывает simple (сравнение значения) и searched (логические условия).

**Пример реализации:**
```sql
-- Simple CASE
SELECT
  CASE status
    WHEN 'active' THEN 'Активен'
    WHEN 'inactive' THEN 'Неактивен'
    ELSE 'Неизвестно'
  END AS status_label
FROM users;

-- Searched CASE
SELECT
  CASE
    WHEN salary > 10000 THEN 'Высокая'
    WHEN salary > 5000 THEN 'Средняя'
    ELSE 'Низкая'
  END AS salary_level
FROM employees;
```

---

## 43. Как использовать подзапрос для вычисления рангов/топ-N по группе? Пример реализации.
**Теория:**  
Оконные функции + подзапрос для топ-N в группе.

**Пример реализации:**
```sql
SELECT *
FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
  FROM employees
) sub
WHERE rn <= 3;
```

---

## 44. Как выделить категории на основе диапазонов значений через CASE? Пример реализации.
**Теория:**  
CASE присваивает категорию по диапазону.

**Пример реализации:**
```sql
SELECT name,
  CASE
    WHEN age < 18 THEN 'Детство'
    WHEN age < 65 THEN 'Взрослый'
    ELSE 'Пожилой'
  END AS age_category
FROM users;
```

---

## 45. Как проверять деление на ноль и пропуски данных в агрегатах? Пример реализации.
**Теория:**  
NULLIF позволяет избежать деления на ноль; агрегаты игнорируют NULL.

**Пример реализации:**
```sql
SELECT SUM(amount) / NULLIF(COUNT(*), 0) AS avg_amount
FROM orders;
```

---

## 46. В чём разница между коррелированным и некоррелированным подзапросом? Пример реализации.
**Теория:**  
Коррелированный зависит от внешнего запроса, некоррелированный — нет.

**Пример реализации:**
```sql
-- Коррелированный
SELECT name
FROM employees e
WHERE EXISTS (
  SELECT 1 FROM orders o WHERE o.employee_id = e.id
);

-- Некоррелированный
SELECT name
FROM employees
WHERE department_id IN (SELECT id FROM departments WHERE active = true);
```

---

## 47. Как создать DOMAIN с CHECK‑ограничением? Пример реализации.
**Теория:**  
DOMAIN позволяет задать тип с ограничением.

**Пример реализации:**
```sql
CREATE DOMAIN positive_int AS INTEGER CHECK (VALUE > 0);

CREATE TABLE items (
  quantity positive_int
);
```

---

## 48. Какие базовые агрегаты существуют (COUNT, SUM, AVG, MIN, MAX) и для чего? Пример реализации.
**Теория:**  
COUNT, SUM, AVG, MIN, MAX для подсчёта, суммы, среднего, минимума, максимума.

**Пример реализации:**
```sql
SELECT
  COUNT(*) AS total,
  SUM(salary) AS sum_salary,
  AVG(salary) AS avg_salary,
  MIN(salary) AS min_salary,
  MAX(salary) AS max_salary
FROM employees;
```

---

## 49. Когда CTE материализуется/не материализуется в современных версиях PostgreSQL? Пример реализации.
**Теория:**  
CTE может материализоваться или быть встроенным (inline) — зависит от запроса и версии.

**Пример реализации:**
```sql
WITH active_employees AS (
  SELECT * FROM employees WHERE active = true
)
SELECT * FROM active_employees;

WITH active_employees AS MATERIALIZED (
  SELECT * FROM employees WHERE active = true
)
SELECT * FROM active_employees;
```

---

## 50. Как использовать LATERAL JOIN вместо коррелированного подзапроса? Пример реализации.
**Теория:**  
LATERAL позволяет ссылаться на столбцы из предыдущих таблиц в FROM.

**Пример реализации:**
```sql
SELECT o.*, c.*
FROM orders o
LEFT JOIN LATERAL (
  SELECT * FROM comments WHERE order_id = o.id ORDER BY created_at DESC LIMIT 1
) c ON TRUE;
```

---

## 51. Как написать условие «не существует ни одной связанной записи» с NOT EXISTS? Пример реализации.
**Теория:**  
NOT EXISTS возвращает TRUE, если подзапрос не вернул ни одной строки.

**Пример реализации:**
```sql
SELECT * FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.id
);
```

---

## 52. Как превратить булевы условия в метки «Да»/«Нет» через CASE? Пример реализации.
**Теория:**  
CASE позволяет преобразовать булево в метку.

**Пример реализации:**
```sql
SELECT name,
  CASE
    WHEN active THEN 'Да'
    ELSE 'Нет'
  END AS active_label
FROM users;
```

---

## 53. Как сравнить число с подзапросом через > ANY и > ALL — в чём разница? Пример реализации.
**Теория:**  
`> ANY` — больше хотя бы одного значения; `> ALL` — больше всех.

**Пример реализации:**
```sql
SELECT * FROM employees
WHERE salary > ANY (SELECT salary FROM employees WHERE department_id = 1);

SELECT * FROM employees
WHERE salary > ALL (SELECT salary FROM employees WHERE department_id = 1);
```

---

## 54. Как фильтровать строки в запросе с помощью WHERE? Пример реализации.
**Теория:**  
WHERE фильтрует строки до других операций.

**Пример реализации:**
```sql
SELECT * FROM employees WHERE active = true;
```

---

## 55. Как использовать DISTINCT ON для выборки по ключу вместо агрегирования? Пример реализации.
**Теория:**  
DISTINCT ON выбирает одну строку по ключу, обычно первую по сортировке.

**Пример реализации:**
```sql
SELECT DISTINCT ON (customer_id) *
FROM orders
ORDER BY customer_id, created_at;
```

---

## 56. Как CASE влияет на тип результата и приведение типов? Пример реализации.
**Теория:**  
CASE возвращает тип, приводимый из всех ветвей.

**Пример реализации:**
```sql
SELECT
  CASE WHEN salary > 10000 THEN salary ELSE NULL END AS salary_value
FROM employees;

SELECT
  CASE WHEN salary > 10000 THEN salary::text ELSE 'мало' END AS label
FROM employees;
```

---

## 57. Как проверять целостность группировок тестовыми подмножествами? Пример реализации.
**Теория:**  
Создайте тестовую таблицу, проверьте агрегаты.

**Пример реализации:**
```sql
SELECT department_id, COUNT(*), SUM(salary)
FROM test_employees
GROUP BY department_id;
```

---

## 58. Как тестировать и профилировать подзапросы (EXPLAIN/ANALYZE, enable_* GUC)? Пример реализации.
**Теория:**  
EXPLAIN/ANALYZE показывают план выполнения; GUC‑параметры влияют на оптимизацию.

**Пример реализации:**
```sql
EXPLAIN ANALYZE
SELECT * FROM employees WHERE active = true;

SET enable_seqscan = off;
```

---

## 59. Как группировать по условию (CASE внутри GROUP BY)? Пример реализации.
**Теория:**  
Группировка по вычисляемому значению CASE.

**Пример реализации:**
```sql
SELECT
  CASE
    WHEN age < 18 THEN 'Детство'
    WHEN age < 65 THEN 'Взрослый'
    ELSE 'Пожилой'
  END AS age_category,
  COUNT(*)
FROM users
GROUP BY age_category;
```

---

## 60. Чем отличается COUNT(*) от COUNT(column)? Пример реализации.
**Теория:**  
COUNT(*) — все строки; COUNT(column) — только не NULL.

**Пример реализации:**
```sql
SELECT COUNT(*) FROM employees;
SELECT COUNT(salary) FROM employees;
```

---

## 61. Как выполнить агрегирование по выражениям и функциональным ключам? Пример реализации.
**Теория:**  
Группировка по результату функции/выражения.

**Пример реализации:**
```sql
SELECT EXTRACT(YEAR FROM created_at) AS year, COUNT(*)
FROM orders
GROUP BY year;
```

---

## 62. Как совместить EXISTS с дополнительными фильтрами внешнего запроса? Пример реализации.
**Теория:**  
EXISTS учитывает фильтры внешнего запроса.

**Пример реализации:**
```sql
SELECT * FROM customers c
WHERE c.active
  AND EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

---

## 63. Как записать анти‑соединение через NOT EXISTS и чем оно лучше LEFT JOIN … IS NULL? Пример реализации.
**Теория:**  
NOT EXISTS безопасен для NULL и быстрее, чем LEFT JOIN ... IS NULL.

**Пример реализации:**
```sql
SELECT * FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

---

## 64. Как оформить сложный запрос так, чтобы он оставался читаемым и поддерживаемым? Пример реализации.
**Теория:**  
Используйте CTE, отступы, алиасы.

**Пример реализации:**
```sql
WITH active_customers AS (
  SELECT * FROM customers WHERE active = true
)
SELECT c.id, c.name, COUNT(o.id) AS order_count
FROM active_customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name
ORDER BY order_count DESC;
```

---

## 65. Как использовать = ANY для упрощения выражений c IN в PostgreSQL? Пример реализации.
**Теория:**  
`= ANY(array)` эквивалентно `IN (list)`.

**Пример реализации:**
```sql
SELECT * FROM users WHERE id = ANY(ARRAY[1,2,3]);
```

---

## 66. Как отсекать малые группы с HAVING после агрегирования? Пример реализации.
**Теория:**  
HAVING фильтрует группы после агрегирования.

**Пример реализации:**
```sql
SELECT department_id, COUNT(*)
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5;
```

---

## 67. Как изменить ENUM, добавив новое значение (ADD VALUE …)? Пример реализации.
**Теория:**  
Добавление значения в ENUM не нарушает данные.

**Пример реализации:**
```sql
ALTER TYPE mood ADD VALUE 'angry';
```

---

## 68. Когда выбирать SIMILAR TO вместо LIKE и наоборот? Пример реализации.
**Теория:**  
LIKE — простой шаблон; SIMILAR TO — расширенный.

**Пример реализации:**
```sql
SELECT * FROM users WHERE name LIKE 'A%';
SELECT * FROM users WHERE name SIMILAR TO '(A|B)%';
```

---

## 69. Как вынести повторяющийся подзапрос в CTE и улучшить читаемость? Пример реализации.
**Теория:**  
CTE позволяет вынести общий подзапрос.

**Пример реализации:**
```sql
WITH big_orders AS (
  SELECT * FROM orders WHERE amount > 1000
)
SELECT * FROM big_orders WHERE status = 'paid';
SELECT COUNT(*) FROM big_orders;
```

---

## 70. Как применять CASE прямо в GROUP BY/HAVING? Пример реализации.
**Теория:**  
Можно группировать или фильтровать по выражению CASE.

**Пример реализации:**
```sql
SELECT
  CASE WHEN salary > 10000 THEN 'Высокая' ELSE 'Обычная' END AS salary_cat,
  COUNT(*)
FROM employees
GROUP BY salary_cat
HAVING COUNT(*) > 3;
```

---

## 71. Как использовать подстановки и шаблоны поиска в текстовых колонках? Пример реализации.
**Теория:**  
LIKE, SIMILAR TO, POSIX‑регекс для поиска по шаблону.

**Пример реализации:**
```sql
SELECT * FROM users WHERE email LIKE '%@gmail.com';
SELECT * FROM users WHERE email SIMILAR TO '%@%.%';
```

---

## 72. Как использовать подзапрос в WHERE с оператором IN для фильтрации? Пример реализации.
**Теория:**  
IN (подзапрос) фильтрует строки по значениям из подзапроса.

**Пример реализации:**
```sql
SELECT * FROM employees
WHERE department_id IN (SELECT id FROM departments WHERE active = true);
```

---

## 73. Как строить условия с EXISTS с учетом производительности (индексы, лимит)? Пример реализации.
**Теория:**  
Индекс ускоряет EXISTS; LIMIT 1 не нужен.

**Пример реализации:**
```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

---

## 74. Как переписать NOT IN на NOT EXISTS с учётом NULL‑значений? Пример реализации.
**Теория:**  
NOT EXISTS безопасен для NULL, NOT IN — нет.

**Пример реализации:**
```sql
SELECT * FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

---

## 75. Как использовать ANY для сравнения значения с набором (value = ANY(array/subquery))? Пример реализации.
**Теория:**  
ANY сравнивает значение с элементами массива или результатом подзапроса.

**Пример реализации:**
```sql
SELECT * FROM employees
WHERE department_id = ANY (SELECT id FROM departments WHERE active = true);
```

---

## 76. Что такое составной (composite) тип и как его определить? Пример реализации.
**Теория:**  
Composite тип — набор полей, определяемых как один тип.

**Пример реализации:**
```sql
CREATE TYPE address_type AS (city TEXT, zip TEXT);
CREATE TABLE users (
  id SERIAL,
  address address_type
);
```

---

## 77. Что такое подзапрос и где его можно использовать (SELECT, FROM, WHERE)? Пример реализации.
**Теория:**  
Подзапросы допустимы в SELECT, FROM, WHERE, HAVING.

**Пример реализации:**
```sql
SELECT name, (SELECT COUNT(*) FROM orders o WHERE o.customer_id = u.id) AS order_count
FROM users u;

SELECT * FROM (SELECT * FROM orders WHERE amount > 100) big_orders;

SELECT * FROM users WHERE id IN (SELECT customer_id FROM orders);
```

---

## 78. Как использовать COALESCE в ORDER BY для управления сортировкой NULL? Пример реализации.
**Теория:**  
COALESCE позволяет задать порядок сортировки для NULL.

**Пример реализации:**
```sql
SELECT * FROM employees
ORDER BY COALESCE(salary, 0) DESC;
```

---

## 79. Как агрегировать уникальные значения (COUNT(DISTINCT …), SUM(DISTINCT …))? Пример реализации.
**Теория:**  
Агрегаты с DISTINCT считаются по уникальным значениям.

**Пример реализации:**
```sql
SELECT COUNT(DISTINCT department_id) FROM employees;
SELECT SUM(DISTINCT salary) FROM employees;
```

---

## 80. Как связать внешний запрос с подзапросом (коррелированный подзапрос)? Пример реализации.
**Теория:**  
В подзапросе используются данные из внешнего запроса.

**Пример реализации:**
```sql
SELECT name,
  (SELECT COUNT(*) FROM orders o WHERE o.customer_id = u.id) AS order_count
FROM users u;
```

---

## 81. Как писать читаемые шаблоны SIMILAR TO и сопровождать их тестами? Пример реализации.
**Теория:**  
Пишите шаблоны понятно, сопровождайте тест-запросами.

**Пример реализации:**
```sql
SELECT email FROM users WHERE email SIMILAR TO '%@%.%';
```
Тест: 'test@mail.com' проходит, 'testmail.com' — нет.

---

## 82. Как считать долю группы от общего итога через оконные функции? Пример реализации.
**Теория:**  
Доля = агрегат по группе / агрегат по всем строкам (через оконную функцию).

**Пример реализации:**
```sql
SELECT department_id,
  SUM(salary) AS dept_sum,
  SUM(salary) / SUM(SUM(salary)) OVER () AS dept_share
FROM employees
GROUP BY department_id;
```

---

## 83. Как использовать ROLLUP/CUBE/GROUPING SETS в PostgreSQL? Пример реализации.
**Теория:**  
Расширенные группировки для итогов по нескольким уровням.

**Пример реализации:**
```sql
SELECT department_id, SUM(salary)
FROM employees
GROUP BY ROLLUP(department_id);

SELECT department_id, job_id, SUM(salary)
FROM employees
GROUP BY CUBE(department_id, job_id);

SELECT department_id, job_id, SUM(salary)
FROM employees
GROUP BY GROUPING SETS ((department_id), (job_id), ());
```

---

## 84. Как ограничить подзапрос TOP‑N на каждую группу (ROW_NUMBER + фильтр)? Пример реализации.
**Теория:**  
ROW_NUMBER() + фильтр по номеру строки.

**Пример реализации:**
```sql
SELECT *
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
  FROM employees
) sub
WHERE rn <= 3;
```

---

## 85. Как задать шаблон с альтернативами через | в SIMILAR TO? Пример реализации.
**Теория:**  
| задаёт альтернативы.

**Пример реализации:**
```sql
SELECT * FROM users WHERE name SIMILAR TO '(Ivan|Maria)%';
```

---

## 86. Как создать ENUM‑тип со списком допустимых значений? Пример реализации.
**Теория:**  
ENUM — тип с ограниченным списком допустимых значений.

**Пример реализации:**
```sql
CREATE TYPE status_type AS ENUM ('active', 'inactive', 'pending');
CREATE TABLE users (id SERIAL, status status_type);
```

---

## 87. Как отрицать совпадение шаблона через NOT SIMILAR TO? Пример реализации.
**Теория:**  
NOT SIMILAR TO — TRUE если строка НЕ соответствует шаблону.

**Пример реализации:**
```sql
SELECT * FROM users WHERE email NOT SIMILAR TO '%@%.%';
```

---

## 88. Как выбирать данные из нескольких таблиц с JOIN в разделе FROM? Пример реализации.
**Теория:**  
JOIN объединяет строки из нескольких таблиц по условию.

**Пример реализации:**
```sql
SELECT e.name, d.name AS dept
FROM employees e
JOIN departments d ON e.department_id = d.id;
```

---

## 89. Как создавать анти‑ и полу‑соединения через EXISTS/NOT EXISTS?
**Теория:**  
- Полу‑соединение (`EXISTS`): возвращает строки, для которых есть связанные записи.
- Анти‑соединение (`NOT EXISTS`): возвращает строки, для которых нет связанных записей.

**Реализация:**
```sql
-- Полу‑соединение: клиенты с заказами
SELECT * FROM customers c WHERE EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- Анти‑соединение: клиенты без заказов
SELECT * FROM customers c WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.id
);
```

---

## 90. Как проверить, что строка состоит только из цифр с SIMILAR TO?
**Теория:**  
SIMILAR TO позволяет указать шаблон для числовых строк.

**Реализация:**
```sql
-- Только строки из цифр
SELECT * FROM test WHERE value SIMILAR TO '[0-9]+';
```

---

## 91. Как сравнить производительность SIMILAR TO и POSIX‑регекса?
**Теория:**  
POSIX‑регекс (`~`, `~*`) обычно быстрее и поддерживает индексацию по выражению. SIMILAR TO — медленнее, сложнее.

**Реализация:**
```sql
-- SIMILAR TO
SELECT * FROM test WHERE value SIMILAR TO '[0-9]+';

-- POSIX‑регекс
SELECT * FROM test WHERE value ~ '^[0-9]+$';

-- Для профилирования используйте EXPLAIN ANALYZE:
EXPLAIN ANALYZE SELECT * FROM test WHERE value ~ '^[0-9]+$';
```

---

## 92. Как упрощать CASE с помощью GREATEST/LEAST и bool‑выражений?
**Теория:**  
GREATEST/LEAST выбирает минимум/максимум; булевы выражения можно напрямую преобразовать в метки.

**Реализация:**
```sql
-- Минимальное значение между salary и 5000
SELECT GREATEST(salary, 5000) FROM employees;

-- Булево → текст
SELECT CASE WHEN active THEN 'Да' ELSE 'Нет' END AS active_label FROM users;
```

---

## 93. Как посчитать агрегат по подмножеству строк с FILTER (WHERE …)?
**Теория:**  
`FILTER` применяет агрегат только к строкам, удовлетворяющим условию.

**Реализация:**
```sql
SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE active) AS active_count
FROM users;
```

---

## 94. Как избежать ошибки «column must appear in the GROUP BY clause»?
**Теория:**  
В SELECT с GROUP BY можно использовать только агрегаты и столбцы из GROUP BY.

**Реализация:**
```sql
-- Верно: оба столбца — агрегат и группируемый
SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;

-- Ошибка: name не в GROUP BY
-- SELECT department_id, name, COUNT(*) FROM employees GROUP BY department_id; -- ошибка
```

---

## 95. Как переписать подзапрос с IN в EXISTS и когда это выгодно?
**Теория:**  
EXISTS быстрее при большом количестве значений или наличии NULL, IN проще для маленьких наборов.

**Реализация:**
```sql
-- IN
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

-- EXISTS
SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

---

## 96. Что такое SIMILAR TO и как он соотносится с LIKE и POSIX‑регекс?
**Теория:**  
- LIKE — простой шаблон (% и _)
- SIMILAR TO — расширенный шаблон (регулярные выражения)
- POSIX‑регекс — полнофункциональный регекс (`~`, `~*`)

**Реализация:**
```sql
-- LIKE: 'a%'
SELECT * FROM test WHERE name LIKE 'a%';

-- SIMILAR TO: '(a|b)%'
SELECT * FROM test WHERE name SIMILAR TO '(a|b)%';

-- POSIX‑регекс: ~
SELECT * FROM test WHERE name ~ '^(a|b)';
```

---

## 97. Когда подзапрос можно заменить на JOIN и почему это иногда быстрее?
**Теория:**  
JOIN быстрее для больших данных, если нужен весь набор; подзапрос — для проверки существования.

**Реализация:**
```sql
-- Подзапрос
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

-- JOIN
SELECT DISTINCT u.* FROM users u JOIN orders o ON u.id = o.user_id;
```

---

## 98. Как использовать DOMAIN в таблице и наследовать его ограничения?
**Теория:**  
DOMAIN хранит ограничения, которые наследуются колонкой.

**Реализация:**
```sql
CREATE DOMAIN positive_int AS INTEGER CHECK (VALUE > 0);
CREATE TABLE items (qty positive_int);
```

---

## 99. Как комбинировать COALESCE и NULLIF в одном выражении?
**Теория:**  
NULLIF устраняет конфликт/деление на ноль, COALESCE подставляет значение по умолчанию.

**Реализация:**
```sql
SELECT COALESCE(amount / NULLIF(qty, 0), 0) FROM items;
```

---

## 100. Как использовать массивы с ANY/ALL без подзапросов?
**Теория:**  
ANY/ALL можно использовать с литеральными массивами.

**Реализация:**
```sql
SELECT * FROM users WHERE id = ANY(ARRAY[1,2,3]);
SELECT * FROM employees WHERE salary > ALL(ARRAY[5000,10000]);
```
