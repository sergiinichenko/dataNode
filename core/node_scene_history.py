
from graphics.graphics_edge import GraphicsEdge


DEBUG = False

class SceneHistory():
    def __init__(self, scene):
        self.scene = scene

        self.history_stack        = []
        self.history_current_step = -1
        self.history_limit        = 32

    def undo(self):
        if DEBUG : print("UNDO")
        if self.history_current_step > 0:
            self.history_current_step -= 1
            self.restoreHistory()

    def redo(self):
        if DEBUG : print("REDO")
        if self.history_current_step + 1 < len(self.history_stack) :
            self.history_current_step += 1
            self.restoreHistory()



    def restoreHistory(self):
        if DEBUG : print("Restoring the history ... current step: @%d" % self.history_current_step, 
        "(%d)" % len(self.history_stack))
        self.restoreHistoryStamp(self.history_stack[self.history_current_step])
    


    def storeHistory(self, desc):
        if DEBUG : print("Storing the history", "{0}".format(desc) , 
                         " ... current step: %d" % self.history_current_step, 
                         "(%d)" % len(self.history_stack))

        # if the current step is not at the end of the history stack
        if self.history_current_step +1 < len(self.history_stack):
            self.history_stack = self.history_stack[:self.history_current_step+1]

        # check the history stack size limit
        if self.history_current_step + 1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        hs = self.createHistoryStamp(desc)
        self.history_stack.append(hs)
        self.history_current_step += 1
        
        if DEBUG : print("  --- setting step to:", self.history_current_step)



    def restoreHistoryStamp(self, history_stamp):
        if DEBUG : print("RHS: ", history_stamp)
        self.scene.deserialize(history_stamp['snapshot'])

        # restore selection
        for edge_id in history_stamp['selection']['edges']:
            for edge in self.scene.edges:
                if edge.id == edge_id:
                    edge.grEdge.setSelected(True)
                    break

        for node_id in history_stamp['selection']['nodes']:
            for node in self.scene.nodes:
                if node.id == node_id:
                    node.grNode.setSelected(True)
                    break


    def createHistoryStamp(self, desc):
        if DEBUG : print("SHS: ", desc)
        self_obj = {
            "nodes" : [],
            "edges" : []
        }

        for item in self.scene.grScene.selectedItems():
            if hasattr(item, "node"):
                self_obj['nodes'].append(item.node.id)
            elif isinstance(item, GraphicsEdge):
                self_obj['edges'].append(item.edge.id)

        history_stamp = {
            "desc"      : desc,
            "snapshot"  : self.scene.serialize(),
            "selection" : self_obj
        }

        return history_stamp
