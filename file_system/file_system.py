import pickle
import os




class MyPickle:

    def __init__(self, file_path: str):
        self.file_path = file_path

        if not os.path.isfile(self.file_path):
            path_list = file_path.split(os.sep)
            dir_list = path_list[:len(path_list)-1]
            dirs = os.sep.join(dir_list)  # 目录
            if len(dir_list) and not os.path.isdir(dirs):
                os.makedirs(dirs)
            self.dump(set())  # 初始化为一个空的集合

    # 从文件中加载对象
    def load(self):
        with open(self.file_path, 'rb') as f:
            return pickle.load(f)

    # 将对象写入文件
    def dump(self, obj):
        with open(self.file_path, 'wb') as f:
            pickle.dump(obj, f)




if __name__ == '__main__':
    my_pickle = MyPickle(file_path='data/demo')
    data_set = my_pickle.load()
    print(data_set)
    data_set.add("hello")
    data_set.add("world")
    my_pickle.dump(data_set)
