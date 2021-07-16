
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
import re

class SeparateDFGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160.0
        self.height = 200.0

class SeparateDFContent(NodeContentWidget):
    def initUI(self):
        self.operation = "To Float"
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Data Separate")

    def serialize(self):
        res = super().serialize()
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        res['content-widht'] = self.size().width()
        res['content-height'] = self.size().height()
        return res


    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.grNode.height = data['height']
            self.node.grNode.width  = data['width']
            self.resize(data['content-widht'], data['content-height'])
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_SEP)
class SeparateDFNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_SEP
    op_title = "Data Separate"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP


    def initInnerClasses(self):
        self.content = SeparateDFContent(self)
        self.grNode  = SeparateDFGraphicsNode(self)


    def generateSockets(self, data, names=None):
        self.clearOutputs()        
        outputs = [SOCKET_DATA_TEXT for l in range(len(data)+1)]
        dnames = ['DATA']
        if names is not None: dnames.extend(names)
        self.createOutputs(outputs, dnames)
        self.grNode.height = (len(data)+1) * self.socket_spacing + 2.0 * self.socket_spacing
        self.grNode.update()

        self.border_radius = 10.0
        self.padding       = 10.0
        self.title_height = 24.0
        self._hpadding     = 5.0
        self._vpadding     = 5.0

        x, y = self.grNode.width - 2.0 * self.grNode.padding, (len(data)+1) * self.socket_spacing + 2.0 * self.socket_spacing - self.grNode.title_height - 2.0 * self.grNode.padding
        self.content.resize(x, y)


    def evalImplementation(self):
        input_edge = self.getInput(0)

        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False

        else:
            self.setDirty(False)
            self.setInvalid(False)
            if DEBUG : print("PRCNODE_SEP: reset dirty and invalid")
            self.e     = ""
            self.value = input_edge.value
            self.type  = input_edge.type
            if DEBUG : print("PRCNODE_SEP: get input value and type")

            if isinstance(self.value, dict):
                if DEBUG : print("PRCNODE_SEP: input is df")

                if len(self.getOutputs()) != (len(self.value)+1):
                    if DEBUG : print("PRCNODE_SEP: generate new sockets")
                    self.generateSockets(self.value, list(self.value.keys()))
                    if DEBUG : print("PRCNODE_SEP: new sockets have been generated")

                self.getOutput(0).value = self.value
                self.getOutput(0).type  = "df"
                for name, socket in zip(self.value, self.getOutputs()[1:]):
                    socket.value = {name : self.value[name]}
                    socket.type  = "df"
                    if DEBUG : print("PRCNODE_SEP: sockets have been filled with data and types")
            else:
                print("FALSE: ", self.value)
            return True







