
## Запуск

1. Установить виртуальное окружение:
```bash
python -m venv venv
```
2. Запустить окружение:
```bash
venv/scripts/activate
```
3. Установить зависимости:
```bash
pip install -r requirements.txt
```
4. Отредактировать файл .env (пример в файле .env.example):
```bash
BOT_TOKEN=
SMTP_SERVER=smtp.yandex.ru
SMTP_PORT=587
EMAIL_USER=
EMAIL_PASSWORD=
```
5. Запустить приложение:
```bash
python main.py
```
