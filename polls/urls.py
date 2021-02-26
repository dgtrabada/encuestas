from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:questionarie_id>/votar/', views.votar, name='votar'),
    path('login/', views.login, name='login'),
    path('view_pdf/', views.view_pdf, name='view_pdf'),
    path('activar_usuarios/', views.activar_usuarios, name='activar_usuarios'),
    path('<int:questionarie_id>/resultados/', views.resultados, name='resultados'),
    path('/grupo_resultados/', views.grupo_resultados, name='grupo_resultados'),
    path('/gestion_usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('/gestion_encuestas/', views.gestion_encuestas, name='gestion_encuestas'),
    path('/crear_usuarios/', views.crear_usuarios, name='crear_usuarios'),
    path('/crear_usuarios_definitivo/', views.crear_usuarios_definitivo, name='crear_usuarios_definitivo'),
    path('/crear_encuestas/', views.crear_encuestas, name='crear_encuestas'),
    path('/cambiar_passwd/', views.cambiar_passwd, name='cambiar_passwd'),
    path('/cambiar_passwd_definitivo/', views.cambiar_passwd_definitivo, name='cambiar_passwd_definitivo'),
#    path('detail/', views.DetailView, name='detail'),
    path('<int:questionarie_id>/detail/', views.DetailView, name='detail')
    ]

