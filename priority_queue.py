import heapq

# Create a priority queue that doesn't add duplicate nodes
class PrioritySet(object):
    def __init__(self):
        self.myheap = []
        self.myset = set()

    def show(self):
        return self.myheap

    def push(self, priority, node):
        if not node in self.myset:
            heapq.heappush(self.myheap, (priority, node))
            self.myset.add(node)

    def pop(self):
        priority, node = heapq.heappop(self.myheap)
        self.myset.remove(node)
        return priority, node