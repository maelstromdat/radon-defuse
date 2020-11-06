from django.urls import path
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    path('repositories/get-github-repo/', views.get_github_repository, name='get_github_repo'),
    path('repositories/', TemplateView.as_view(template_name='repositories_index.html'), name='repositories_index'),
    path('repositories/<str:pk>/', views.repository_home, name='repository_home'),
    path('repositories/<str:pk>/dump/metrics/', views.repository_dump_metrics, name='repository_dump_metrics'),
    path('repositories/<str:pk>/dump/model/', views.repository_dump_model, name='repository_dump_model'),
    path('repositories/<str:pk>/fixing-commits', views.repository_fixing_commits, name='repository_fixing_commits'),
    path('repositories/<str:pk>/fixed-files', views.repository_fixed_files, name='repository_fixed_files'),
    path('repositories/<str:pk>/mine', views.repository_mine, name='repository_mine'),
    path('repositories/<str:pk>/train', views.repository_train_settings, name='repository_train_settings'),
    path('repositories/<str:pk>/start-train', views.repository_train_start, name='repository_train_start')
]
