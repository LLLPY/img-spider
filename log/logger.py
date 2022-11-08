import logging
import os
import datetime


class MyLogger:

    def __init__(self, log_to_file=False) -> None:

        MyLogger.log_to_file = log_to_file
        # 创建对应的日志文件
        if log_to_file:
            now_date = datetime.datetime.now()
            cur_dir = os.path.abspath(__file__).rsplit(os.sep, 1)[0]
            log_dir = os.path.join(cur_dir, str(now_date.year), str(
                now_date.month), str(now_date.day))
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir)
            MyLogger.log_file = os.path.join(log_dir, 'img_spider.log')

    @classmethod
    def get_logger(cls):
        img_spider_logger = logging.getLogger('img_spider_logger')
        img_spider_logger.setLevel(logging.INFO)
        if cls.log_to_file:
            handler = logging.FileHandler(
                filename=cls.log_file, mode='a', encoding='utf8')

        else:
            handler = logging.StreamHandler()

        handler.setLevel(logging.INFO)
        formater = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
        handler.setFormatter(formater)
        img_spider_logger.addHandler(handler)
        return img_spider_logger


if __name__ == '__main__':
    logger=MyLogger().get_logger()
    logger.info('hello')


