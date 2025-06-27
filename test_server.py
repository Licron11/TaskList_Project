from http.server import ThreadingHTTPServer
import requests
import pytest
import time
import threading
from server import TaskListHandler


#Фикстура для запуска тестового сервера
@pytest.fixture(scope='module')
def http_server():
    server = ThreadingHTTPServer(('localhost', 8008), TaskListHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    time.sleep(0.1)
    base_url = f'http://localhost:{port}'
    yield base_url
    server.shutdown()
    thread.join()


#Тест создания новой задачи
def test_create_task(http_server):
    response = requests.post(f'{http_server}/tasks', json={'title': 'Test task'})
    assert response.status_code == 201
    data = response.json()
    assert 'id' in data
    assert data['title'] == 'Test task'
    assert data['done'] is False
    return data['id']


#Тест получения всех задач
def test_get_all_tasks(http_server):
    response = requests.get(f'{http_server}/tasks')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


#Тест получения только невыполненных задач
def test_get_unfinished_tasks(http_server):
    response = requests.get(f'{http_server}/tasks?status=unfinished')
    assert response.status_code == 200
    tasks = response.json()
    assert all(task['done'] is False for task in tasks)


#Тест отметки задачи как выполенной
def test_mark_task_done(http_server):
    response = requests.patch(f'{http_server}/tasks/1', json={'done': True})
    assert response.status_code == 200
    assert response.json()['done'] is True


#Тест удаления задачи
def test_delete_task(http_server):
    response = requests.delete(f'{http_server}/tasks/1')
    assert response.status_code == 204


#Тест удаления несуществующей задачи
def test_delete_nonexistent_task(http_server):
    response = requests.delete(f'{http_server}/tasks/999')
    assert response.status_code == 404