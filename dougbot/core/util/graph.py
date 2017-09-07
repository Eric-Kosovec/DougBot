class Edge:
    def __init__(self, v1, v2, element):
        self.v1 = v1
        self.v2 = v2
        self.element = element
        self.decoration = dict()
        return

    def get_element(self):
        return self.element

    def set_element(self, new_element):
        old_element = self.element
        self.element = new_element
        return old_element

    def get_vertex1(self):
        return self.v1

    def get_vertex2(self):
        return self.v2

    def put(self, key, value):
        old_value = None

        if key in self.decoration:
            old_value = self.decoration[key]

        self.decoration[key] = value

        return old_value

    def get(self, key):
        return self.decoration.get(key, None)

    def remove(self, key):
        value = None

        if key in self.decoration:
            value = self.decoration[key]
            del self.decoration[key]

        return value


class Vertex:
    def __init__(self, element):
        self.element = element
        self.incident_edges = []
        self.decoration = dict()
        return

    def get_element(self):
        return self.element

    def set_element(self, new_element):
        old_element = self.element
        self.element = new_element
        return old_element

    def get_incident_edges(self):
        return self.incident_edges

    def insert_edge(self, edge):
        self.incident_edges.append(edge)

    def remove_edge(self, edge):
        element = edge.get_element()
        self.incident_edges.remove(edge)
        return element

    def put(self, key, value):
        old_value = None

        if key in self.decoration:
            old_value = self.decoration[key]

        self.decoration[key] = value

        return old_value

    def get(self, key):
        return self.decoration.get(key, None)

    def remove(self, key):
        value = None

        if key in self.decoration:
            value = self.decoration[key]
            del self.decoration[key]

        return value


class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = []
        return

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges

    @staticmethod
    def incident_edges(vertex):
        return vertex.get_incident_edges()

    @staticmethod
    def opposite(vertex, edge):
        if not edge.get_vertex1() == vertex and not edge.get_vertex2() == vertex:
            return None
        if not edge.get_vertex1() == vertex:
            return edge.get_vertex1()
        else:
            return edge.get_vertex2()

    @staticmethod
    def end_vertices(edge):
        vertices = list()
        vertices.append(edge.get_vertex1())
        vertices.append(edge.get_vertex2())
        return vertices

    @staticmethod
    def are_adjacent(v1: Vertex, v2: Vertex):
        search_vertex = v1
        target_vertex = v2

        if len(v1.get_incident_edges()) > len(v2.get_incident_edges()):
            search_vertex = v2
            target_vertex = v1

        search_edges = search_vertex.get_incident_edges()

        for edge in search_edges:
            if ((edge.get_vertex1() == target_vertex and edge.get_vertex2() == search_vertex) or
                    (edge.get_vertex2() == target_vertex and edge.get_vertex1() == search_vertex)):
                return True

        return False

    @staticmethod
    def replace(vertex: Vertex, element):
        return vertex.set_element(element)

    @staticmethod
    def replace(edge: Edge, element):
        return edge.set_element(element)

    def insert_vertex(self, element):
        vertex = Vertex(element)
        self.vertices.append(vertex)
        return vertex

    def insert_edge(self, v1, v2, element):
        edge = Edge(v1, v2, element)

        v1.insert_edge(edge)
        v2.insert_edge(edge)

        self.edges.append(edge)

        return edge

    def remove_edge(self, edge):
        element = edge.get_element()

        edge.get_vertex1().remove_edge(edge)
        edge.get_vertex2().remove_edge(edge)

        self.edges.remove(edge)

        return element

    def remove_vertex(self, vertex):
        element = vertex.get_element()

        incident_edges = vertex.get_incident_edges()

        for edge in incident_edges:
            opposite_vertex = self.opposite(vertex, edge)
            opposite_vertex.remove_edge(edge)
            self.edges.remove(edge)

        vertex.incident_edges = []

        self.vertices.remove(vertex)

        return element
