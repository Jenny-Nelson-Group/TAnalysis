import sys
import os
import os.path
import glob
import numpy as np
from PyQt4 import QtGui
from PyQt4.uic import loadUiType
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import TAQtGuiFunctions
from matplotlib import style
style.use('ggplot')

Ui_MainWindow, QMainWindow = loadUiType('window.ui')

class Main(QMainWindow, Ui_MainWindow) :
    def __init__(self, ) :
        super(Main, self).__init__()
        self.setupUi(self)

        self.chooseInputDirButton.clicked.connect(self.choose_input_dir)
        self.chooseOutputDirButton.clicked.connect(self.choose_output_dir)
        self.updateButton.clicked.connect(self.update)
        self.runButton.clicked.connect(self.run)
        self.runButton.setEnabled(False)

        self.sld0i.sliderReleased.connect( lambda arg=[self.sld0i,self.sld0f,'start']: self.dontTrollMe(arg))
        self.sld0f.sliderReleased.connect( lambda arg=[self.sld0i,self.sld0f,'end']: self.dontTrollMe(arg))
        self.sld1i.sliderReleased.connect( lambda arg=[self.sld1i,self.sld1f,'start']: self.dontTrollMe(arg))
        self.sld1f.sliderReleased.connect( lambda arg=[self.sld1i,self.sld1f,'end']: self.dontTrollMe(arg))
        self.sld2i.sliderReleased.connect( lambda arg=[self.sld2i,self.sld2f,'start']: self.dontTrollMe(arg))
        self.sld2f.sliderReleased.connect( lambda arg=[self.sld2i,self.sld2f,'end']: self.dontTrollMe(arg))
        self.sld3i.sliderReleased.connect( lambda arg=[self.sld3i,self.sld3f,'start']: self.dontTrollMe(arg))
        self.sld3f.sliderReleased.connect( lambda arg=[self.sld3i,self.sld3f,'end']: self.dontTrollMe(arg))
        self.sld4i.sliderReleased.connect( lambda arg=[self.sld4i,self.sld4f,'start']: self.dontTrollMe(arg))
        self.sld4f.sliderReleased.connect( lambda arg=[self.sld4i,self.sld4f,'end']: self.dontTrollMe(arg))
        self.sld5i.sliderReleased.connect( lambda arg=[self.sld5i,self.sld5f,'start']: self.dontTrollMe(arg))
        self.sld5f.sliderReleased.connect( lambda arg=[self.sld5i,self.sld5f,'end']: self.dontTrollMe(arg))

        self.separateGraphsDC.clicked.connect(self.refreshfit)
        self.separateGraphsLambda.clicked.connect(self.refreshfit)
        self.useTightLayoutDC.clicked.connect(self.refreshfit)
        self.useTightLayoutLambda.clicked.connect(self.refreshfit)

        self.colorsfit = ['#66FF33', '#FF6633', '#CC33FF', '#33FFCC', '#FF3366', '#3366FF']

        for i in range(1,7): self.tabWidget.setTabEnabled(i, False)

        def_conf = TAQtGuiFunctions.readConfFile()
        self.inputDirEdit.setText(def_conf['def_dir'])
        self.outputDirEdit.setText(def_conf['def_out'])
        self.thicknessEdit.setText(def_conf['def_L'])
        self.areaEdit.setText(def_conf['def_A'])
        self.dieConstEdit.setText(def_conf['def_eps'])

        self.dict_figs = {}
        self.dict_figs['llc'] = {'canvas': FigureCanvas(Figure()),
                                'canvasPlace': self.llcCanvasPlace,
                                'widget': self.llcWidget}
        self.dict_figs['ce'] = {'canvas': FigureCanvas(Figure()),
                                'canvasPlace': self.ceCanvasPlace,
                                'widget': self.ceWidget}
        self.dict_figs['tpc'] = {'canvas': FigureCanvas(Figure()),
                                'canvasPlace': self.tpcCanvasPlace,
                                'widget': self.tpcWidget}
        self.dict_figs['tpv'] = {'canvas': FigureCanvas(Figure()),
                                'canvasPlace': self.tpvCanvasPlace,
                                'widget': self.tpvWidget}
        self.dict_figs['dc'] = {'canvas': FigureCanvas(Figure()),
                                'canvasPlace': self.dcCanvasPlace,
                                'widget': self.dcWidget}
        self.dict_figs['lambda'] = {'canvas': FigureCanvas(Figure()),
                                'canvasPlace': self.lambdaCanvasPlace,
                                'widget': self.lambdaWidget}


        self.addCanvas(Figure(), 'llc')
        self.addCanvas(Figure(), 'ce')
        self.addCanvas(Figure(), 'tpc')
        self.addCanvas(Figure(), 'tpv')
        self.addCanvas(Figure(), 'dc')
        self.addCanvas(Figure(), 'lambda')

        self.tabWidget.setCurrentIndex(0)

        self.control1 = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+1'), self)
        self.control1.activated.connect( lambda arg = [1] : self.runShortcut(arg))
        self.control2 = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+2'), self)
        self.control2.activated.connect( lambda arg = [2] : self.runShortcut(arg))
        self.control3 = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+3'), self)
        self.control3.activated.connect( lambda arg = [3] : self.runShortcut(arg))
        self.control4 = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+4'), self)
        self.control4.activated.connect( lambda arg = [4] : self.runShortcut(arg))
        self.control5 = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+5'), self)
        self.control5.activated.connect( lambda arg = [5] : self.runShortcut(arg))
        self.control6 = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+6'), self)
        self.control6.activated.connect( lambda arg = [6] : self.runShortcut(arg))
        self.control7 = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+7'), self)
        self.control7.activated.connect( lambda arg = [7] : self.runShortcut(arg))

    def runShortcut(self, index) :
        self.tabWidget.setCurrentIndex(int(index[0])-1)

    def refreshfit(self): # EVERY TIME YOU CHANGE THE LIMITS ON THE FITTINGS IT CALLS THIS
        # THIS GET THE FITTING LIMITS FROM THE SLIDERS
        limits = []
        limits.append([self.sld0i.value(),self.sld0f.value()])
        limits.append([self.sld1i.value(),self.sld1f.value()])
        limits.append([self.sld2i.value(),self.sld2f.value()])
        limits.append([self.sld3i.value(),self.sld3f.value()])
        limits.append([self.sld4i.value(),self.sld4f.value()])
        limits.append([self.sld5i.value(),self.sld5f.value()])
        TAQtGuiFunctions.workOnDC(limits, TAQtGuiFunctions.lookForFiles())
        self.updateCanvas(updateDC(self), 'dc')
        self.updateCanvas(updateLambda(self), 'lambda')

    def dontTrollMe(self, arg): # THIS IS SELF-EXPLANATORY. OR NOT.
        # THIS IS CALLED EVERYTIME YOU CHANGE ANY OF THE SLIDERS.
        # event IS A ARGUMENT NECESSARY FOR THE bind() METHOD ON THE SLIDERS.
        # I DONT KNOW WHAT event DOES EXACTLY. BUT IS IMPORTANT SHIT.
        # arg IS A LIST OF 3 PARAMETERS.
        # arg[0] IS THE TOP SLIDE OBJECT (START POINT TO FIT).
        # arg[0].get() RETURNS THE CURRENT VALUE ON SLIDER.
        # arg[0].set(x) FORCE SOME VALUE x ON THE SLIDER.
        # SAME THING FOR arg[1] WHICH IS THE BOTTOM SLIDER OBJECT (END POINT TO FIT).
        # arg[2] IS A STRING STATING 'start' FOR THE TOP SLIDER OR 'end' FOR THE BOTTON SLIDER
        suns = TAQtGuiFunctions.whatIsThis('suns_LLC') # NECESSARY TO OBTAIN THE AMOUNT OF POINTS
                                                  # ON THE EXPERIMENTAL DATA FOR FITTING
        if arg[2] == 'start' and arg[1].value()-arg[0].value() < 2 : # CHECK IF YOU ARE USING
                                                                 # EITHER TOP SLIDER
                                                                 # AND IF END SLIDE IS LESS
                                                                 # THAN 2 POINTS GREATER THAN
                                                                 # START SLIDER
            arg[1].setValue(arg[0].value()+2) # IF THE SLIDERS ARE TOO CLOSE,
                                       # SET END SLIDER 2 POINTS AWAY FROM THE CURRENT
                                       # VALUE OF START SLIDER
            if arg[1].value() == len(suns): # IF AFTER THAT, END SLIDER REACHED LIMIT OF SLIDER
                arg[0].setValue(len(suns)-2) # PUSH BACK THE START SLIDERS
        # THE OPPOSITE OF WHAT WAS SAID BEFORE HAPPENS DOWN HERE
        if arg[2] == 'end' and arg[1].value()-arg[0].value() < 2 :
            arg[0].setValue(arg[1].value()-2)
            if arg[0].value() == 0:
                arg[1].setValue(2)
        # WHAT WAS DONE ABOVE IS JUST TO ENSURE THAT SOMEONE (YOU) DON'T DO ANYTHING
        # SILLY WITH THE SLIDERS.
        self.refreshfit() # CALL refreshfit TO RECALCULATE THE FITTINGS

    def addCanvas(self, fig, which):
        self.dict_figs[which]['canvas'] = FigureCanvas(fig)
        self.dict_figs[which]['canvasPlace'].addWidget(self.dict_figs[which]['canvas'])
        self.dict_figs[which]['canvas'].draw()
        self.dict_figs[which]['toolbar'] = NavigationToolbar(
                                            self.dict_figs[which]['canvas'],
                                            self.dict_figs[which]['widget'],
                                            coordinates=True)
        self.dict_figs[which]['canvasPlace'].addWidget(self.dict_figs[which]['toolbar'])

    def updateCanvas(self, fig, which):
        self.dict_figs[which]['canvasPlace'].removeWidget(self.dict_figs[which]['canvas'])
        self.dict_figs[which]['canvas'].close()
        self.dict_figs[which]['canvasPlace'].removeWidget(self.dict_figs[which]['toolbar'])
        self.dict_figs[which]['toolbar'].close()
        self.addCanvas(fig, which)

    def run(self) :
        self.update()
        (isThereACalibrationFile, CEFiles, CEsuns, TPCFiles, TPCsuns, TPVFiles,
                TPVsuns) = TAQtGuiFunctions.lookForFiles()

        if isThereACalibrationFile :
            TAQtGuiFunctions.getJscCal(self)
            self.updateCanvas(updateLLC(), 'llc')
            self.tabWidget.setTabEnabled(1, True)
        if CEFiles :
            TAQtGuiFunctions.workOnCEData(self.geoCapCorrCheck.isChecked())
            self.updateCanvas(updateCE(),  'ce' )
            self.tabWidget.setTabEnabled(2, True)
        if TPCFiles :
            TAQtGuiFunctions.workOnTPCData()
            self.updateCanvas(updateTPC(), 'tpc')
            self.tabWidget.setTabEnabled(3, True)
        if TPVFiles :
            TAQtGuiFunctions.workOnTPVData()
            self.updateCanvas(updateTPV(), 'tpv')
            self.tabWidget.setTabEnabled(4, True)
        if (TPVFiles and TPCFiles ) or CEFiles :
            suns = TAQtGuiFunctions.whatIsThis('suns_LLC')
            self.sld0i.setRange(0,len(suns))
            self.sld0f.setRange(0,len(suns))
            self.sld0f.setValue(len(suns))
            self.sld1i.setRange(0,len(suns))
            self.sld1f.setRange(0,len(suns))
            self.sld1f.setValue(len(suns))
            self.sld2i.setRange(0,len(suns))
            self.sld2f.setRange(0,len(suns))
            self.sld2f.setValue(len(suns))
            self.sld3i.setRange(0,len(suns))
            self.sld3f.setRange(0,len(suns))
            self.sld3f.setValue(len(suns))
            self.sld4i.setRange(0,len(suns))
            self.sld4f.setRange(0,len(suns))
            self.sld4f.setValue(len(suns))
            self.sld5i.setRange(0,len(suns))
            self.sld5f.setRange(0,len(suns))
            self.sld5f.setValue(len(suns))

            limits = []
            limits.append([0,len(suns)])
            limits.append([0,len(suns)])
            limits.append([0,len(suns)])
            limits.append([0,len(suns)])
            limits.append([0,len(suns)])
            limits.append([0,len(suns)])
            TAQtGuiFunctions.workOnDC(limits, TAQtGuiFunctions.lookForFiles())
            self.updateCanvas(updateDC(self), 'dc')
            self.tabWidget.setTabEnabled(5, True)
            self.updateCanvas(updateLambda(self), 'lambda')
            self.tabWidget.setTabEnabled(6, True)

    def choose_input_dir(self) :
        path = QtGui.QFileDialog.getExistingDirectory(self,
                'Select Input Directory', self.inputDirEdit.text())
        path = TAQtGuiFunctions.windowsFilenamesSuck(path)
        self.inputDirEdit.setText(path)

    def choose_output_dir(self) :
        path = QtGui.QFileDialog.getExistingDirectory(self,
                'Select Output Directory', self.outputDirEdit.text())
        path = TAQtGuiFunctions.windowsFilenamesSuck(path)
        self.outputDirEdit.setText(path)

    def update(self) :
        for i in range(1,6): self.tabWidget.setTabEnabled(i, False)
        self.inputDirLabel.setText(self.inputDirEdit.text())
        self.outputDirLabel.setText(self.outputDirEdit.text())
        self.thicknessLabel.setText(self.thicknessEdit.text())
        self.areaLabel.setText(self.areaEdit.text())
        self.dieConstLabel.setText(self.dieConstEdit.text())

        # UPDATE THE CONF.TXT FILE WITH THE NEW INFORMATION TO BE LOADED NEXT TIME
        with open('conf.txt', 'w') as f:
            f.write('def_dir , %s , #\n' % self.inputDirEdit.text())
            f.write('def_out , %s , #\n' % self.outputDirEdit.text())
            f.write('def_eps , %f , #\n' % float(self.dieConstEdit.text()))
            f.write('def_L , %f , nm\n' % float(self.thicknessEdit.text()))
            f.write('def_A , %f , cm^2' % float(self.areaEdit.text()))

        a, b, volume, geoC = TAQtGuiFunctions.getConfTxt()
        self.geoCLabel.setText('%1.2e' % geoC)
        (isThereACalibrationFile, CEFiles, CEsuns, TPCFiles, TPCsuns, TPVFiles,
                TPVsuns) = TAQtGuiFunctions.lookForFiles()
        if isThereACalibrationFile :
            self.llcLabel.setText('Light Level Calibration file found')
        else :
            self.llcLabel.setText('Light Level Calibration file NOT found')
        self.ceLabel.setText('%i files. List of suns: %s' % (CEFiles, CEsuns))
        self.tpcLabel.setText('%i files. List of suns: %s' % (TPCFiles, TPCsuns))
        self.tpvLabel.setText('%i files. List of suns: %s' % (TPVFiles, TPVsuns))
        self.runButton.setEnabled(True)

