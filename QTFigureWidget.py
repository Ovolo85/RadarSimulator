from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

# Qt
from PyQt5.QtWidgets import QSizePolicy, QComboBox, QPlainTextEdit, QGridLayout, QLineEdit, QMainWindow, QApplication, QPushButton, QWidget, QTabWidget,QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon

# MatplotLib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

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

    def update_point_figure_2dim(self, pointlabels, pointsListsToPlot, lineLabels, lineListsToPlot, title, xLabel, yLabel, ticks = [], aspectForced = False):
        # This plots single points, each one in a different color 
        #
        # INPUT
        # pointlabels: list of labels, each one for one point-set
        # pointsToPlot: list of lists of lists, each one is a single point of 2 dimensions
        # linelabels
        # lineListsToPlot: list of np arrays, each array shall be one line (in a distinct color)
        # title: String
        # xLabel: String
        # yLabel: String
        # ticks: The Grid, list of [major_xTick, minor_xTick, major_yTick, minor_yTick]
        # aspectForced: keep the aspect of x and y 1:1, make slim plots square

        self.axes.cla()
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        point_symboltable = ["ro", "go", "bo", "co", "mo", "yo", "ko", "rx"]
        line_symboltable = ["r-", "g-", "b-", "c-", "m-", "y-", "k-", "r--"]
        
        # plot points
        symbol = 0
        for idx, l in enumerate(pointsListsToPlot):
            arrayToPlot = np.array(l)
            #for p in l:
                #self.axes.plot(p[0], p[1], point_symboltable[symbol], label=labels[idx])
            if len(pointlabels) == len(pointsListsToPlot):
                self.axes.plot(arrayToPlot[:,0], arrayToPlot[:,1], point_symboltable[symbol], label=pointlabels[idx])
            else:
                self.axes.plot(arrayToPlot[:,0], arrayToPlot[:,1], point_symboltable[symbol])
            symbol = symbol+1

        # plot lines
        symbol = 0
        for idx, line in enumerate(lineListsToPlot):
            if len(lineLabels) == len(lineListsToPlot):
                self.axes.plot(line[:,0], line[:,1], line_symboltable[symbol], label = lineLabels[idx])
            else:
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

    def update_figure_rects(self, rectsToPlot, title, xLabel, yLabel, xMax, yMax, xMin, yMin):
        self.axes.cla()
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        self.axes.set_xlim([xMin, xMax])
        self.axes.set_ylim([yMin, yMax])

        for r in rectsToPlot:
            self.axes.add_patch(Rectangle(r[0], r[1], r[2], color=r[3]))

        #self.axes.legend(loc="upper right")
        self.axes.set_title(title)
        self.axes.set_xlabel(xLabel)
        self.axes.set_ylabel(yLabel)

        self.axes.grid(True)

        self.draw()

    def clear_figure(self):
        self.axes.cla()
        self.fig.clf()

        self.draw()