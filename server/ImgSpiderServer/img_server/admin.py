from django.contrib import admin
from img_server.models import Img
# Register your models here.



@admin.register(Img)
class ImgAdmin(admin.ModelAdmin):
    
    save_on_top=True
    save_on_bottom=True
    list_select_related=True
    save_as=True
    list_display=['id',
                  'keyword',
                'status',
                'crawl_time',
                  'url',
                  'thumb_url',
                'page_url',
                  'uid',
                  'desc',
                  ]
    
    
    