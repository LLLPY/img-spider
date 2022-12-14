

class A:
    
    def __init__(self,name):
        self.name=name
    
    
    def __hash__(self):
        return len(self.name)
    
    


    



a=set()

demo1=A('qq')
demo2=demo1
a.add(demo1)
print(demo2 in a)