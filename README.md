### Проект «Foodgram»

#### Описание проекта:
- Foodgram - это онлайн-платформа, где пользователи могут делиться своими рецептами, подписываться на публикации других участников, добавлять интересные рецепты в список «Избранное», а также перед выходом за покупками легко скачивать собранный список продуктов, необходимых для приготовления выбранных блюд.
#### Стек технологий:
- Python 3.9
- Django REST
- Postgres
- Nginx
- Docker Compose
- React
#### Как запустить проект:
- Клонировать репозиторий локально:
```
git clone git@github.com:bauman1922/foodgram-project-react.git
```
- Создать файл с переменными окружения в головной директории проекта:
```
touch .env

POSTGRES_USER="пользователь"
POSTGRES_PASSWORD="пароль"
POSTGRES_DB="имя"
DB_HOST=db
DB_PORT=5432
DEBAG=False
ALLOWED_HOSTS="список доменных имён и IP адресов"
SECRET_KEY="ключ Джанго из settings.py"
```
- Установить Docker на удаленном сервере:
```
sudo apt update
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose
```
- Создайте папку проекта foodgram:
```
mkdir foodgram
```
- Локально соберите образы для backend и frontend, запуште их на DockerHub и измените в файле docker-compose на свои образы
(image: bauman1922/foodgram_backend, bauman1922/foodgram_frontend).
- Перенести файлы docker-compose.yml, nginx.conf и .env, openapi-chema.yml и redoc.html на удаленный сервер.
- Запуcтите контейнеры на удаленном сервере:
```
sudo docker compose -f docker-compose.yml up -d
```
- Выполните миграции, соберите статику, создайте суперюзера, наполните предварительно бд ингредиентами:
```
sudo docker exec -it <имя контейнера backend> python manage.py migrate
sudo docker exec -it имя контейнера backend> python manage.py collectstatic
sudo docker-compose exec <имя контейнера backend> python manage.py createsuperuser
sudo docker exec -it <имя контейнера backend> python manage.py load_ingr
````
- Документация и примеры запросов:
```
server_ip/api/docs/
```
##### Автор
* [Sergey Samorukov](https://github.com/bauman1922)