if __name__ == '__main__' :

    fLLC = Figure()
    fCE  = Figure()
    fTPC = Figure()
    fTPV = Figure()
    fDC  = Figure()
    fLambda = Figure()

    def readIandQfromCE(): # TO BE USED IN updatefCE()
        directory, output, volume, Cgeo = TAQtGuiFunctions.getConfTxt()
        list_of_i = []
        list_of_q = []
        ti, i     = [], []
        tq, q     = [], []
        for path in glob.glob(output+'*'):
            if path.find('I_CE') > 0 :
                ti, i = [], []
                with open(path,'r') as f:
                    for linenumber,line in enumerate(f.readlines()):
                        if linenumber > 3 :
                            ti.append(1e6*float(line.split(' , ')[0]))
                            i.append(float(line.split(' , ')[3]))
                list_of_i.append(i)
            if path.find('Q_CE') > 0 :
                tq, q = [], []
                with open(path,'r') as f:
                    for linenumber,line in enumerate(f.readlines()):
                        if( linenumber > 3 ):
                            tq.append(1e6*float(line.split(' , ')[0]))
                            q.append(1e9*float(line.split(' , ')[1]))
                list_of_q.append(q)

        return ti, list_of_i, tq, list_of_q

    def readIandQfromTPC(): # TO BE USED IN updatefTPC()
        directory, output, volume, Cgeo = TAQtGuiFunctions.getConfTxt()
        list_of_i = []
        list_of_q = []
        ti, i     = [], []
        tq, q     = [], []
        for path in glob.glob(output+'*'):
            if path.find('I_TPC') > 0 :
                ti, i = [], []
                with open(path,'r') as f:
                    for linenumber,line in enumerate(f.readlines()):
                        if linenumber > 3 :
                            ti.append(1e6*float(line.split(' , ')[0]))
                            i.append(float(line.split(' , ')[2]))
                list_of_i.append(i)
            if path.find('Q_TPC') > 0 :
                tq, q = [], []
                with open(path,'r') as f:
                    for linenumber,line in enumerate(f.readlines()):
                        if( linenumber > 3 ):
                            tq.append(1e6*float(line.split(' , ')[0]))
                            q.append(1e9*float(line.split(' , ')[1]))
                list_of_q.append(q)

        return ti, list_of_i, tq, list_of_q

    def readVandFitfromTPV(): # TO BE USED IN updatefTPV
        directory, output, volume, Cgeo = TAQtGuiFunctions.getConfTxt()
        list_of_v_exp   = []
        list_of_t_fit = []
        list_of_v_exp_fit   = []
        list_of_fit = []
        t_exp, t_fit, v_exp_fit, fit   = [], [], [], []
        for path in glob.glob(output+'*'):
            if path.find('V_TPV') > 0 :
                t_exp, v_exp = [], []
                with open(path,'r') as f:
                    for linenumber,line in enumerate(f.readlines()):
                        if linenumber > 3 :
                            t_exp.append(1e6*float(line.split(' , ')[0]))
                            v_exp.append(float(line.split(' , ')[2]))
                list_of_v_exp.append(v_exp)

            if path.find('Fit_TPV') > 0 :
                t_fit, v_exp_fit, fit = [], [], []
                with open(path,'r') as f:
                    for linenumber,line in enumerate(f.readlines()):
                        if linenumber > 3 :
                            t_fit.append(1e6*float(line.split(' , ')[0]))
                            v_exp_fit.append(float(line.split(' , ')[1]))
                            fit.append(float(line.split(' , ')[2]))
                list_of_t_fit.append(t_fit)
                list_of_v_exp_fit.append(v_exp_fit)
                list_of_fit.append(fit)

        return t_exp, list_of_v_exp, list_of_t_fit, list_of_v_exp_fit, list_of_fit

    def readFits(): # TO BE USED IN updatefDC()
        voc_fit, lnC_fit, voc_fit_rev, lnC_fit_rev = [], [], [], []
        lnQ1, lnLT1, lnQ2, lnLT2, lnQ3, lnLT3, lnQ4, lnLT4 = [], [], [], [], [], [], [], []
        directory, output, volume, Cgeo =TAQtGuiFunctions.getConfTxt()
        in_file = output+'Fit for DiffC.txt'
        with open(in_file,'r') as f:
            for linenumber, line in enumerate(f):
                if linenumber > 2 :
                    voc_fit.append(float(line.split(',')[0]))
                    lnC_fit.append(float(line.split(',')[1]))
        in_file = output+'Fit for DiffC rev.txt'
        with open(in_file,'r') as f:
            for linenumber, line in enumerate(f):
                if linenumber > 2 :
                    voc_fit_rev.append(float(line.split(',')[0]))
                    lnC_fit_rev.append(float(line.split(',')[1]))
        in_file = output+'Fit for logLT_fitdc.txt'
        with open(in_file,'r') as f:
            for linenumber, line in enumerate(f):
                if linenumber > 2 :
                    lnQ1.append( float(line.split(' , ')[0]))
                    lnLT1.append(float(line.split(' ,         in_file = output+'Fit for logLT_fitdc_rev.txt'
        with open(in_file,'r') as f:
            for linenumber, line in enumerate(f):
                if linenumber > 2 :
                    lnQ2.append(float(line.split(',')[0]))
                    lnLT2.append(float(line.split(',')[1]))
        in_file = output+'Fit for logLT_fitce.txt'
        if os.path.isfile(in_file) :
            with open(in_file,'r') as f:
                for linenumber, line in enumerate(f):
                    if linenumber > 2 :
                        lnQ3.append(float(line.split(',')[0]))
                        lnLT3.append(float(line.split(',')[1]))
        in_file = output+'Fit for logLT_fitce_rev.txt'
        if os.path.isfile(in_file) :
            with open(in_file,'r') as f:
                for linenumber, line in enumerate(f):
                    if linenumber > 2 :
                        lnQ4.append(float(line.split(',')[0]))
                        lnLT4.append(float(line.split(',')[1]))

        return voc_fit, lnC_fit, voc_fit_rev, lnC_fit_rev, lnQ1, lnLT1, lnQ2, lnLT2, lnQ3, lnLT3, lnQ4, lnLT4

    def readLambdas(): # TO BE USED IN updatefDC()
        lambdas = {}
        directory, output, volume, Cgeo =TAQtGuiFunctions.getConfTxt()
        with open(output+'Lambdas.txt','r') as f:
            for line in f:
                lambdas[line.split(' , ')[0]] = line.split(' , ')[1]

        return lambdas

    def updateLLC() :
        suns          = TAQtGuiFunctions.whatIsThis('suns_LLC')
        jsc           = TAQtGuiFunctions.whatIsThis('jsc_LLC')
        jsc_rev       = TAQtGuiFunctions.whatIsThis('jsc_rev_LLC')
        voc           = TAQtGuiFunctions.whatIsThis('voc_LLC')
        voc_rev       = TAQtGuiFunctions.whatIsThis('voc_rev_LLC')
        fLLC.clear()

        fLLCplot = fLLC.add_subplot(111)
        fLLCplot.set_title('$G1$ - $J_{sc}$ $(green)$ $and$ $V_{oc}$ $(red)$ x $Suns$')
        text = 'Filled circle: Forward \nOpen circle: Reverse'
        fLLCplot.text(0.4, 0.10, text,
                      transform=fLLCplot.transAxes, fontsize=15)
        fLLCplot.set_xlabel('$Suns$', fontsize=20)
        fLLCplot.tick_params(axis='x', labelsize=15)
        fLLCplot.set_ylabel('$J_{sc}$ $(mA/cm^2)$', color='g', fontsize=20)
        fLLCplot.tick_params(axis='y', labelcolor='g', labelsize=15)
        fLLCplotright = fLLCplot.twinx()
        fLLCplotright.set_ylabel('$V_{oc}$ $(V)$', color='r', fontsize=20)
        fLLCplotright.tick_params(axis='y', labelcolor='r', labelsize=15)
        fLLCplotright.grid(False)
        fLLCplot.plot(suns, jsc, 'g-o', lw=3, ms=8)
        fLLCplot.plot(suns, jsc_rev, 'g-o', lw=3, ms=8, mfc='w')
        fLLCplotright.plot(suns, voc, 'r-o', lw=3, ms=8)
        fLLCplotright.plot(suns, voc_rev, 'r-o', lw=3, ms=8, mfc='w')

        return fLLC

    def updateCE(): # CALLED BY aniCE
        ti, list_of_i, tq, list_of_q  = readIandQfromCE()
        suns          = TAQtGuiFunctions.whatIsThis('suns_LLC')
        voc           = TAQtGuiFunctions.whatIsThis('voc_LLC')
        voc_rev       = TAQtGuiFunctions.whatIsThis('voc_rev_LLC')
        qce           = TAQtGuiFunctions.whatIsThis('q_CE')
        qce_rev       = TAQtGuiFunctions.whatIsThis('q_rev_CE')

        fCE.clear()

        fCEplot = fCE.add_subplot(221)
        fCEplot.set_title('$G2$ - $Current$ x $Time$')
        fCEplot.set_xlabel('$Time$ $(\mu s)$', fontsize=15)
        fCEplot.tick_params(axis='x', labelsize=12)
        fCEplot.set_ylabel('$I$ $(mA)$', fontsize=15)
        fCEplot.tick_params(axis='y', labelsize=12)
        fCEplot.autoscale(tight=True)
        for i in list_of_i: fCEplot.plot(ti, i, 'k-', lw=1, ms=8, alpha=0.4)

        fCEplot = fCE.add_subplot(223)
        fCEplot.set_title('$G3$ - $Charge$ x $Time$')
        fCEplot.set_xlabel('$Time$ $(\mu s)$', fontsize=15)
        fCEplot.tick_params(axis='x', labelsize=12)
        fCEplot.set_ylabel('$Q$ $(nC)$', fontsize=15)
        fCEplot.tick_params(axis='y', labelsize=12)
        fCEplot.autoscale(tight=True)
        for q in list_of_q: fCEplot.plot(tq, q, 'k-', lw=1, ms=8, alpha=0.7)

        fCEplot = fCE.add_subplot(122)
        text='$G4$ - $Charge$ x $V_{oc}$ $(green)$ $and$ $Suns$ $(red)$'
        fCEplot.text(0.05, 0.95, text,
                     transform=fCEplot.transAxes, fontsize=15)
        text='Filled circle: Forward \nOpen circle: Reverse'
        fCEplot.text(0.05, 0.85, text,
                     transform=fCEplot.transAxes, fontsize=12)
        fCEplot.set_xlabel('$V_{oc}$ $(V)$', color='g', fontsize=15)
        fCEplot.tick_params(axis='x', labelcolor='g', labelsize=12)
        fCEplot.set_ylabel('$Q$ $(nC)$', fontsize=15)
        fCEplot.tick_params(axis='y', labelsize=12)
        fCEplottop = fCEplot.twiny()
        fCEplottop.set_xlabel('$Suns$', color='r', fontsize=15)
        fCEplottop.tick_params(axis='x', labelcolor='r', labelsize=12)
        fCEplottop.grid(False)
        fCEplot.plot(voc, 1e9*qce, 'g-o', lw=3, ms=8)
        fCEplot.plot(voc_rev, 1e9*qce_rev, 'g-o', lw=3, ms=5, mfc='w')
        fCEplottop.plot(suns, 1e9*qce, 'r-o', lw=3, ms=8)
        fCEplottop.plot(suns, 1e9*qce_rev, 'r-o', lw=3, ms=5, mfc='w')

        fCE.set_tight_layout(True)
        return fCE

    def updateTPC(): # CALLED BY aniTPC
        ti, list_of_i, tq, list_of_q  = readIandQfromTPC()
        suns          = TAQtGuiFunctions.whatIsThis('suns_LLC')
        voc           = TAQtGuiFunctions.whatIsThis('voc_LLC')
        qtpc          = TAQtGuiFunctions.whatIsThis('q_TPC')

        fTPC.clear()

        fTPCplot = fTPC.add_subplot(221)
        fTPCplot.set_title('$G5$ - $Current$ x $Time$')
        fTPCplot.set_xlabel('$Time(\mu s)$', fontsize=15)
        fTPCplot.tick_params(axis='x', labelsize=12)
        fTPCplot.set_ylabel('$I(mA)$', fontsize=15)
        fTPCplot.tick_params(axis='y', labelsize=12)
        fTPCplot.autoscale(tight=True)
        for i in list_of_i: fTPCplot.plot(ti, i, 'k-', lw=1, ms=8, alpha=0.4)

        fTPCplot = fTPC.add_subplot(223)
        fTPCplot.set_title('$G6$ - $Charge$ x $Time$')
        fTPCplot.set_xlabel('$Time(\mu s)$', fontsize=15)
        fTPCplot.tick_params(axis='x', labelsize=12)
        fTPCplot.set_ylabel('$Q(nC)$', fontsize=15)
        fTPCplot.tick_params(axis='y', labelsize=12)
        fTPCplot.autoscale(tight=True)
        for q in list_of_q: fTPCplot.plot(tq, q, 'k-', lw=1, ms=8, alpha=0.7)

        fTPCplot = fTPC.add_subplot(122)
        text='$G7$ - $Charge$ x $V_{oc}$ $(green)$ $and$ $Suns$ $(red)$'
        fTPCplot.text(0.05, 0.05, text,
                     transform=fTPCplot.transAxes, fontsize=15)
        fTPCplot.set_xlabel('$V_{oc} (V)$', color='g', fontsize=15)
        fTPCplot.tick_params(axis='x', labelcolor='g', labelsize=12)
        fTPCplot.set_ylabel('$Q (nC)$', fontsize=15)
        fTPCplot.tick_params(axis='y', labelsize=12)
        fTPCplottop = fTPCplot.twiny()
        fTPCplottop.set_xlabel('$Suns$', color='r', fontsize=15)
        fTPCplottop.tick_params(axis='x', labelcolor='r', labelsize=12)
        fTPCplottop.grid(False)
        fTPCplot.plot(voc, 1e9*qtpc, 'g-o', lw=3, ms=8)
        fTPCplottop.plot(suns, 1e9*qtpc, 'r-o', lw=3, ms=8)

        fTPC.set_tight_layout(True)

        return fTPC


    def updateTPV(): # CALLED BY aniTPV
        t_exp, list_of_v_exp, list_of_t_fit, list_of_v_exp_fit, list_of_fit = readVandFitfromTPV()
        suns          = TAQtGuiFunctions.whatIsThis('suns_LLC')
        tau           = TAQtGuiFunctions.whatIsThis('tau')
        deltaV0       = TAQtGuiFunctions.whatIsThis('v0')

        fTPV.clear()

        fTPVplot = fTPV.add_subplot(221)
        fTPVplot.set_title('$G8$ - $Voltage$ x $Time$')
        fTPVplot.set_xlabel('$Time(\mu s)$', fontsize=15)
        fTPVplot.tick_params(axis='x', labelsize=12)
        fTPVplot.set_ylabel('$V(mV)$', fontsize=15)
        fTPVplot.tick_params(axis='y', labelsize=12)
        fTPVplot.autoscale(tight=True)
        for v in list_of_v_exp: fTPVplot.plot(t_exp, v, 'k-', lw=1, ms=8, alpha=0.4)

        fTPVplot = fTPV.add_subplot(223)
        fTPVplot.set_title('$G9$ - $Exponential$ $fitting$ $of$ $Voltage$ x $Time$')
        fTPVplot.set_xlabel('$Time(\mu s)$', fontsize=15)
        fTPVplot.tick_params(axis='x', labelsize=12)
        fTPVplot.set_ylabel('$Ln(V)$', fontsize=15)
        fTPVplot.tick_params(axis='y', labelsize=12)
        fTPVplot.autoscale(tight=True)
        for t, v in zip(list_of_t_fit, list_of_v_exp_fit):
            fTPVplot.plot(t, v, 'k-', lw=1, ms=8, alpha=0.7)
        for t, v in zip(list_of_t_fit, list_of_fit):
            fTPVplot.plot(t, v, 'b-', lw=2, ms=8, alpha=0.6)

        fTPVplot = fTPV.add_subplot(122)
        fTPVplot.set_title('$G10$ - $Lifetime$ $and$ $\Delta V_0$ x $and$ $Suns$')
        fTPVplot.set_xlabel('$Suns$', fontsize=15)
        fTPVplot.tick_params(axis='x', labelsize=12)
        fTPVplot.set_ylabel('$Lifetime (s)$', color='g', fontsize=15)
        fTPVplot.tick_params(axis='y', labelcolor='g', labelsize=12)
        fTPVplot.grid(which='both')
        fTPVplottop = fTPVplot.twinx()
        fTPVplottop.set_ylabel('$\Delta V_0 (mV)$', color='r', fontsize=15)
        fTPVplottop.tick_params(axis='y', labelcolor='r', labelsize=12)
        fTPVplottop.grid(False)
        fTPVplot.loglog(suns, tau, 'g-o', lw=3, ms=8)
        fTPVplottop.loglog(suns, deltaV0, 'r-o', lw=3, ms=8)

        fTPV.set_tight_layout(True)

        return fTPV

    def updateDC(self): # CALLED BY aniDC
        voc           = TAQtGuiFunctions.whatIsThis('voc_LLC')
        voc_rev       = TAQtGuiFunctions.whatIsThis('voc_rev_LLC')
        C             = TAQtGuiFunctions.whatIsThis('DiffC')
        nce           = TAQtGuiFunctions.whatIsThis('n_CE')
        nce_rev       = TAQtGuiFunctions.whatIsThis('n_rev_CE')
        ndiffC        = TAQtGuiFunctions.whatIsThis('n_DiffC')
        ndiffC_rev    = TAQtGuiFunctions.whatIsThis('n_DiffC_rev')

        voc_fit, lnC_fit, voc_fit_rev, lnC_fit_rev, lnQ1, lnLT1, lnQ2, lnLT2, lnQ3, lnLT3, lnQ4, lnLT4 = readFits()
        fDC.clear()

        if self.separateGraphsDC.isChecked() :
            fDCplot = fDC.add_subplot(221)
            fDCplot.set_title('$G11$ - $Differential$ $Capacitance$ x $V_{oc}$')
            for label in fDCplot.get_xticklabels(): label.set_visible(False)
            fDCplot.set_ylabel('$Diff.$ $Capacitance$ $(F)$', fontsize=15)
            fDCplot.tick_params(axis='y', labelsize=12)
            fDCplot.semilogy(voc, C, 'k-o', lw=1, ms=8, label="Diff. Cap.")
            fDCplot.semilogy(voc_fit, np.exp(lnC_fit), color=self.colorsfit[0], lw=3, alpha=0.8)
            fDCplot.legend(fontsize="9",loc="best", framealpha=0.5)
            if self.useTightLayoutDC.checkState() :
                fDCplot.autoscale(tight=True)
            fDCplot = fDC.add_subplot(223, sharex = fDCplot)
            fDCplot.set_xlabel('$V_{oc}(V)$', fontsize=15)
            fDCplot.tick_params(axis='x', labelsize=12)
            for label in fDCplot.get_xticklabels(): label.set_rotation(30)
            fDCplot.set_ylabel('$Diff.$ $Capacitance$ $(F)$', fontsize=15)
            fDCplot.tick_params(axis='y', labelsize=12)
            fDCplot.semilogy(voc_rev, C, 'k-o', mfc='w', lw=1, ms=8, label="Diff. Cap. [rev]")
            fDCplot.semilogy(voc_fit_rev, np.exp(lnC_fit_rev), color=self.colorsfit[1], lw=3, alpha=0.8)
            fDCplot.legend(fontsize="9",loc="best", framealpha=0.5)
            if self.useTightLayoutDC.checkState() :
                fDCplot.autoscale(tight=True)
        else:
            fDCplot = fDC.add_subplot(121)
            fDCplot.set_title('$G11$ - $Differential$ $Capacitance$ x $V_oc$')
            fDCplot.set_xlabel('$V_{oc}(V)$', fontsize=15)
            fDCplot.tick_params(axis='x', labelsize=12)
            for label in fDCplot.get_xticklabels(): label.set_rotation(30)
            fDCplot.set_ylabel('$Diff.$ $Capacitance$ $(F)$', fontsize=15)
            fDCplot.tick_params(axis='y', labelsize=12)
            fDCplot.semilogy(voc, C, 'k-o', lw=1, ms=8, label="Diff. Cap.")
            fDCplot.semilogy(voc_fit, np.exp(lnC_fit), color=self.colorsfit[0], lw=3, alpha=0.8)
            fDCplot.semilogy(voc_rev, C, 'k-o', mfc='w', lw=1, ms=5, label="Diff. Cap. [rev]")
            fDCplot.semilogy(voc_fit_rev, np.exp(lnC_fit_rev), color=self.colorsfit[1], lw=3, alpha=0.8)
            fDCplot.legend(fontsize="9",loc="best", framealpha=0.5)
            if self.useTightLayoutDC.checkState() :
                fDCplot.autoscale(tight=True)

        if self.separateGraphsDC.isChecked() :
            fDCplot = fDC.add_subplot(222)
            fDCplot.set_title('$G12$ - $Charge$ $density$ x $V_{oc}$')
            for label in fDCplot.get_xticklabels(): label.set_visible(False)
            fDCplot.set_ylabel('$n( 10^{17} cm^{-3} )$', fontsize=15)
            fDCplot.tick_params(axis='y', labelsize=12)
            fDCplot.plot(voc, 1e-17*ndiffC, 'k-o', lw=1, ms=8, label="from Diff. Cap.")
            if len(nce) : fDCplot.plot(voc, 1e-17*nce, 'b-o', lw=1, ms=8, label="from CE")
            fDCplot.legend(fontsize="9",loc="best", framealpha=0.5)
            if self.useTightLayoutDC.checkState() :
                fDCplot.autoscale(tight=True)
            fDCplot = fDC.add_subplot(224, sharex = fDCplot)
            fDCplot.set_xlabel('$V_{oc}(V)$', fontsize=15)
            fDCplot.tick_params(axis='x', labelsize=12)
            for label in fDCplot.get_xticklabels(): label.set_rotation(30)
            fDCplot.set_ylabel('$n( 10^{17} cm^{-3} )$', fontsize=15)
            fDCplot.tick_params(axis='y', labelsize=12)
            fDCplot.plot(voc_rev, 1e-17*ndiffC_rev, 'k-o', mfc='w', lw=1, ms=8, label="from Diff. Cap. [rev]")
            if len(nce_rev) : fDCplot.plot(voc_rev, 1e-17*nce_rev, 'b-o', mfc='w', lw=1, ms=8, label="from CE [rev]")
            fDCplot.legend(fontsize="9",loc="best", framealpha=0.5)
            if self.useTightLayoutDC.checkState() :
                fDCplot.autoscale(tight=True)
        else:
            fDCplot = fDC.add_subplot(122)
            fDCplot.set_title('$G12$ - $Charge$ $density$ x $V_{oc}$')
            fDCplot.set_xlabel('$V_{oc}(V)$', fontsize=15)
            fDCplot.tick_params(axis='x', labelsize=12)
            for label in fDCplot.get_xticklabels(): label.set_rotation(30)
            fDCplot.set_ylabel('$n( 10^{17} cm^{-3} )$', fontsize=15)
            fDCplot.tick_params(axis='y', labelsize=12)
            fDCplot.plot(voc, 1e-17*ndiffC, 'k-o', lw=1, ms=8, label="from Diff. Cap.")
            fDCplot.plot(voc_rev, 1e-17*ndiffC_rev, 'k-o', mfc='w', lw=1, ms=5, label="from Diff. Cap. [rev]")
            if len(nce) : fDCplot.plot(voc, 1e-17*nce, 'b-o', lw=1, ms=8, label="from CE")
            if len(nce_rev) :fDCplot.plot(voc_rev, 1e-17*nce_rev, 'b-o', mfc='w', lw=1, ms=5, label="from CE [rev]")
            fDCplot.legend(fontsize="9",loc="best", framealpha=0.5)
            if self.useTightLayoutDC.checkState() :
                fDCplot.autoscale(tight=True)

        fDC.set_tight_layout(True)

        return fDC

    def updateLambda(self): # CALLED BY aniDC
        nce           = TAQtGuiFunctions.whatIsThis('n_CE')
        nce_rev       = TAQtGuiFunctions.whatIsThis('n_rev_CE')
        ndiffC        = TAQtGuiFunctions.whatIsThis('n_DiffC')
        ndiffC_rev    = TAQtGuiFunctions.whatIsThis('n_DiffC_rev')
        tau           = TAQtGuiFunctions.whatIsThis('tau')

        lambdas = readLambdas()

        voc_fit, lnC_fit, voc_fit_rev, lnC_fit_rev, lnQ1, lnLT1, lnQ2, lnLT2, lnQ3, lnLT3, lnQ4, lnLT4 = readFits()
        fLambda.clear()

        if self.separateGraphsLambda.isChecked() :
            fLambdaplot = fLambda.add_subplot(221)
            fLambdaplot.set_title('$G13$ - $Lifetime$ x $Charge$ $density$')
            fLambdaplot.set_xlabel('$n( cm^{-3} )$', fontsize=15)
            fLambdaplot.tick_params(axis='x', labelsize=12)
            fLambdaplot.set_ylabel('$Lifetime$ $(s)$', fontsize=15)
            fLambdaplot.tick_params(axis='y', labelsize=12)
            fLambdaplot.loglog(ndiffC, tau, 'k-o', lw=1, ms=8, label='from Diff. Cap. ($\lambda$ = %1.2f)' % float(lambdas['lambDC']))
            fLambdaplot.loglog(np.exp(lnQ1), np.exp(lnLT1), color=self.colorsfit[2], lw=3, alpha=0.8)
            fLambdaplot.legend(fontsize="14",loc="best", framealpha=0.5)
            if self.useTightLayoutLambda.isChecked() :
                fLambdaplot.autoscale(tight=True)

            fLambdaplot = fLambda.add_subplot(222)
            fLambdaplot.set_xlabel('$n( cm^{-3} )$', fontsize=15)
            fLambdaplot.tick_params(axis='x', labelsize=12)
            fLambdaplot.set_ylabel('$Lifetime$ $(s)$', fontsize=15)
            fLambdaplot.tick_params(axis='y', labelsize=12)
            fLambdaplot.loglog(ndiffC_rev, tau, 'k-o', mfc='w', lw=1, ms=8, label='from Diff. Cap. [rev] ($\lambda$ = %1.2f)' % float(lambdas['lambDC_rev']))
            fLambdaplot.loglog(np.exp(lnQ2), np.exp(lnLT2), color=self.colorsfit[3], lw=3, alpha=0.8)
            fLambdaplot.legend(fontsize="14",loc="best", framealpha=0.5)
            if self.useTightLayoutLambda.isChecked() :
                fLambdaplot.autoscale(tight=True)

            fLambdaplot = fLambda.add_subplot(223)
            fLambdaplot.set_xlabel('$n( cm^{-3} )$', fontsize=15)
            fLambdaplot.tick_params(axis='x', labelsize=12)
            fLambdaplot.set_ylabel('$Lifetime$ $(s)$', fontsize=15)
            fLambdaplot.tick_params(axis='y', labelsize=12)
            if len(lnLT3) :
                fLambdaplot.loglog(nce, tau, 'b-o', lw=1, ms=8, label='from CE ($\lambda$ = %1.2f)' % float(lambdas['lambCE']))
                fLambdaplot.loglog(np.exp(lnQ3), np.exp(lnLT3), color=self.colorsfit[4], lw=3, alpha=0.8)
                fLambdaplot.legend(fontsize="14",loc="best", framealpha=0.5)
            if self.useTightLayoutLambda.isChecked() :
                fLambdaplot.autoscale(tight=True)

            fLambdaplot = fLambda.add_subplot(224)
            fLambdaplot.set_xlabel('$n( cm^{-3} )$', fontsize=15)
            fLambdaplot.tick_params(axis='x', labelsize=12)
            fLambdaplot.set_ylabel('$Lifetime$ $(s)$', fontsize=15)
            fLambdaplot.tick_params(axis='y', labelsize=12)
            if len(lnLT4) :
                fLambdaplot.loglog(nce_rev, tau, 'b-o', mfc='w', lw=1, ms=8, label='from CE [rev] ($\lambda$ = %1.2f)' % float(lambdas['lambCE_rev']))
                fLambdaplot.loglog(np.exp(lnQ4), np.exp(lnLT4), color=self.colorsfit[5], lw=3, alpha=0.8)
                fLambdaplot.legend(fontsize="14",loc="best", framealpha=0.5)
            if self.useTightLayoutLambda.isChecked() :
                fLambdaplot.autoscale(tight=True)

        else:
            fLambdaplot = fLambda.add_subplot(111)
            fLambdaplot.set_title('$G13$ - $Lifetime$ x $Charge$ $density$')
            fLambdaplot.set_xlabel('$n( cm^{-3} )$', fontsize=15)
            fLambdaplot.tick_params(axis='x', labelsize=12)
            fLambdaplot.set_ylabel('$Lifetime$ $(s)$', fontsize=15)
            fLambdaplot.tick_params(axis='y', labelsize=12)
            fLambdaplot.loglog(ndiffC, tau, 'k-o', lw=1, ms=8, label='from Diff. Cap. ($\lambda$ = %1.2f)' % float(lambdas['lambDC']))
            fLambdaplot.loglog(np.exp(lnQ1), np.exp(lnLT1), color=self.colorsfit[2], lw=3, alpha=0.8)
            fLambdaplot.loglog(ndiffC_rev, tau, 'k-o', mfc='w', lw=1, ms=5, label='from Diff. Cap. [rev] ($\lambda$ = %1.2f)' % float(lambdas['lambDC_rev']))
            fLambdaplot.loglog(np.exp(lnQ2), np.exp(lnLT2), color=self.colorsfit[3], lw=3, alpha=0.8)
            if len(lnLT3) :
                fLambdaplot.loglog(nce, tau, 'b-o', lw=1, ms=8, label='from CE ($\lambda$ = %1.2f)' % float(lambdas['lambCE']))
                fLambdaplot.loglog(np.exp(lnQ3), np.exp(lnLT3), color=self.colorsfit[4], lw=3, alpha=0.8)
            if len(lnLT4) :
                fLambdaplot.loglog(nce_rev, tau, 'b-o', mfc='w', lw=1, ms=5, label='from CE [rev] ($\lambda$ = %1.2f)' % float(lambdas['lambCE_rev']))
                fLambdaplot.loglog(np.exp(lnQ4), np.exp(lnLT4), color=self.colorsfit[5], lw=3, alpha=0.8)
            fLambdaplot.legend(fontsize="14",loc="best", framealpha=0.5)
            if self.useTightLayoutLambda.isChecked() :
                fLambdaplot.autoscale(tight=True)

        fLambda.set_tight_layout(True)

        return fLambda

    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())