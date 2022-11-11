import time
import functools


#计时器，计算函数执行耗时



def clocked(func):

    @functools.wraps(func)
    def clock_it(*args,**kwargs):
        
        start=time.time_ns()
        res= func(*args,**kwargs)
        end=time.time_ns()

        print(f'func[{func.__name__}] costs {(end-start)/1000000000} s')
        return res
    return clock_it
