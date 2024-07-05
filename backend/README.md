### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/vvvolokitin/foodgram
```

```
cd foodgram/backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если Linux/macOS

    ```
    source env/bin/activate
    ```

* Если вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

Подготовка к запуску через Docker:

Добавьте файл Dockerfile в корневую директорию проекта со следующим содержимым:

```
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver"]
```

Сборка образа:
Создайте образ Docker из вашего приложения:

```
docker build -t foodgram_backend .
```

Запуск контейнера:
Запустите контейнер с вашим приложением:

```
docker run -p 8000:8000 foodgram_backend
```
Эта команда запустит контейнер на порту 8000 вашего хоста.
Вы можете получить доступ к вашему приложению,
перейдя по адресу http://localhost:8000 в браузере.

Остановка контейнера:
Чтобы остановить контейнер, выполните команду:

```
docker stop <container_id>
```

Удаление контейнера:
Если вы больше не используете контейнер, удалите его с помощью команды:

```
docker rm <container_id>
```