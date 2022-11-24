from django.shortcuts import render
from page_server.models import Keyword,Page
from django.http import JsonResponse
# Create your views here.


def keyword_list(request):
    
    if request.method == 'GET':
        
        keyword_list=Keyword.get_keyword_list()
        print(keyword_list)
        return JsonResponse({'keyword_list':keyword_list})