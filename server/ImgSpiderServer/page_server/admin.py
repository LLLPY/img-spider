from django.contrib import admin
from page_server.models import Keyword,Page
# Register your models here.

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    save_on_top=True
    save_on_bottom=True
    list_select_related=True
    save_as=True
    
    list_display=['id',
                  'keyword',
                'create_time'
                  ]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    save_on_top=True
    save_on_bottom=True
    list_select_related=True
    save_as=True
    
    list_display=['id',
                  'keyword',
                  'url',
                  'status',
                'crawl_time'
                  ]