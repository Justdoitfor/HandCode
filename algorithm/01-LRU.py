class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value

        self.prev = None
        self.next = None


class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity        # 缓存容量
        self.cache = {}                 # 缓存字典存储 key-node映射
        self.head = Node()              # 虚拟头节点
        self.tail = Node()              # 虚拟尾节点
        self.head.next = self.tail      # 初始化头节点的后继为 尾节点
        self.tail.prev = self.head      # 初始化尾节点的前驱为 头节点

    def remove(self, node: Node) -> None:
        node.next.prev = node.prev      # 当前节点的后继节点的前驱指向当前节点的前驱节点
        node.prev.next = node.next      # 当前节点的前驱节点的后继节点指向当前节点的后继节点

    def add_to_tail(self, node: Node) -> None:
        node.next = self.tail           # 当前节点后继指向尾节点
        node.prev = self.tail.prev      # 当前节点前驱指向原来尾节点的前驱节点

        self.tail.prev.next = node      # 原来尾节点的前驱节点的后继指向当前节点
        self.tail.prev = node           # 原来尾节点的前驱节点指向当前节点

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1

        node = self.cache[key]          # 从缓存中查看key对应的 node
        self.remove(node)               # 移除已经使用的 node
        self.add_to_tail(node)          # 将该 node 插入到尾节点的前驱位置表示更新为最近使用
        return node.value               # 返回获取的 node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]      # 当key存在于缓存中时，通过cache可以查找到 key 对应的 node
            node.value = value          # 更新node对应的value, cache中存在的是node引用会随之更新对应的value
            self.remove(node)           # 移除原来较长时间未使用，现在使用了的node
            self.add_to_tail(node)      # 将更新的node插入最近使用位置
            return                      # 如果key在cache中，此时已经插入结束
        node = Node(key, value)         # 如果key不在cache中，需要创建node并插入
        self.cache[key] = node          # cache中记录新 key 对应的 node
        self.add_to_tail(node)          # 添加到最近使用的位置

        if len(self.cache) > self.capacity:
            lru = self.head.next        # 最近最久未使用的节点
            self.remove(lru)            # 移除最近最久未使用的节点
            del self.cache[lru.key]     # 同步移除缓存中对应的 key
