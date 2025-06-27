import pytest
import json
import os
from TaskList import TaskList


# Фикстура для создания тестового списка задач
@pytest.fixture
def task_list(tmp_path):
    test_file = tmp_path / "test_tasks.json"
    return TaskList(filename=str(test_file))


# Тест инициализиции, если файл отсутствует
def test_init_if_no_file(task_list):
    assert task_list.tasks == []
    assert os.path.exists(task_list.filename) is False


# Тест инициализации, если файл существует
def test_init_with_file(tmp_path):
    test_file = tmp_path / "test_tasks.json"
    sample_task = [{"id": 1, "title": "Test", "done": False}]
    with open(test_file, 'w') as f:
        json.dump(sample_task, f)
    assert TaskList(filename=str(test_file)).tasks == sample_task


# Тест добавления задач
def test_add_task(task_list):
    task1 = task_list.add_task("Task 1")
    assert task1 == {"id": 1, "title": "Task 1", "done": False}
    assert task_list.tasks == [task1]

    task2 = task_list.add_task("Task 2")
    assert task2["id"] == 2
    assert task_list.tasks == [task1, task2]


# Тест отметки задач как выполненных
def test_mark_done(task_list):
    task_list.add_task("Task 1")
    task_list.add_task("Task 2")

    assert task_list.mark_done(1) is True
    assert task_list.tasks[0]["done"] is True
    assert task_list.tasks[1]["done"] is False

    assert task_list.mark_done(999) is False


# Тест получения всех задач
def test_get_all_tasks(task_list):
    task_list.add_task("Task 1")
    task_list.add_task("Task 2")
    tasks = task_list.get_all_tasks()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 1"


# Тест получения только невыполенных задач
def test_get_unfinished_tasks(task_list):
    task_list.add_task("Task 1")
    task_list.add_task("Task 2")
    task_list.mark_done(1)

    unfinished = task_list.get_unfinished_tasks()
    assert len(unfinished) == 1
    assert unfinished[0]["title"] == "Task 2"


# Тест удаления задач
def test_delete_task(task_list):
    task_list.add_task("Task 1")
    task_list.add_task("Task 2")
    task_list.add_task("Task 3")

    assert task_list.delete_task(2) is True
    assert len(task_list.tasks) == 2

    assert [task["id"] for task in task_list.tasks] == [1, 2]
    assert [task["title"] for task in task_list.tasks] == ["Task 1", "Task 3"]

    assert task_list.delete_task(999) is False