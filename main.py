import sys
from PyQt5.QtWidgets import *
from node_window import NodeWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = NodeWindow()

    sys.exit(app.exec_())
4