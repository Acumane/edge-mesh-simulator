from cascade import cascade

GRAPH: cascade.Cascade = cascade.Cascade()

def makeGraph(mesh):
    for controller in mesh.values():
        GRAPH.graph.addVert(controller.name)
        for target, weight in controller.hears.items():
            GRAPH.graph.addEdge(controller.name, target, weight)

def updateGraph(updates):
    return
