# Foodgram

## Содержание

- [Описание](#описание)
- [Стек технологий](#стеек=технологий)
- [Как запустить проект](#как-запустить-проект)
- [Примеры запросов](#примеры-запросов)
- [Команда проекта](#команда-проекта)

### Описание:

[Foodgram](http://yc-foodgram.zapto.org/) - Блог для публикации рецептов.

### Стек технологий

- Python
- Django
- Django REST framework
- Nginx
- Docker
- JavaScrip

### Как запустить проект:

1. Клонируйте репозиторий на свой компьютер:

```
git clone https://github.com/vvvolokitin/foodgram
```

```
cd foodgram_backend
```
2. Создать файл .env и заполните его данными.

```

POSTGRESQL=django.db.backends.postgresql
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
DEBUG=False
SECRET_KEY='указать секретный ключ'
ALLOWED_HOSTS='указать разрешенные адреса'
URL_HOST= url для короткой ссылки
```
3. Запустить docker-compose.production:

```
sudo docker compose -f docker-compose.production.yml up
```

4. Выполнить миграции, сбор статики:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/backend_static/. /backend_static/static/
```
5. Выполнить импорт ингредиентов в БД:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py importdata
```
### Примеры запросов

```
Добавить рецепт: POST /recipes/create

Редактировать рецепт: PUTCH /recipes/{id}/edit

Просмотр рецептов: GET /recipes/

Просмотр рецепта: GET /recipes/{id}

Получить короткую ссылку на рецепт: GET /api/recipes/{id}/get-link/


```

### Команда проекта:

- [Волокитин Никита](https://github.com/vvvolokitin) — backend developer
