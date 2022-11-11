# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/6 22:05  


# 1.根据url爬取页面
# 2.解析页面内容，抽取需要的部分
# 3.

import asyncio
from spider.baidu_spider import run_baidu_spider

async def main():
    keyword='大海'
    await run_baidu_spider(keyword)



if __name__ == '__main__':
    asyncio.run(main())


