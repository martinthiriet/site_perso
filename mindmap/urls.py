from django.urls import path
from . import views
from django.urls import path, include


urlpatterns = [
    path("",views.mindmap,name="mindmap" ),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('signup/', views.signup, name='signup'),
    path('user/', views.user, name='user'),
    path('create_map/', views.create_map, name='create_map'),
    path('edit_map/', views.edit_map, name='edit_map'),
    path('delete_map/', views.delete_map, name='delete_map'),
    path("zoom/",views.zoom,name="zoom" ),
    path("add_node/",views.add_node,name="add_node" ),
    path("edit_node/",views.edit_node,name="edit_node" ),
    path("compile_add/",views.compile_add,name="compile_add" ),
    path("compile_edit/",views.compile_edit,name="compile_edit" ),
    path("rebuid_all/",views.rebuild_all,name="rebuild_all" ),
    path("delete_node/",views.delete_node,name="delete_node" ),
]