class Node:
    count = 0
    uid = 0
    
    def __init__(self,value,left=None,right=None):
        self.value = value
        self.left = left
        self.right = right
        self.id = None
        self.firstpos = set()
        self.lastpos = set() 
        self.followpos = set()
        self.nullable = None
        if value not in {"*","|","."}:
            Node.count += 1
            self.id = Node.count
            
    def __str__(self):
        return f"{self.firstpos}\n{self.lastpos}\n{self.followpos}\n{self.nullable}\n{self.value}"
        
    
         
  
