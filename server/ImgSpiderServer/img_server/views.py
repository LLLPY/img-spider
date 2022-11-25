from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,JsonResponse
from img_server.models import Img
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


class ImgView(View):
    
    def get(self,request):
        return HttpResponse('hello!')

#根据keyword，返回该keyword下未爬取的图片
def get_img(request):
    
    if request.method == 'GET':
        keyword=request.GET.get('keyword')
    
        img_obj,success=Img.get_uncrawl_img_by_keyword(keyword)
        print(img_obj,success)
        
        return JsonResponse({'msg':''})

#上传图片
# @csrf_exempt
def upload_img(request):
    print(request.method)
    if request.method == 'POST':
        print(6666)
        img_list=request.POST.items()
        print(111,img_list)
        
        return JsonResponse({'msg':img_list})
