# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/12/18 21:20  

# 工人
import time
from concurrent.futures.thread import ThreadPoolExecutor
from webbrowser import Chrome

from conf import conf


class ChromeWorker:
    STATUS_READY = 0
    STATUS_RUNNING = 1
    STATUS_DONE = 2

    def __init__(self) -> None:
        self.status = self.STATUS_READY  # 0:待启动 1:运行中 2:运行结束
        self.chrome = Chrome(
            service=conf.CHROMEDRIVER_SERVICE, options=conf.chrome_options)

    # 启动
    def start(self, img_obj):
        self.status = self.STATUS_RUNNING
        res = self.chrome.get(img_obj.url)
        time.sleep(1)
        self.status = self.STATUS_DONE
        return res, img_obj

    def is_ready(self):
        return self.status == self.STATUS_READY

    # callback
    def done(self, msg):
        res = msg.result()
        self.status = self.STATUS_READY
        return res

    def close(self):
        self.chrome.close()


# 监工
class ChromeWorkerManager:
    instance = None

    def __init__(self, workrom_size=5):
        self.workroom = [ChromeWorker() for _ in range(workrom_size)]

    # 分配任务
    def dispatch(self, url_list):
        th_pool = ThreadPoolExecutor(len(self.workroom))
        for i in range(len(self.workroom)):
            if self.workroom[i].is_ready() and url_list:
                future = th_pool.submit(self.workroom[i].start, url_list.pop())
                future.add_done_callback(self.workroom[i].done)
        th_pool.shutdown()

    # 关闭所有任务
    def done(self):
        for i in range(len(self.workroom)):
            self.workroom[i].close()
