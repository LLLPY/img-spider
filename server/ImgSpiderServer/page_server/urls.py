from django.urls import re_path
from page_server.views import *
urlpatterns=[
    
    re_path(r'keyword_list/',keyword_list,name='keyword_list'),
    
]