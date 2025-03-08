
from django.urls import path , include
from home import views

app_name = "home"  # This registers the namespace


urlpatterns = [
    path('', views.index, name='index'),
    

]
