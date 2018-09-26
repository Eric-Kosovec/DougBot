from collections import deque


class Vertex:

    def __init__(self, value):
        self.incident = []
        self.value = value
        self.decor = {}

    def add_edge(self, edge):
        if edge is not None and edge not in self.incident:
            self.incident.append(edge)

    def remove_edge(self, edge):
        if edge is not None and edge in self.incident:
            self.incident.remove(edge)

    def __str__(self):
        return f'{Vertex: {self.value}}'

    def __repr__(self):
        return f'Vertex({self.value})'


class Edge:

    def __init__(self, v1, v2, value=None):
        self.value = value
        self.v1 = v1
        self.v2 = v2
        v1.add_edge(self)
        v2.add_edge(self)
        self.decor = {}

    def connects(self, v1, v2):
        return (self.v1 == v1 and self.v2 == v2) or (self.v1 == v2 and self.v2 == v1)

    def __str__(self):
        return f'{Edge: {self.value}}'

    def __repr__(self):
        return f'Edge({self.v1}, {self.v2}, {self.value})'


class Graph:

    def __init__(self):
        self._vertices = []
        self._edges = []

    def add_vertex(self, vertex):
        if vertex is not None and vertex not in self._vertices:
            self._vertices.append(vertex)
            for edge in vertex.incident:
                self.add_edge(edge)

    def remove_vertex(self, vertex):
        if vertex is not None and vertex in self._vertices:
            for edge in vertex.incident:
                edge.v1.remove_edge(edge)
                edge.v2.remove_edge(edge)
                self.remove_edge(edge)
            self._vertices.remove(vertex)

    def add_edge(self, edge):
        if edge is not None and edge not in self._edges:
            self._edges.append(edge)
            self.add_vertex(edge.v1)
            self.add_vertex(edge.v2)

    def remove_edge(self, edge):
        if edge is not None and edge in self._edges:
            edge.v1.remove_edge(edge)
            edge.v2.remove_edge(edge)
            self._edges.remove(edge)

    @staticmethod
    def get_vertex_value(vertex):
        if vertex is not None:
            return vertex.value
        return None

    @staticmethod
    def set_vertex_value(vertex, value):
        prev_value = None
        if vertex is not None:
            prev_value = vertex.value
            vertex.value = value
        return prev_value

    @staticmethod
    def get_edge_value(edge):
        if edge is not None:
            return edge.value
        return None

    @staticmethod
    def set_edge_value(edge, value):
        prev_value = None
        if edge is not None:
            prev_value = edge.value
            edge.value = value
        return prev_value

    @staticmethod
    def neighbors(vertex):
        if vertex is None:
            return []
        neighbors = []
        for edge in vertex.incident:
            if edge.v1 == vertex:
                neighbors.append(edge.v2)
            else:
                neighbors.append(edge.v1)
        return neighbors

    @staticmethod
    def adjacent(v1, v2):
        if v1 is None or v2 is None:
            return False
        if v1 == v2:
            return False

        adjacency_list = v1.incident
        if len(v2.incident) < len(adjacency_list):
            adjacency_list = v2.incident

        for edge in adjacency_list:
            if edge.connects(v1, v2):
                return True

        return False

    def traverse(self, vertices=None, bfs=True, visit=None):
        if vertices is None:
            vertices = self._vertices

        for v in vertices:
            v.decor['VISITED'] = False

        # Attempt a search from each vertex in case of a forest
        for v in vertices:
            if v is not None and not v.decor['VISITED']:
                yield self._traverse_helper(v, bfs, visit)

    def _traverse_helper(self, vertex, bfs, visit):
        frontier = deque([vertex])

        if bfs:
            vertex.decor['VISITED'] = True
            yield vertex

        while len(frontier) > 0:
            if bfs:
                curr = frontier.popleft()
            else:
                curr = frontier.pop()



            frontier.extend(filter(lambda v: not v.decor['VISITED'], self.neighbors(curr)))

    def vertex_count(self):
        return len(self._vertices)

    def edge_count(self):
        return len(self._edges)


def main():
    g = Graph()
    v1 = Vertex(5)
    v2 = Vertex(6)
    g.add_vertex(v1)
    g.add_vertex(v2)
    g.add_edge(Edge(v1, v2))
    print(g.adjacent(v1, v2))
    print(g.neighbors(v1))
    print(g.neighbors(v2))
    print([list(x) for x in list(g.traverse())])


if __name__ == '__main__':
    main()
