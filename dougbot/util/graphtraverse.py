# TODO EXTEND USABILITY, E.G. METHOD FOR VISITING
# METHOD FOR RETURNING A RESULT MAYBE


def bfs(graph, start_vertex, goal_vertex):
    frontier = []

    for vertex in graph.get_vertices():
        vertex.put("VISITED", False)

    for edge in graph.get_edges():
        edge.put("VISITED", False)

    start_vertex.put("VISITED", True)

    frontier.append(start_vertex)

    while len(frontier) > 0:
        curr_vertex = frontier.pop(0)

        if goal_vertex is not None and curr_vertex == goal_vertex:
            return curr_vertex

        incident_edges = graph.incident_edges(curr_vertex)

        for edge in incident_edges:
            if not edge.get("VISITED"):
                opp_vertex = graph.opposite(curr_vertex, edge)

                # Not seen, so the current edge is a discovery edge.
                # Also, indicate we have seen the vertex and how we
                # got to it.
                if not opp_vertex.get("VISITED"):
                    # Visit the opposite vertex
                    opp_vertex.put("VISITED", True)
                    frontier.append(opp_vertex)

                edge.put("VISITED", True)

    return None


def _next_edge(graph, vertex):
    incident_edges = graph.incident_edges(vertex)

    for edge in incident_edges:
        if not edge.get("VISITED"):
            opp_vertex = graph.opposite(vertex, edge)

            if not opp_vertex.get("VISITED"):
                return edge

    return None


def dfs(graph, start_vertex):
    frontier = []

    for vertex in graph.get_vertices():
        vertex.put("VISITED", False)

    for edge in graph.get_edges():
        edge.put("VISITED", False)

    start_vertex.put("VISITED", True)

    frontier.append(start_vertex)

    while len(frontier) > 0:
        # Peek the stack top
        curr_vertex = frontier[-1]

        # Find the next edge to cross
        edge = _next_edge(graph, curr_vertex)

        # No adjacent vertices that are unvisited
        if edge is None:
            frontier.pop()

        else:
            opp_vertex = graph.opposite(curr_vertex, edge)

            # Visit the opposite vertex
            opp_vertex.put("VISITED", True)
            edge.put("VISITED", True)

            # Push onto stack the next vertex
            frontier.append(opp_vertex)

    return
