# django_sprint4

## Запуск проекта

запустить виртуальное окружение
```
python -m venv venv
venv/Scripts/activate
```
установить зависимости
```
pip install -r requirements.txt
```
выполнить миграции таблиц БД
```
python manage.py migrate
```
применить тестовые данные
```
python manage.py loaddata db.json
```
запустить сервер
```
python manage.py runserver
```
