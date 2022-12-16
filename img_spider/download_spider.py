import queue
from urllib.request import urlretrieve
import os
import model.models as model
import conf.conf as conf
from typing import *
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor


# 用于下载的爬虫
class DownloadSpider:
    # 日志器
    logger = conf.img_spider_logger

    # 客户端
    client = conf.img_client
    img_queue = queue.Queue()  # 图片消费队列
    img_crawled_queue = queue.Queue()  # 下载完成的图片队列

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword
        self.logger.warning(f'[{self.__class__.__name__}]已启动...')

    # 下载图片
    @classmethod
    def download_img(cls, img_obj: model.Img) -> Dict:
        # 创建下载目录
        dirs = img_obj.save_path.rsplit(os.sep, 1)[0]
        try:
            if not os.path.isdir(dirs):
                os.makedirs(dirs)
        except:
            pass
        success = True
        msg = ''
        try:
            urlretrieve(img_obj.url, img_obj.save_path)
        except Exception as e:
            msg = e
            success = False
            img_obj.err_msg = str(e)
        return {'status': success, 'msg': msg, 'img_obj': img_obj}

    # 下载函数的回调
    @classmethod
    def download_img_callback(cls, msg) -> None:
        result = msg.result()
        status = result['status']
        success = ['失败', '成功'][status]
        img_obj = result['img_obj']

        if success == '成功':
            img_obj.download = model.Img.DOWNLOADED
        else:
            img_obj.download = model.Img.DOWNLOADERROR
        msg = result['msg']
        cls.logger.info(
            f'[{cls.__name__}]下载{success},msg:{msg},剩余{cls.img_queue.qsize()}待爬取...img_url:{img_obj.url}')
        cls.img_crawled_queue.put(img_obj)

    # 补充消费队列
    async def supply_img_queue(self) -> None:
        res = await self.client.get_undownload_img_list(self.keyword)

        if res['code'] == '200':
            img_dict_list = res['data']
            for img_dict in img_dict_list:
                img_obj = model.Img.to_obj(img_dict)
                self.img_queue.put(img_obj)
            self.logger.info(f'补充了张{len(img_dict_list)}图片到消费队列...')
        else:
            msg = res['msg']
            self.logger.warning(
                f'f[{self.__class__.__name__}]图片补充失败,msg:{msg}...')

    # 定时上传爬取完成的图片
    @classmethod
    async def timed_upload_img(cls) -> None:

        cls.logger.info(f'[{cls.__name__}]图片上传服务已启动...')
        start = time.time()
        while True:

            await asyncio.sleep(0)

            if cls.img_crawled_queue.qsize() > 20 or time.time() - start > 10:
                img_dict_list = []

                while not cls.img_crawled_queue.empty():
                    img_obj = cls.img_crawled_queue.get()
                    img_dict_list.append(img_obj.to_dict())

                if img_dict_list:
                    res = await cls.client.update_img(img_dict_list)

                    if res['code'] == '200':
                        cls.logger.info(
                            f'[{cls.__name__}]图片状态更新成功,上传了{len(img_dict_list)}个图片...')
                    else:
                        msg = res['msg']
                        cls.logger.warning(
                            f'[{cls.__name__}]图片状态更新失败,msg:{msg}...')

                start = time.time()

            print(1111,cls.img_crawled_queue.qsize())
            # end
            for _ in range(15):
                await asyncio.sleep(1)
                if cls.img_crawled_queue.qsize() > 0:
                    break
                else:
                    print('empty')
            else:
                cls.logger.warning(f'[{cls.__name__}]图片上传服务结束...')
                break

    # 下载图片
    async def download_imgs(self) -> None:
        self.logger.warning(f'[{self.__class__.__name__}]开始下载图片...')

        await self.supply_img_queue()
        while True:

            # 让出cpu
            await asyncio.sleep(0)

            task_count = 8
            th_pool = ThreadPoolExecutor(task_count)
            for _ in range(task_count):
                if not self.img_queue.empty():
                    img_obj = self.img_queue.get()
                    future = th_pool.submit(self.download_img, img_obj)
                    future.add_done_callback(self.download_img_callback)

            # 等待当前批次的下载任务完成之后再进行下一批次的任务进行
            th_pool.shutdown()

            # 结束下载
            if self.img_queue.empty():
                await self.supply_img_queue()
                # 如果连续15秒内队列中都没有新的数据，就结束爬取
                for _ in range(15):
                    await asyncio.sleep(1)
                    if not self.img_queue.empty():
                        break
                else:
                    self.logger.warning(
                        f'[{self.__class__.__name__}]图片下载结束...')
                    break

    # 并发运行
    @classmethod
    async def gather_task(cls, keyword: str) -> None:
        spider = cls(keyword)
        await asyncio.gather(
            spider.download_imgs(),
            spider.timed_upload_img(),

        )

    # 启动
    @classmethod
    def run(cls, keyword: str) -> None:
        asyncio.run(cls.gather_task(keyword))
