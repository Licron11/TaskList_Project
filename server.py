import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from TaskList import TaskList


class TaskListHandler(BaseHTTPRequestHandler):
    #Инициализация обработчика с пустым списком задач
    def __init__(self, *args, **kwargs):
        self.task_list = TaskList()
        super().__init__(*args, **kwargs)

    #Отправка успешного HTTP-ответа
    def _send_response(self, status_code, data=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if data is not None:
            self.wfile.write(json.dumps(data).encode('utf-8'))

    #Отправка ошибок
    def _send_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = {"error": message}
        self.wfile.write(json.dumps(error_response).encode('utf-8'))

    #Извлечение ID задачи из URL
    def _get_task_id_from_url(self):
        path_parts = self.path.split('/')
        if len(path_parts) < 3 or not path_parts[2].isdigit():
            return None
        return int(path_parts[2])

    #Обработка GET запросов для получения задач
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/tasks':
            query = parse_qs(parsed_url.query)
            if query.get('status') == ['unfinished']:
                tasks = self.task_list.get_unfinished_tasks()
            else:
                tasks = self.task_list.get_all_tasks()
            self._send_response(200, tasks)
        else:
            self._send_error(404, "Эндпоинт не найден")

    #Обработка POST запросов для добавления новых задач
    def do_POST(self):
        if self.path == '/tasks':
            content_length = int(self.headers['Content-Length'])
            try:
                post_data = json.loads(self.rfile.read(content_length))
            except json.JSONDecodeError:
                self._send_error(400, "Неверный формат JSON")
                return

            if 'title' not in post_data or not isinstance(post_data['title'], str):
                self._send_error(400, "Название задачи обязательно и должно быть строкой")
                return

            try:
                new_task = self.task_list.add_task(post_data['title'])
                self._send_response(201, new_task)
            except Exception as e:
                self._send_error(500, f"Ошибка при создании задачи: {str(e)}")
        else:
            self._send_error(404, "Эндпоинт не найден")

    #Обработка PATCH запросов для изменения статуса задачи на выполенный
    def do_PATCH(self):
        task_id = self._get_task_id_from_url()
        if not task_id:
            self._send_error(400, "Некорректный ID задачи")
            return

        content_length = int(self.headers['Content-Length'])
        try:
            patch_data = json.loads(self.rfile.read(content_length))
        except json.JSONDecodeError:
            self._send_error(400, "Неверный формат JSON")
            return

        if 'done' not in patch_data or not isinstance(patch_data['done'], bool):
            self._send_error(400, "Статус выполнения обязателен и должен быть булевым значением")
            return

        try:
            if patch_data['done']:

                success = self.task_list.mark_done(task_id)
                if not success:
                    self._send_error(404, "Задача не найдена")
                    return

                for task in self.task_list.tasks:
                    if task['id'] == task_id:
                        self._send_response(200, task)
                        return
            else:
                self._send_error(400, "Возможно ответить только как выполенным")
        except Exception as e:
            self._send_error(500, f"Ошибка при обновлении задачи: {str(e)}")

    #Обработка DELETE запросов для удаления задач
    def do_DELETE(self):
        task_id = self._get_task_id_from_url()
        if not task_id:
            self._send_error(400, "Некорректный ID задачи")
            return

        try:
            success = self.task_list.delete_task(task_id)
            if success:
                self.send_response(204)
                self.end_headers()
            else:
                self._send_error(404, "Задача не найдена")
        except Exception as e:
            self._send_error(500, f"Ошибка при удалении задачи: {str(e)}")


#Запуск сервера
if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8008
    server = ThreadingHTTPServer((host, port), TaskListHandler)
    server.serve_forever()
