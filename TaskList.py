import json
import os

class TaskList:
    def __init__(self, filename='tasks.json'):
        self.filename = filename
        self.tasks = self.load_tasks()

    """Загрузка задач из Json"""
    def load_tasks(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return []

    """Сохранение задач в Json"""
    def save_tasks(self):
        with open(self.filename, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    """Добавление новой задачи"""
    def add_task(self, title):
        new_id = max(task['id'] for task in self.tasks) + 1 if self.tasks else 1
        new_task = {'id': new_id,
                    'title': title,
                    'done': False}
        self.tasks.append(new_task)
        self.save_tasks()
        return new_task

    """Отметить задачу как выполенную"""
    def mark_done(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['done'] = True
                self.save_tasks()
                return True
        return False

    """Получить все задачи"""
    def get_all_tasks(self):
        return self.tasks

    """Получить все невыполенные задачи"""
    def get_unfinished_tasks(self):
        return [task for task in self.tasks if not task['done']]

    """Удалить задачу"""
    def delete_task(self, task_id):
        initial_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if task['id'] != task_id]

        if len(self.tasks) < initial_count:
            for new_id, task in enumerate(self.tasks, start=1):
                task['id'] = new_id
            self.save_tasks()
            return True
        return False

def main():
    manager = TaskList()

    while True:
        print("\n1. Добавить задачу")
        print("2. Показать все задачи")
        print("3. Показать невыполненные задачи")
        print("4. Отметить задачу выполненной")
        print("5. Удалить задачу")
        print("6. Выйти")

        choice = input("Выберите действие: ")

        if choice == '1':
            title = input("Введите описание задачи: ")
            task = manager.add_task(title)
            print(f"Добавлена задача #{task['id']}")

        elif choice == '2':
            tasks = manager.get_all_tasks()
            if not tasks:
                print("Список задач пуст")
            else:
                for task in tasks:
                    status = "✓" if task['done'] else "✗"
                    print(f"{task['id']}. {task['title']} [{status}]")

        elif choice == '3':
            tasks = manager.get_unfinished_tasks()
            if not tasks:
                print("Нет невыполненных задач")
            else:
                for task in tasks:
                    print(f"{task['id']}. {task['title']} [✗]")

        elif choice == '4':
            try:
                task_id = int(input("Введите Номер задачи: "))
                if manager.mark_done(task_id):
                    print("Задача отмечена выполненной")
                else:
                    print("Задача не найдена")
            except ValueError:
                print("Ошибка: введите число")

        elif choice == '5':
            try:
                task_id = int(input("Введите Номер задачи: "))
                if manager.delete_task(task_id):
                    print("Задача удалена")
                else:
                    print("Задача не найдена")
            except ValueError:
                print("Ошибка: введите число")

        elif choice == '6':
            print("Выход")
            break

        else:
            print("Неверный ввод")


if __name__ == "__main__":
    main()