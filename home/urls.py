
from django.urls import path , include
from home import views

app_name = "home"  # This registers the namespace


urlpatterns = [
    path('', views.index, name='index'),
    path('blog-details/', views.blog_details, name='blog_details'),
    path('blog/', views.blog, name='blog'),

]