class CombineGraphicsNode(ResizableInputGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160.0
        self.height = 100.0
        self.min_height = 100.0

class CombineContent(ResizableInputContent):
    def serialize(self):
        res = super().serialize()
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        res['content-widht'] = self.size().width()
        res['content-height'] = self.size().height()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.grNode.height = data['height']
            self.node.grNode.width  = data['width']
            self.resize(data['content-widht'], data['content-height'])
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_COMBXY)
class CombineNode(ResizableInputNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_COMBXY
    op_title = "Data Combine"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content = CombineContent(self)
        self.grNode  = CombineGraphicsNode(self)

    def evalImplementation(self):
        input_edges = self.getInputs()
        if not input_edges:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.sortSockets()
            self.getSocketsNames()
            self.generateNewSocket()
            if len(input_edges) > 0:      
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                self.value = {}
                for input in input_edges:
                    try:
                        if isinstance(input.value, dict):
                            for name in input.value:
                                try:
                                    self.value[name] = input.value[name].copy()
                                except:
                                    self.value[name] = input.value[name]

                        if isinstance(input.value, pd.Series):
                            self.value[input.value.name] = pd.Series(input.value.values)

                        if isinstance(input.value, pd.DataFrame):
                            for name in input.value.columns:
                                self.value[name] = pd.Series(input.value[name].values)
                    except Exception as e:
                        self.e = e
                        dumpException(e)
                        
                self.getOutput(0).value = self.value
                self.getOutput(0).type = "df"
                return True
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not enough input data"
                self.getOutput(0).value = 0
                self.getOutput(0).type = "float"
                return False







class CleanGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200.0
        self.height = 240.0

class CleanContent(DataContent):
    def initUI(self):
        self.mainlayout = QGridLayout()
        self.mainlayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainlayout)

        self.dropSTR = QCheckBox('String to NAN', self)
        self.dropSTR.toggle()
        self.dropSTR.stateChanged.connect(self.recalculate)
        self.mainlayout.addWidget(self.dropSTR, 0, 0, 1, 2)

        self.removeSTR = QCheckBox('Remove sub-strings', self)
        self.removeSTR.toggle()
        self.removeSTR.stateChanged.connect(self.recalculate)
        self.mainlayout.addWidget(self.removeSTR, 1, 0, 1, 2)

        self.strToNum = QCheckBox('String to ', self)
        self.strToNum.toggle()
        self.strToNum.stateChanged.connect(self.recalculate)
        self.strToNumValue = QLineEdit("0.0", self)
        self.strToNumValue.setAlignment(Qt.AlignCenter)
        self.mainlayout.addWidget(self.strToNum, 2, 0)
        self.mainlayout.addWidget(self.strToNumValue, 2, 1)

        self.infToNum = QCheckBox('INF to ', self)
        self.infToNum.toggle()
        self.infToNum.stateChanged.connect(self.recalculate)
        self.infToNumValue = QLineEdit("0.0", self)
        self.infToNumValue.setAlignment(Qt.AlignCenter)
        self.mainlayout.addWidget(self.infToNum, 3, 0)
        self.mainlayout.addWidget(self.infToNumValue, 3, 1)

        self.dropINF = QCheckBox('INF to NAN', self)
        self.dropINF.toggle()
        self.dropINF.stateChanged.connect(self.recalculate)
        self.mainlayout.addWidget(self.dropINF, 4, 0, 1, 2)

        self.nanToNum = QCheckBox('NAN to ', self)
        self.nanToNum.toggle()
        self.nanToNum.stateChanged.connect(self.recalculate)
        self.nanToNumValue = QLineEdit("0.0", self)
        self.nanToNumValue.setAlignment(Qt.AlignCenter)
        self.mainlayout.addWidget(self.nanToNum, 5, 0)
        self.mainlayout.addWidget(self.nanToNumValue, 5, 1)

        self.dropNAN = QCheckBox('Drop NAN', self)
        self.dropNAN.toggle()
        self.dropNAN.stateChanged.connect(self.recalculate)
        self.mainlayout.addWidget(self.dropNAN, 6, 0, 1, 2)

        self.setWindowTitle("Data Clean")
    
    def recalculate(self):
        self.node.recalculate = True
        self.node.eval()

    def serialize(self):
        res = super().serialize()
        res['dropSTR']        = self.dropSTR.isChecked()
        res['removeSTR']      = self.removeSTR.isChecked()
        res['strToNum']       = self.strToNum.isChecked()
        res['strToNumValue']  = self.strToNumValue.text()
        res['infToNum']       = self.infToNum.isChecked()
        res['infToNumValue']  = self.infToNumValue.text()
        res['dropINF']        = self.dropINF.isChecked()
        res['nanToNum']       = self.nanToNum.isChecked()
        res['nanToNumValue']  = self.nanToNumValue.text()
        res['dropNAN']        = self.dropNAN.isChecked()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.dropSTR.setChecked(data['dropSTR'])
            self.removeSTR.setChecked(data['removeSTR'])
            self.strToNum.setChecked(data['strToNum'])
            self.strToNumValue.setText(data['strToNumValue'])
            self.infToNum.setChecked(data['infToNum'])
            self.infToNumValue.setText(data['infToNumValue'])
            self.dropINF.setChecked(data['dropINF'])
            self.nanToNum.setChecked(data['nanToNum'])
            self.nanToNumValue.setText(data['nanToNumValue'])
            self.dropNAN.setChecked(data['dropNAN'])
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_CLEAN)
class CleanNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_CLEAN
    op_title = "Data Clean"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def initInnerClasses(self):
        self.content = CleanContent(self)
        self.grNode  = CleanGraphicsNode(self)
        self.content.nanToNumValue.returnPressed.connect(self.recalculate)
        self.content.strToNumValue.returnPressed.connect(self.recalculate)
        self.content.infToNumValue.returnPressed.connect(self.recalculate)
        self.content.changed.connect(self.recalculate)

    def recalculate(self):
        self.setDirty()
        self.eval()

    def toFloat(self, x):
        try:
            return float(x)
        except:
            return np.nan

    def isString(self, x):
        try:
            float(x)
            return False
        except:
            return True

    def onlyNumerics(self, seq):
        return re.sub("[^\d\.]", "", seq)

    def evalImplementation(self):
        input_socket = self.getInput(0)

        if not input_socket:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.setDirty(False)
            self.setInvalid(False)
            if DEBUG : print("PRCNODE_SEP: reset dirty and invalid")
            self.e     = ""
            self.value = input_socket.value
            self.type  = input_socket.type
            if DEBUG : print("PRCNODE_SEP: get input value and type")
            self.filtered = {}

            try:
                self.e = ""
                if isinstance(self.value, dict):
                    self.filtered = self.value.copy()

                    if self.content.dropSTR.isChecked():
                        for name in self.filtered:
                            self.filtered[name] = np.array(list(map(self.toFloat, self.filtered[name])))

                    if self.content.removeSTR.isChecked():
                        for name in self.filtered:
                            self.filtered[name] = np.array(list(map(self.onlyNumerics, self.filtered[name].astype('str'))))
                            self.filtered[name] = np.array(list(map(self.toFloat, self.filtered[name])))

                    if self.content.strToNum.isChecked():
                        val = float(self.content.strToNumValue.text())
                        for name in self.filtered:
                            sel = np.array(list(map(self.isString, self.filtered[name])))
                            print()
                            print(sel)
                            print(val)
                            self.filtered[name][sel] = val
                            self.filtered[name] = np.array(list(map(self.toFloat, self.filtered[name])))

                    if self.content.infToNum.isChecked():
                        val = float(self.content.infToNumValue.text())
                        for name in self.filtered:
                            self.filtered[name][np.isinf(self.filtered[name])] = val

                    if self.content.dropINF.isChecked():
                        for name in self.filtered:
                            self.filtered[name][np.isinf(self.filtered[name])] = np.nan

                    if self.content.nanToNum.isChecked():
                        val = float(self.content.nanToNumValue.text())
                        for name in self.filtered:
                            self.filtered[name][np.isnan(self.filtered[name])] = val

                    if self.content.dropNAN.isChecked():
                        nansel = None
                        for name in self.filtered:
                            if nansel is None:
                                nansel = np.isnan(self.filtered[name])
                            else:
                                sel = np.isnan(self.filtered[name])
                                nansel = np.logical_and(nansel, sel)
                        for name in self.filtered:
                            self.filtered[name] = self.filtered[name][nansel]




                elif isinstance(self.value, pd.DataFrame):
                    self.filtered = self.value.copy()

                    if self.content.dropINF.isChecked():
                        self.filtered.replace([np.inf, -np.inf], np.nan, inplace=True)

                    if self.content.dropSTR.isChecked():
                        self.filtered = self.filtered.applymap(self.toFloat)

                    if self.content.removeSTR.isChecked():
                        self.filtered = self.filtered.applymap(str)
                        for name in self.filtered.columns:
                            self.filtered[name].str.replace(r'\D', '')
                        self.filtered = self.filtered.applymap(self.toFloat)

                    if self.content.dropNAN.isChecked():
                        self.filtered.dropna(inplace = True)

                else:
                    self.setDirty(False)
                    self.setInvalid(False)
                    self.e = "Not suotable format of the input data"
                    self.getOutput(0).value = {0.0}
                    self.getOutput(0).type = "float"
                    return False

                self.getOutput(0).value = self.filtered
                self.getOutput(0).type  = "df"
                return True

            except Exception as e:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = e
                self.getOutput(0).value = {0.0}
                self.getOutput(0).type = "float"
                return False
