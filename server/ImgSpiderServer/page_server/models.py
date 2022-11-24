from django.db import models


class Keyword(models.Model):
    
    #关键字
    keyword=models.CharField(max_length=50,db_column='关键字',verbose_name='关键字')

    #创建时间
    create_time=models.DateTimeField(db_column='创建时间',verbose_name='创建时间')
    
    class Meta:
        db_table= '关键字'
        verbose_name_plural = verbose_name = db_table  # admin 后台显示
        ordering=['create_time']
    
    @classmethod
    def get_keyword_list(cls):
        return [k[0] for k in cls.objects.values_list('keyword')]
        

    def __str__(self) -> str:
        return self.keyword
    
    
# Create your models here.
class Page(models.Model):

    #待爬取
    STATUS_UNCRAWL=0
    #爬取中
    STATUS_CRAWLIMG=1
    #已爬取
    STATUS_CRAWLED=2
    #状态映射
    STATUS_MAPPING=(
        (STATUS_UNCRAWL,'待爬取'),
        (STATUS_CRAWLIMG,'爬取中'),
        (STATUS_CRAWLED,'已爬取')
    )

 
  # 所属分类，根据哪个关键字爬取的就是哪个分类
    keyword = models.ForeignKey(Keyword,on_delete=models.CASCADE,db_column='关键字',verbose_name='关键字')
    
    url=models.URLField(db_column='页面地址',verbose_name='页面地址')
   # 唯一标识
    uid = models.CharField(max_length=100, db_column='唯一标识',verbose_name='唯一标识')
    # 爬取状态 
    status = models.IntegerField(default=STATUS_UNCRAWL,choices=STATUS_MAPPING,db_column='状态',verbose_name='状态')  
    # 爬取的时间
    crawl_time = models.DateTimeField(db_column='爬取时间',verbose_name='爬取时间')
    
    class Meta:
        db_table= '页面'
        verbose_name_plural = verbose_name = db_table  # admin 后台显示
        ordering=[]
    
    
    #根据keyword获取一个未爬取的页面对象

    
    def __str__(self) -> str:
        return self.url
