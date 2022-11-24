from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,JsonResponse
from img_server.models import Img
# Create your views here.


class ImgView(View):
    
    def get(self,request):
        return HttpResponse('hello!')


def get_img(request):
    
    if request.method == 'GET':
        keyword=request.GET.get('keyword')
    
        img_obj,success=Img.get_uncrawl_img_by_keyword(keyword)
        print(img_obj,success)
        
        return JsonResponse({'msg':''})
    