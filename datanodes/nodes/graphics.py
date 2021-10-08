
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from sklearn.linear_model import LinearRegression
import matplotlib.tri as tri
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt

LINE_STYLES = ['solid',   'dotted', 'dashed','dashdot', 'solid', 'dotted', 'dashed','dashdot', 'solid', 'dotted', 'dashed','dashdot', 'solid', 'dotted', 'dashed','dashdot', 'dotted', 'dashed','dashdot']
COLORS      = ['#D98880', '#AF7AC5', '#85C1E9', '#6C3483', '#196F3D', '#CB4335', '#58D68D', '#2874A6', '#A2D9CE', '#935116', '#DC7633', '#E59866', '#154360', '#16A085', '#7D6608', '#313131']

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)



class GraphicsOutputGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 300.0
        self.height = 300.0

class GraphicsOutputContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # graph area
        self.graph = Figure()
        self.graph.autofmt_xdate()
        self.axis   = self.graph.add_subplot(111)
        self.canvas = FigureCanvas(self.graph)
        self.layout.addWidget(self.canvas)


class LineStylePicker(QComboBox):
    def __init__(self, node, name, value=None):
        super().__init__()
        self.node = node
        self.name = name
        self.addItem("solid")
        self.addItem("dashed")
        self.addItem("dashdot")
        self.addItem("dotted")
        if value is not None:
            index = self.findText(value, Qt.MatchFixedString)
            self.setCurrentIndex(index)
        self.currentIndexChanged.connect(self.chageStyle)

    def chageStyle(self):
        self.node.properties.linestyle[self.name] = self.currentText()
        self.node.drawPlot()    


class LineSizePicker(QLineEdit):
    def __init__(self, node, name, text):
        super().__init__()
        self.node = node
        self.name = name
        self.setText(str(text))
        self.textChanged.connect(self.chageSize)

    def chageSize(self):
        try:
            self.node.properties.linesize[self.name] = float(self.text())
            self.node.drawPlot()    
        except Exception as e:
            self.node.e = e
            self.node.properties.linesize[self.name] = float(1.0)
    @property
    def value(self):
        return float(self.text())


class GraphicsProperties(NodeProperties):
    def __init__(self, node, parent=None):
        super().__init__(node)
        self.names     = {}
        self.linesize  = {}
        self.linecolor = {}
        self.linestyle = {}
        self.linetype  = {}
        self.c = 0

    def resetWidgets(self):
        self.resetProperties()
        self.names     = {}
        self.linesize  = {}
        self.linecolor = {}
        self.linestyle = {}
        self.linetype  = {}
        self.c = 0

    def cleanProperties(self):
        value = self.node.value
        x_name = list(value.keys())[0]

        for name in value:
            if name != x_name:
                if name not in self.names : 
                    self.names[name]     = name
                    self.linecolor[name] = COLORS[self.c]
                    self.linestyle[name] = "solid"
                    self.linetype[name]  = "line"
                    self.linesize[name]  = 2.0
                    self.c += 1

        for name in reversed(self.names):
            if name not in value : 
                del self.names[name]
                del self.linecolor[name]
                del self.linestyle[name]
                del self.linetype[name]
                del self.linesize[name]



    def fillWidgets(self):
        for name in self.names : 

            label = QLabel(name + " ", self)        
            label.setStyleSheet("margin-top: 10px;")
            label.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

            style = LineStylePicker(self.node, name, self.linestyle[name])
            style.setStyleSheet("margin-top: 10px;")

            self.layout.addWidget(label, self.i, 0)
            self.layout.addWidget(style, self.i, 1)
            self.i += 1


            size  = LineSizePicker(self.node, name, self.linesize[name])
            size.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

            color = QWidget(self)
            color.setStyleSheet("background-color:" + self.linecolor[name] + " ;")

            self.layout.addWidget(size, self.i, 0)
            self.layout.addWidget(color, self.i, 1)
            self.i += 1


    def serialize(self):
        res = super().serialize()
        styles  = []
        colors  = []
        types   = []
        names   = []
        sizes   = []

        for name in self.names:
            styles.append(self.linestyle[name])
            colors.append(self.linecolor[name])
            types.append( self.linetype[name])
            sizes.append( self.linesize[name])
            names.append(name)

        res['styles'] = styles
        res['colors'] = colors
        res['types']  = types
        res['sizes']  = sizes
        res['names']  = names
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                self.resetWidgets()
                for i, name in enumerate(data['names']):
                    self.names[name]     = name
                    self.linecolor[name] = data['colors'][i]
                    self.linestyle[name] = data['styles'][i]
                    self.linetype[name]  = data['types'][i]
                    self.linesize[name]  = data['sizes'][i]
                    self.c += 1
                self.fillWidgets()
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_PLOT)
class GraphicsOutputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_PLOT
    op_title = "Plot"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)
        self.linecolor = {}
        self.linestyle = {}
        self.linetype  = {}
        self.linesize  = {}
        self.c = 0
        
    def initInnerClasses(self):
        self.content    = GraphicsOutputContent(self)
        self.grNode     = GraphicsOutputGraphicsNode(self)
        self.properties = GraphicsProperties(self)


    def prepareSettings(self):
        self.properties.resetProperties()
        self.properties.cleanProperties()
        self.properties.fillWidgets()

        return True

    def drawPlot(self):
        self.content.axis.clear()
        x_name = list(self.value.keys())[0]
        x_val  = self.value[x_name]
        for i, name in enumerate(self.value):
            if name != x_name:
                self.content.axis.plot(x_val, self.value[name], label=name, 
                                        color=self.properties.linecolor[name], linestyle=self.properties.linestyle[name],
                                        linewidth=self.properties.linesize[name])
        self.content.axis.legend(loc = 1)
        self.content.axis.set_xlabel(x_name)
        self.content.canvas.draw()


    def evalImplementation(self, silent=False):
        if isinstance(self.value, dict):
            self.drawPlot()
        else:
            pass
        return True










class TernaryPlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        #divider = make_axes_locatable(self.axes)
        #self.bar = divider.append_axes("right", size="5%", pad=0.1)
        self.bar = self.fig.add_axes([0.90, 0.25, 0.05, 0.70])#divider.append_axes("right", size="5%", pad=0.2)

        super(TernaryPlotCanvas, self).__init__(self.fig)



class TernaryPlotGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 300.0
        self.height = 300.0

class TernaryPlotContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.canvas = TernaryPlotCanvas()
        self.layout.addWidget(self.canvas)


    def serialize(self):
        res = super().serialize()
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                self.node.grNode.height = data['height']
                self.node.grNode.width  = data['width']
                self.updateSize()
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_PLOT_TERNARY)
class TernaryPlotNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_PLOT_TERNARY
    op_title = "Ternary Diagram"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = TernaryPlotContent(self)
        self.grNode  = TernaryPlotGraphicsNode(self)
        self.properties = NodeProperties(self)

    def prepareSettings(self):
        return True


    def cAxes(self, ax, x, y, pos='x'):
        xmin = x[0]
        xmax = x[-1]
        ymin = y[0]
        ymax = y[-1]
        ax.plot(x, y, color='black')
        
        xt = xmin
        yt = ymin
        dx = (xmax - xmin) / 10
        dy = (ymax - ymin) / 10
        x2 = ( dx * np.cos(1.5708) - dy * np.sin(1.5708) ) / 5 
        y2 = ( dy * np.cos(1.5708) + dx * np.sin(1.5708) ) / 5 
        for i in range(0, 11):
            ax.plot([xt, xt+x2], [yt, yt+y2], color='black')
            ax.text(xt + 1.75*x2, yt + 1.75*y2, i/10,
                    horizontalalignment='center',
                    verticalalignment='center',
                    color='black', fontsize=15)
            xt = xt + dx
            yt = yt + dy
        
        
        
    def mesh(self, num):
        # creating mesh 
        sc = 0.5 * np.sqrt(3) * 1.0
        dx = 1.0 / (num)
        dy = 1.0 / (num)
        size = int((num+1) * ((num+1) + 1) / 2)
        xm = np.zeros(size)
        ym = np.zeros(size)
        index = 0
        for i in range(0, (num+1)):
            for n in range(0, i+1):
                xm[index] = 0.5 - 0.5 * i / num + 1.0 * n / num
                ym[index] = (1.0 - dy * i) * sc
                index = index + 1
        
        return np.array([xm, ym]).transpose()
    

    def drawPlot(self):
        self.content.canvas.axes.clear()

        size  = len(self.value)
        names = list(self.value.keys())

        # barycentric coords: (a,b,c)
        self.a = np.array( self.value[names[0]] )
        self.b = np.array( self.value[names[1]] )
        self.c = np.array( self.value[names[2]] )
    
        # values is stored in the last column
        self.v = np.array( self.value[names[-1]] )

        # translate the data to cartesian corrds
        self.x = 0.5 * ( 2. * self.b + self.c ) / ( self.a + self.b + self.c )
        self.y = 0.5 * np.sqrt(3) * self.c / (self.a + self.b + self.c)
        ylim   = 0.5 * np.sqrt(3) * 1.0
            
        #add frame
        self.cAxes(self.content.canvas.axes, [0, 0.5], [0, ylim])
        self.cAxes(self.content.canvas.axes, [1, 0],   [0, 0])
        self.cAxes(self.content.canvas.axes, [0.5, 1.0], [ylim, 0])
        
        # plot the contour
        im = self.content.canvas.axes.tricontourf(self.x, self.y, self.v)
        plt.colorbar(im, cax=self.content.canvas.bar)
        self.content.canvas.bar.set_label(names[-1])
        
        #position the axis labels
        self.content.canvas.axes.text(1.05, -0.05,  names[1], fontsize=24, ha="left")
        self.content.canvas.axes.text(0.50,  0.92,  names[2], fontsize=24, ha="center")
        self.content.canvas.axes.text(-0.05,-0.05,  names[0], fontsize=24, ha="right")

        self.content.canvas.axes.set_axis_off()
        self.content.canvas.draw()


    def evalImplementation(self, silent=False):
        input_edge = self.getInput(0)
        if not input_edge:
            if DEBUG : print("OUTNODE_TXT: no input edge")
            self.setInvalid()
            if DEBUG : print("OUTNODE_TXT: set invalid")
            self.e = "Does not have and intry Node"
            self.content.textOut.clear()
            self.content.textOut.insertPlainText("NaN")
            if DEBUG : print("OUTNODE_TXT: clear the content")
            return False
        else:            
            if DEBUG : print("OUTNODE_TXT: process the input edge data")
            self.setDirty(False)
            self.setInvalid(False)
            if DEBUG : print("OUTNODE_TXT: reset Dirty and Invalid")
            self.e = ""
            self.value = input_edge.value
            self.drawPlot()
        return True
