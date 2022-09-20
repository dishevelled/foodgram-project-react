[![CI and CD](https://github.com/dishevelled/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/dishevelled/foodgram-project-react/actions/workflows/main.yml)

# Foodgram

Foodgram - это новая революционная сеть для публикации авторских рецептов.

## Стек технологий

- Проект написан на Python с использованием Django REST Framework;
- Djoser - аутентификация токенами;
- django-filter - фильтрация запросов;
- БД - PostgreSQL
- Система управления версиями - git
- [Docker](https://docs.docker.com/engine/install/ubuntu/), [Dockerfile](https://docs.docker.com/engine/reference/builder/), [Docker Compose](https://docs.docker.com/compose/).

## 1й этап

* Cоздать .env файл и заполнить:
    ```
    SECRET_KEY=<секретный ключ проекта django>
    DB_NAME=<имя базы данных postgresql>
    POSTGRES_USER=<пользователь базы данных>
    POSTGRES_PASSWORD=<пароль базы данных>
    DB_HOST=<название хоста базы данных>
    DB_PORT=<порт базы данных>
    ```

* Собрать статические файлы:
  ```
  python manage.py collectstatic --noinput
  ```
* Применить миграции:
  ```
  python manage.py migrate --noinput
  ```
Рабочая версия находится по адресу:
http://51.250.74.160/

Я.Практикум - Александр Чернышов.