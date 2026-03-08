from typing import Callable, Generic, List, MutableMapping, TypeVar

T = TypeVar("T")


class Node(Generic[T]):
    def __init__(self, key: str, data: T) -> None:
        self.key = key
        self.data = data

        self.incoming: MutableMapping[str, Node[T]] = {}
        self.outgoing: MutableMapping[str, Node[T]] = {}


class Graph(Generic[T]):
    def __init__(self, hash_func: Callable[[T], str]) -> None:
        self._nodes: MutableMapping[str, Node[T]] = {}
        self.hash_func = hash_func

    def roots(self) -> List[Node[T]]:
        ret: List[Node[T]] = []

        for node in self._nodes.values():
            if len(node.outgoing) == 0:
                ret.append(node)

        return ret

    def insert_edges(self, from_data: T, to_data: T) -> None:
        from_node = self.lookup_or_insert_node(from_data)
        to_node = self.lookup_or_insert_node(to_data)

        from_node.outgoing[to_node.key] = to_node
        to_node.incoming[from_node.key] = from_node

    def remove_node(self, data: T) -> None:
        key = self.hash_func(data)
        self._nodes.pop(key)

        for node in self._nodes.values():
            node.outgoing.pop(key, None)
            node.incoming.pop(key, None)

    def lookup_or_insert_node(self, data: T) -> Node[T]:
        key = self.hash_func(data)
        node = self._nodes.get(key)
        if node is None:
            node = Node(key, data)
            self._nodes[key] = node

        return node

    def lookup(self, data: T) -> Node[T] | None:
        return self._nodes.get(self.hash_func(data))

    def is_empty(self) -> bool:
        return True if len(self._nodes) == 0 else False

    def to_string(self) -> str:
        data: list[str] = []
        for key, value in self._nodes.items():
            data.append(
                f"{key}\n\t(-> incoming)[{','.join(value.incoming.keys())}]\n\t(outgoing ->)[{','.join(value.outgoing.keys())}]\n"
            )

        return "\n ".join(data)

    def __repr__(self) -> str:
        return self.to_string()

    def find_cycle_slow(self) -> str | None:
        for start_id, node in self._nodes.items():
            seen: set[str] = {start_id}
            res = self.__find_cycle(node, seen)

            if res is not None:
                return res

        return None

    def __find_cycle(self, node: Node[T], seen: set[str]) -> str | None:
        for neighbor_id, outgoing in node.outgoing.items():
            if neighbor_id in seen:
                cycle = list(seen) + [neighbor_id]
                return " -> ".join(cycle)
            seen.add(neighbor_id)
            value = self.__find_cycle(outgoing, seen)
            if value is not None:
                return value
            seen.remove(neighbor_id)
        return None
