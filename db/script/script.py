import requests
import json
import time
from collections import defaultdict

# Словарь для хранения уникальных вопросов по темам
questions_by_topic = defaultdict(set)


def get_random_question(topic_id):
    url = "https://palchevsky.ru/index.php"
    params = {
        "rest_route": "/qa/v1/random-question",
        "topic_id": topic_id
    }
    headers = {
        "X-WP-Nonce": "7b76960c2e",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        if data.get("success"):
            return data.get("question", "Вопрос не найден")
        else:
            return f"Ошибка: {data.get('message', 'Неизвестная ошибка')}"

    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {str(e)}"
    except json.JSONDecodeError:
        return "Ошибка обработки ответа сервера"


def save_questions_to_file(questions_dict, filename):
    """Сохраняет вопросы в файл с группировкой по темам"""
    with open(filename, 'w', encoding='utf-8') as f:
        for topic_name, questions in questions_dict.items():
            f.write(f"{topic_name}:\n")
            for i, question in enumerate(questions, 1):
                f.write(f"  {i}. {question}\n")
            f.write("\n" + "=" * 80 + "\n\n")

    print(f"Вопросы сохранены в файл: {filename}")


if __name__ == "__main__":
    # ID темы (можно найти в data-topic-id кнопок на странице)
    topic_ids = {
         "Тема 4. Основы синтаксиса SQL в PostgreSQL": 421        # Добавьте другие topic_id по необходимости
    }

    # Количество итераций для сбора вопросов
    iterations = 1000

    for i in range(iterations):
        print(f"Итерация {i + 1}/{iterations}")

        for topic_name, topic_id in topic_ids.items():
            # Добавляем небольшую задержку между запросами
            time.sleep(0.5)

            question = get_random_question(topic_id)

            # Проверяем, не является ли ответ ошибкой
            if not question.startswith("Ошибка"):
                # Добавляем вопрос в множество (автоматически убирает повторы)
                questions_by_topic[topic_name].add(question)

                print(f"{topic_name}: {question}")
                print(f"Уникальных вопросов в теме: {len(questions_by_topic[topic_name])}")
            else:
                print(f"Ошибка при получении вопроса: {question}")

            print("-" * 50)

    # Сохраняем все собранные вопросы в файл
    save_questions_to_file(questions_by_topic, "4.txt")

    # Выводим статистику
    print("\nСтатистика сбора вопросов:")
    for topic_name, questions in questions_by_topic.items():
        print(f"{topic_name}: {len(questions)} уникальных вопросов")