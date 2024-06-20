from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установка настроек по умолчанию для модуля celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmorpg_board.settings')

app = Celery('mmorpg_board')

# Загружаем настройки из конфигурационного файла settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в каждом установленном приложении
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
