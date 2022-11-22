import time
import functools

import sys,os
sys.path.append(f'..{os.sep}')

import conf.conf as conf

#协程计时器，计算函数执行耗时
def clocked(func):

    @functools.wraps(func)
    async def clock_it(*args,**kwargs):
        
        start=time.time_ns()
        res= await func(*args,**kwargs)
        end=time.time_ns()
        conf.img_spider_logger.info(f'func[{func.__name__}] done, costs {(end-start)/1000000000} s...')

        return res

    return clock_it
