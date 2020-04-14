import heapq

class AStarQueue(object):
    def __init__(self):
        self.myheap = []

    def show(self):
        return self.myheap

    def push(self, priority, distance, node):
        heapq.heappush(self.myheap, (priority, distance, node))

    def pop(self):
        priority, distance, node = heapq.heappop(self.myheap)
        return priority, distance, node


# Create a priority queue
class PriorityQueue(object):
    def __init__(self):
        self.myheap = []

    def show(self):
        return self.myheap

    def push(self, priority, node):
        heapq.heappush(self.myheap, (priority, node))

    def pop(self):
        priority, node = heapq.heappop(self.myheap)
        return priority, node


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