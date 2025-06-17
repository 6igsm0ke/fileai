from django.urls import path
from .views import upload_file

app_name = 'parser'

urlpatterns = [
    path('', upload_file, name='upload_file'),
]
