from django.conf.urls import url

from app01.views import register

urlpatterns = [
    url(r'^register', register, name='register'), #'app01:register'
]