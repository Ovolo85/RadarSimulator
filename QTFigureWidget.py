from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

# Qt
from PyQt5.QtWidgets import QSizePolicy, QComboBox, QPlainTextEdit, QGridLayout, QLineEdit, QMainWindow, QApplication, QPushButton, QWidget, QTabWidget,QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon

# MatplotLib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class FigureWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setLayout(QVBoxLayout())
        self.canvas = FigureCanvas()
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent = None):
        self.fig = Figure(tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)
        self.axes.plot()
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

#class StaticFigureCanvas(FigureCanvas):
    def update_figure_2dim(self, labels, arraysToPlot, title, xLabel, yLabel, aspectForced):
        self.axes.cla()
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        for i in range(len(arraysToPlot)):
            arrayToPlot = arraysToPlot[i]
            self.axes.plot(arrayToPlot[:,2], arrayToPlot[:,1], label=labels[i])
        
        self.axes.legend(loc="upper right")
        self.axes.set_title(title)
        self.axes.set_xlabel(xLabel)
        self.axes.set_ylabel(yLabel)
        if aspectForced:
            self.axes.set_aspect(1)
            xWidth = abs(self.axes.get_xlim()[0] - self.axes.get_xlim()[1])
            yWidth = abs(self.axes.get_ylim()[0] - self.axes.get_ylim()[1])
            xyWidthDiff = abs(xWidth-yWidth)
            if yWidth > 0.75 * xWidth:
                xAddition = xyWidthDiff/0.75 / 2
                self.axes.set_xlim([self.axes.get_xlim()[0] - xAddition, self.axes.get_xlim()[1] + xAddition])
            else: 
                pass
        else:
            self.axes.set_aspect("auto")
        
        self.axes.grid(True)

        self.draw()

    def update_point_figure_2dim(self, labels, pointsListsToPlot, lineListsToPlot, title, xLabel, yLabel, ticks = []):
        # This plots single points, each one in a different color 
        #
        # INPUT
        # labels: list of labels, each one for one point-set
        # pointsToPlot: list of lists of lists, each one is a single point of 2 dimensions
        # lineListsToPlot: list of np arrays, each array shall be one line (in a distinct color)
        # title: String
        # xLabel: String
        # yLabel: String

        self.axes.cla()
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        point_symboltable = ["ro", "go", "bo", "co", "mo", "yo", "ko", "rx"]
        line_symboltable = ["r-", "g-", "b-", "c-", "m-", "y-", "k-", "r--"]
        
        symbol = 0
        for idx, l in enumerate(pointsListsToPlot):
            arrayToPlot = np.array(l)
            #for p in l:
                #self.axes.plot(p[0], p[1], point_symboltable[symbol], label=labels[idx])
            self.axes.plot(arrayToPlot[:,0], arrayToPlot[:,1], point_symboltable[symbol], label=labels[idx])
            symbol = symbol+1

        symbol = 0
        for line in lineListsToPlot:
            self.axes.plot(line[:,0], line[:,1], line_symboltable[symbol])
            symbol = symbol+1

        if len(ticks) > 0:
            self.axes.set_xticks(ticks[0])
            self.axes.set_xticks(ticks[1], minor=True)
            self.axes.set_yticks(ticks[2])
            self.axes.set_yticks(ticks[3], minor=True)

            self.axes.grid(which="minor", alpha=0.2)
            self.axes.grid(which="major", alpha=0.5)

        self.axes.legend(loc="upper right")
        self.axes.set_title(title)
        self.axes.set_xlabel(xLabel)
        self.axes.set_ylabel(yLabel)
        self.axes.grid(True)

        self.draw()


    def update_figure_1dim(self, labels, arraysToPlot, title, xLabel, yLabel, dashedData = []):
        self.axes.cla()
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        for i in range(len(arraysToPlot)):
            arrayToPlot = arraysToPlot[i]
            if i in dashedData:
                self.axes.plot(arrayToPlot[:,0], arrayToPlot[:,1], "--", label=labels[i])
            else:
                self.axes.plot(arrayToPlot[:,0], arrayToPlot[:,1], label=labels[i])
        
        self.axes.legend(loc="upper right")
        self.axes.set_title(title)
        self.axes.set_xlabel(xLabel)
        self.axes.set_ylabel(yLabel)

        self.axes.grid(True)

        self.draw()

    def update_multi_figure(self, labels, arraysToPlot, title, xLabels, yLabels, labelsOff, dashedData = []):
        self.axes.cla()
        self.fig.clf()


        for i in range(len(labels)):
            ax = self.fig.add_subplot(len(arraysToPlot), 1, i+1)
            if i in dashedData:
                ax.plot(arraysToPlot[i][:,0], arraysToPlot[i][:,1], "--")
            else: 
                ax.plot(arraysToPlot[i][:,0], arraysToPlot[i][:,1])
            if i == 0: 
                ax.set_title(title)
            if not labelsOff:
                ax.set_xlabel(xLabels[i])
                ax.set_ylabel(yLabels[i])
            ax.grid(True)

        self.draw()

    


    def clear_figure(self):
        self.axes.cla()
        self.fig.clf()

        self.draw()