import sqlite3

class DBManager:
    def __init__(self, db_name='tasks.db'):
        """
        Ініціалізує менеджер бази даних.
        Підключається до вказаної бази даних SQLite та створює таблицю завдань, якщо вона не існує.

        Args:
            db_name (str): Ім'я файлу бази даних SQLite.
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Встановлює з'єднання з базою даних."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Підключено до бази даних: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Помилка підключення до бази даних: {e}")
            raise

    def _create_table(self):
        """Створює таблицю 'tasks', якщо вона не існує."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            print("Таблиця 'tasks' перевірена/створена.")
        except sqlite3.Error as e:
            print(f"Помилка створення таблиці: {e}")
            raise

    def add_task(self, user_id, description, status='Очікує'):
        """
        Додає нове завдання до бази даних.

        Returns:
            int: ID новоствореного завдання.
        """
        try:
            self.cursor.execute(
                "INSERT INTO tasks (user, description, status) VALUES (?, ?, ?)",
                (user_id, description, status)
            )
            self.conn.commit()
            task_id = self.cursor.lastrowid
            return task_id
        except sqlite3.Error as e:
            print(f"Помилка додавання завдання: {e}")
            return None

    def update_task_status(self, task_id, new_status):
        """
        Оновлює статус завдання за його ID.
        """
        try:
            self.cursor.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (new_status, task_id)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Помилка оновлення статусу завдання {task_id}: {e}")
            return False

    def get_all_tasks(self):
        """
        Отримує всі завдання з бази даних.

        Returns:
            list: Список словників, кожен з яких представляє завдання.
        """
        try:
            self.cursor.execute("SELECT id, user, description, status, timestamp FROM tasks ORDER BY id")
            rows = self.cursor.fetchall()
            tasks = []
            for row in rows:
                tasks.append({
                    'id': row[0],
                    'user': row[1],
                    'description': row[2],
                    'status': row[3],
                    'timestamp': row[4]
                })
            return tasks
        except sqlite3.Error as e:
            print(f"Помилка отримання всіх завдань: {e}")
            return []

    def get_task_by_id(self, task_id):
        """
        Отримує завдання за його ID.

        Returns:
            dict: Словник з інформацією про завдання або None, якщо не знайдено.
        """
        try:
            self.cursor.execute("SELECT id, user, description, status, timestamp FROM tasks WHERE id = ?", (task_id,))
            row = self.cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'user': row[1],
                    'description': row[2],
                    'status': row[3],
                    'timestamp': row[4]
                }
            return None
        except sqlite3.Error as e:
            print(f"Помилка отримання завдання {task_id}: {e}")
            return None

    def close(self):
        """Закриває з'єднання з базою даних."""
        if self.conn:
            self.conn.close()
            print(f"З'єднання з базою даних {self.db_name} закрито.")

if __name__ == "__main__":
    db_manager = DBManager('test_tasks.db')

    task1_id = db_manager.add_task("TestUser1", "Приклад завдання 1")
    task2_id = db_manager.add_task("TestUser2", "Приклад завдання 2")
    print(f"Додано завдання з ID: {task1_id}, {task2_id}")

    if task1_id:
        db_manager.update_task_status(task1_id, "Виконано")
        print(f"Статус завдання {task1_id} оновлено.")

    all_tasks = db_manager.get_all_tasks()
    print("\nВсі завдання:")
    for task in all_tasks:
        print(task)

    if task2_id:
        retrieved_task = db_manager.get_task_by_id(task2_id)
        print(f"\nЗавдання {task2_id}: {retrieved_task}")

    db_manager.close()
    # Після виконання цього блоку буде створено файл test_tasks.db