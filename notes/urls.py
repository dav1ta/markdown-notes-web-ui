from django.urls import path
from . import views

urlpatterns = [
    path('create-tab', views.create_tab, name='create_tab'),
    path('tab/create-subtab/', views.create_subtab, name='create_subtab'),
    path('tab/<int:tab_id>/', views.get_tab_content, name='get_tab_content'),
    path('tabs', views.home, name='home'),
    path('subtab/<int:subtab_id>', views.get_subtab, name='home'),
    path('subtab/<int:subtab_id>/update', views.update_markdown, name='toggle'),
    path('toggle/', views.toggle_edit_mode, name='tafff'),
    path('home/<int:subtab_id>/', views.home_subtab, name='tafff'),

]
