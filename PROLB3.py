import time
from collections import deque
import numpy as np

from db_manager import DBManager  # Імпортуємо наш клас DBManager


class TaskManager:
    def __init__(self, db_name='tasks.db'):
        """
        Ініціалізує менеджер завдань.
        Містить чергу завдань (queue) та використовує DBManager для взаємодії з базою даних.
        """
        self.db_manager = DBManager(db_name)
        self.task_queue = deque()
        self._load_pending_tasks_to_queue()
        print("\n--- Симуляція багатокористувацької системи з чергою завдань (з SQLite) ---")

    def _load_pending_tasks_to_queue(self):
        """
        Завантажує завдання зі статусом 'Очікує' або 'В процесі' з БД у чергу.
        """
        all_db_tasks = self.db_manager.get_all_tasks()
        for task in all_db_tasks:
            if task['status'] == 'Очікує' or task['status'] == 'В процесі':
                self.task_queue.append(task['id'])
        print(f"Завантажено {len(self.task_queue)} завдань у чергу з БД.")
        self.display_queue_status()

    def add_task(self, user_id, task_description):
        """
        Додає нове завдання до бази даних та до черги.
        """
        task_id = self.db_manager.add_task(user_id, task_description, 'Очікує')
        if task_id is not None:
            self.task_queue.append(task_id)
            print(f"[{user_id}] Додано завдання: ID {task_id} - '{task_description}'")
        self.display_queue_status()

    def process_next_task(self):
        """
        Обробляє наступне завдання з черги.
        """
        if not self.task_queue:
            print("Черга завдань порожня. Немає завдань для обробки.")
            return False

        task_id = self.task_queue.popleft()
        task_info = self.db_manager.get_task_by_id(task_id)

        if task_info:
            self.db_manager.update_task_status(task_id, 'В процесі')
            print(
                f"\n[Система] Обробка завдання: ID {task_id} від користувача '{task_info['user']}' - '{task_info['description']}'")
            time.sleep(1)

            if np.random.rand() < 0.8:
                new_status = 'Виконано'
            else:
                new_status = 'Помилка'

            self.db_manager.update_task_status(task_id, new_status)
            print(f"[Система] Завдання ID {task_id} - '{task_info['description']}' - Статус: {new_status}.")
        else:
            print(f"[Система] Помилка: Завдання ID {task_id} не знайдено в базі даних.")
            return False

        self.display_queue_status()
        return True

    def display_queue_status(self):
        """
        Відображає поточний стан черги (ID завдань).
        """
        print(f"Поточний стан черги (ID): {list(self.task_queue)}")

    def display_all_tasks_status(self):
        """
        Відображає статус всіх завдань, зчитаних з бази даних.
        """
        print("\n--- Загальний статус всіх завдань (з БД) ---")
        all_tasks = self.db_manager.get_all_tasks()
        if not all_tasks:
            print("Немає завдань у базі даних.")
            return

        print(f"{'ID':<5} | {'Користувач':<15} | {'Статус':<10} | {'Опис':<30} | {'Час створення':<20}")
        print("-" * 90)
        for task in all_tasks:
            print(
                f"{task['id']:<5} | {task['user']:<15} | {task['status']:<10} | {task['description']:<30} | {task['timestamp']:<20}")
        print("-" * 90)

    def generate_report(self):
        """
        Генерує звіт про оброблені та необроблені завдання, зчитані з бази даних.
        """
        print("\n--- Звіт про обробку завдань (з БД) ---")
        all_tasks = self.db_manager.get_all_tasks()

        processed_count = 0
        unprocessed_count = 0
        processed_list = []
        unprocessed_list = []

        for task in all_tasks:
            if task['status'] == 'Виконано':
                processed_count += 1
                processed_list.append(task)
            elif task['status'] == 'Помилка':
                unprocessed_count += 1
                unprocessed_list.append(task)

        print(f"Всього зареєстровано завдань у БД: {len(all_tasks)}")
        print(f"Кількість успішно оброблених завдань: {processed_count}")
        print(f"Кількість завдань, що завершилися з помилкою: {unprocessed_count}")

        if processed_list:
            print("\nУспішно оброблені завдання:")
            for task in processed_list:
                print(f"- ID {task['id']} (Користувач: {task['user']}, Опис: '{task['description']}')")
        else:
            print("\nНемає успішно оброблених завдань.")

        if unprocessed_list:
            print("\nНеоброблені (з помилкою) завдання:")
            for task in unprocessed_list:
                print(f"- ID {task['id']} (Користувач: {task['user']}, Опис: '{task['description']}')")
        else:
            print("\nНемає завдань, що завершилися з помилкою.")

    def __del__(self):
        """
        Деструктор: гарантує закриття з'єднання з базою даних при завершенні роботи об'єкта.
        """
        self.db_manager.close()


if __name__ == "__main__":
    # Запустіть цей файл, і він створить/використає tasks.db
    manager = TaskManager('tasks.db')

    manager.add_task("UserA", "Надіслати звіт до 17:00")
    manager.add_task("UserB", "Створити новий проект")
    manager.add_task("UserC", "Відповісти на email")
    manager.add_task("UserA", "Забронювати переговорну")
    manager.add_task("UserB", "Підготувати презентацію")

    print("\n--- Початок обробки завдань ---")

    for _ in range(4):
        if not manager.process_next_task():
            break
        time.sleep(0.5)

    manager.add_task("UserD", "Перевірити базу даних")
    manager.add_task("UserC", "Оновити програмне забезпечення")

    while manager.task_queue:
        if not manager.process_next_task():
            break
        time.sleep(0.5)

    print("\n--- Обробка завдань завершена ---")

    manager.display_all_tasks_status()

    manager.generate_report()
