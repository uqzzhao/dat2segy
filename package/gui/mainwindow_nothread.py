
import os

from PyQt5.QtCore import  Qt

from PyQt5.QtWidgets import  QApplication, QComboBox, QDesktopWidget, QDialogButtonBox, QDockWidget, QFrame,\
                             QFileDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSizePolicy, \
                                  QWidget, QProgressBar

from package.thread.segyconverter import SegyConverterThread
from ..psmodule import pssegy 
from ..utils.utils import save_dict, transform_separator
import datetime
import struct
import numpy as np
import copy
import resources_rc

l_int = struct.calcsize('i')
l_uint = struct.calcsize('I')
l_long = 4
# Next line gives wrong result on Linux!! (gives 8 instead of 4)
# l_long = struct.calcsize('l')
l_ulong = struct.calcsize('L')
l_short = struct.calcsize('h')
l_ushort = struct.calcsize('H')
l_char = struct.calcsize('c')
l_uchar = struct.calcsize('B')
l_float = struct.calcsize('f')

HeadInfo_def = {"day": {"pos": 0, "type": "short", "def": 0, "number": 1}}
HeadInfo_def['month'] = {"pos": 2, "type": "short", "def": 0, "number": 1}
HeadInfo_def['year'] = {"pos": 4, "type": "short", "def": 0, "number": 1}
HeadInfo_def['hour'] = {"pos": 6, "type": "short", "def": 0, "number": 1}
HeadInfo_def['minute'] = {"pos": 8, "type": "short", "def": 0, "number": 1}
HeadInfo_def['geo'] = {"pos": 10, "type": "uchar", "def": '0', "number": 20}
HeadInfo_def['sec'] = {"pos": 30, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['met'] = {"pos": 31, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['standby1'] = {"pos": 32, "type": "uchar", "def": '0', "number": 21}
HeadInfo_def['lst'] = {"pos": 52, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['pro'] = {"pos": 53, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['kan'] = {"pos": 54, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['standby2'] = {"pos": 55, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['ab1'] = {"pos": 56, "type": "short", "def": 0, "number": 1}
HeadInfo_def['ab2'] = {"pos": 58, "type": "short", "def": 0, "number": 1}
HeadInfo_def['ab3'] = {"pos": 60, "type": "short", "def": 0, "number": 1}
HeadInfo_def['res'] = {"pos": 62, "type": "short", "def": 0, "number": 1}
HeadInfo_def['Tok'] = {"pos": 64, "type": "float", "def": 0, "number": 1}
HeadInfo_def['Voltage'] = {"pos": 68, "type": "float", "def": 0, "number": 1}

HeadInfo_def['Tgu'] = {"pos": 72, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['Ddt'] = {"pos": 73, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['Tpi'] = {"pos": 74, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['Ngu'] = {"pos": 75, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['C_Prd'] = {"pos": 79, "type": "int32", "def": 0, "number": 1}
HeadInfo_def['C_Pls'] = {"pos": 83, "type": "int32", "def": 0, "number": 1}
HeadInfo_def['standby7'] = {"pos": 87, "type": "uchar", "def": '0', "number": 1}
HeadInfo_def['Nom'] = {"pos": 92, "type": "short", "def": 0, "number": 1}
HeadInfo_def['cugb_sps'] = {"pos": 94, "type": "short", "def": 0, "number": 1}
HeadInfo_def['cugb_ch0gain'] = {"pos": 96, "type": "short", "def": 0, "number": 1}
HeadInfo_def['cugb_ch1gain'] = {"pos": 98, "type": "short", "def": 0, "number": 1}
HeadInfo_def['cugb_ch2gain'] = {"pos": 100, "type": "short", "def": 0, "number": 1}
HeadInfo_def['cugb_ch3gain'] = {"pos": 102, "type": "short", "def": 0, "number": 1}
HeadInfo_def['Fam'] = {"pos": 104, "type": "uchar", "def": '0', "number": 1}


HeadInfo_def['Lps'] = {"pos": 120, "type": "uint32", "def": 0}

def ibm2ieee2(ibm_float):
    """
    ibm2ieee2(ibm_float)
    Used by permission
    (C) Secchi Angelo
    with thanks to Howard Lightstone and Anton Vredegoor. 
    """
    dividend = float(16 ** 6)

    if ibm_float == 0:
        return 0.0
    istic, a, b, c = struct.unpack('>BBBB', ibm_float)
    if istic >= 128:
        sign = -1.0
        istic = istic - 128
    else:
        sign = 1.0
    mant = float(a << 16) + float(b << 8) + float(c)
    return sign * 16 ** (istic - 64) * (mant / dividend)


def getValue(data, index, ctype='l', endian='>', number=1):
    """
    getValue(data,index,ctype,endian,number)
    """
    if (ctype == 'l') | (ctype == 'long') | (ctype == 'int32'):
        size = l_long
        ctype = 'l'
    elif (ctype == 'L') | (ctype == 'ulong') | (ctype == 'uint32'):
        size = l_ulong
        ctype = 'L'
    elif (ctype == 'h') | (ctype == 'short') | (ctype == 'int16'):
        size = l_short
        ctype = 'h'
    elif (ctype == 'H') | (ctype == 'ushort') | (ctype == 'uint16'):
        size = l_ushort
        ctype = 'H'
    elif (ctype == 'c') | (ctype == 'char'):
        size = l_char
        ctype = 'c'
    elif (ctype == 'B') | (ctype == 'uchar'):
        size = l_uchar
        ctype = 'B'
    elif (ctype == 'f') | (ctype == 'float'):
        size = l_float
        ctype = 'f'
    elif (ctype == 'ibm'):
        size = l_float
        ctype = 'ibm'
    else:
        print('Bad Ctype : ' + ctype, -1)

    index_end = index + size * number

    #printverbose("index=%d, number=%d, size=%d, ctype=%s" % (index, number, size, ctype), 8);
    #printverbose("index, index_end = " + str(index) + "," + str(index_end), 9)

    if (ctype == 'ibm'):
        # ASSUME IBM FLOAT DATA
        Value = list(range(int(number)))
        for i in np.arange(number):
            index_ibm_start = i * 4 + index
            index_ibm_end = index_ibm_start + 4
            ibm_val = ibm2ieee2(data[index_ibm_start:index_ibm_end])
            Value[i] = ibm_val
        # this resturn an array as opposed to a tuple    
    else:
        # ALL OTHER TYPES OF DATA
        cformat = 'f' * number
        cformat = endian + ctype * number

        #printverbose("getValue : cformat : '" + cformat + "'", 11)

        Value = struct.unpack(cformat, data[index:index_end])

    if (ctype == 'B'):
        #printverbose('getValue : Ineficient use of 1byte Integer...', -1)

        vtxt = 'getValue : ' + 'start=' + str(index) + ' size=' + str(size) + ' number=' + str(
            number) + ' Value=' + str(Value) + ' cformat=' + str(cformat)
        #printverbose(vtxt, 20)

    if number == 1:
        return Value[0], index_end
    else:
        return Value, index_end


class MainWindow(QMainWindow):  
     
   

    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)


        self.inpath = None
        self.outpath = None 

        self.inFlag = False
        self.outFlag = False

        self.thread = None

    

        # last directory opened
        self.lastDir = 'C:/'         
        
        self.initUI()        
        
        

    def initUI(self):      
        
        self.setWindowTitle('DeepListen SEG-Y Converter')      

        # Adjust screen size
        dw = QDesktopWidget()
        scrCount = dw.screenCount()
        if (scrCount > 1):
            self.iWidth = dw.width()/2
        else:
            self.iWidth = dw.width()
        
        self.iHeight = dw.height()




        self.inButton = QPushButton(u'   Input Directory...', parent=self) 
        self.inLineEdit = QLineEdit(parent=self)

        self.outButton = QPushButton(u'Output Directory...', parent=self) 
        self.outLineEdit = QLineEdit(parent=self) 

        

      
        
        # add line
        self.line = QFrame()
        self.line.setFrameShape(QFrame().HLine)
        self.line.setFrameShadow(QFrame().Sunken)        


        self.progressLabel = QLabel('Converting progress') # progerssbar label showing which process is running
        self.progressBar = QProgressBar(self)


        # Create ButtonBox for OK and Cancel
        self.buttonBox = QDialogButtonBox(parent=self)
        self.buttonBox.setOrientation(Qt.Horizontal) # horizontal
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok) 
        self.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("Convert"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))
        

        
        grid = QGridLayout()
        grid.addWidget(self.inButton,  0, 0, 1, 1, Qt.AlignRight)
        grid.addWidget(self.inLineEdit, 0, 1, 1, 3)
        grid.addWidget(self.outButton,  1, 0, 1, 1, Qt.AlignRight)
        grid.addWidget(self.outLineEdit, 1, 1, 1, 3)
        


        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.progressLabel)
        vbox1.addWidget(self.progressBar)
        
        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(self.line)
        vbox.addLayout(vbox1)
        vbox.addWidget(self.buttonBox)


        




        self.main = QWidget()
        self.setCentralWidget(self.main)
        self.main.setLayout(vbox)  


        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

        self.resize(400, 180)   

        # Connect all necessary signals and slots.
        self._connect_signals_and_slots()
        #self._add_handlers_for_config()
         


    def _connect_signals_and_slots(self):

        self.inButton.clicked.connect(self.onInput)
        self.outButton.clicked.connect(self.onOutput)

        
        self.buttonBox.accepted.connect(self.convert) # OK
        self.buttonBox.rejected.connect(self.cancelConversion) # Cancel
        
    def createActions(self):
        pass


    def createMenus(self):

        pass

    def createToolBars(self):
        pass
        
    def createStatusBar(self):
        pass


    


    def onInput(self):

        folderPath = QFileDialog.getExistingDirectory(self,"Select Directory Containing .DAT Files", self.lastDir)
        
        if folderPath:
            self.inLineEdit.setText(folderPath)
            self.inpath = transform_separator(folderPath)
            self.lastDir = self.inpath

            self.inFlag = True



    def onOutput(self):

        folderPath = QFileDialog.getExistingDirectory(self,"Select Directory to Save SEG-Y Files", self.lastDir)
        
        if folderPath:
            self.outLineEdit.setText(folderPath)
            self.outpath = transform_separator(folderPath)
            self.lastDir = self.outpath

            self.outFlag = True


    def closeEvent(self, event):
        
        """
        redefined closeEvent method
        :param event: close() triggered event
        :return: None
        """

        if self.thread != None:
    
            self.thread.stop()

        event.accept()
        
    def setProgressLabel(self, text):
    
        self.progressLabel.setText(text)
    
    def updateLabel(self, str):

        self.setProgressLabel(str)

    def updateProgress(self, i, imax):   

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(imax)
        self.progressBar.setValue(i)        
              

    def finishProgress(self, completion, str):   
        #self.completion = self.getCompletionStatus(completion)
        self.setProgressLabel(str)
        self.runButton.setEnabled(True)


    def cancelConversion(self):
        
        reply = QMessageBox.critical(self,"Abortion Request", "Are you sure to abort this conversion process?",  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:

            if self.thread != None:

                if self.thread.isRunning():
                    self.thread.stop()
                    
                    self.setAbortStatus()
        else:

            return          
            
    def setAbortStatus(self):

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.setProgressLabel ("Conversion stopped. Click 'Convert' to restart the conversion process.")

    
    def killThread(self):
        
        self.thread.stop() # terminate thread


    def showError(self, msg):
        
        self.killThread()
        
        QMessageBox.critical(self,"Error", msg,
                    QMessageBox.Ok)
        
    def convert(self):

        if self.inFlag and self.outFlag:



            file_list_z, file_list_x, file_list_y, map_dict_z, map_dict_x, map_dict_y, rcvlist, timelist, sizelist = self.datParser(self.inpath)

            self.file_list_z = file_list_z
            self.file_list_x = file_list_x
            self.file_list_y = file_list_y
            self.map_dict_z =  map_dict_z
            self.map_dict_x =  map_dict_x
            self.map_dict_y = map_dict_y
            self.rcvlist = rcvlist
            self.timelist =  timelist
            self.sizelist = sizelist

    

            self.traces_z = None
            self.traces_x = None
            self.traces_y = None


            self.readDat()
            self.exportSegy()

            

    
    def getTraceData(self, filename, lapse, ns):
    
        HeadInfo = {}

        f = open(filename, 'rb')
        data = f.read()

        j = 0
        for key in HeadInfo_def.keys():
            # print('entry')
            j = j + 1
            pos = HeadInfo_def[key]["pos"] 
            fmt = HeadInfo_def[key]["type"]

    
            HeadInfo[key], index = getValue(data, pos, fmt, endian = '<')

    

        ## read trace data
        filesize = len(data)
        ind = 2048
        bps = 4 # float
        nsamples = int((filesize - ind) / bps)        
        index_end = ind + bps * nsamples
        ctype = 'l'
        endian = '<'
        cformat = ctype * nsamples
        cformat = endian + ctype * nsamples

        
        

        # GET TRACE   
        # print('entry unpack')
        traceData = struct.unpack(cformat, data[ind:index_end]) 
        

        f.close()

        

        return np.array(traceData[lapse:lapse + ns])

    
    def readDat(self):

      
        # deal with time lapses
        timestamp = max(self.timelist)

        dt_max = timestamp

        lengths = []
        lapses = []
        dt = 0.001 # seconds
        ind = 2048
        bps = 4 # float

        for i, d_t in enumerate(self.timelist):

            lapse = int((dt_max - d_t).total_seconds()/dt)
            filesize = self.sizelist[i]  
            lapses.append(lapse)
            lengths.append(int((filesize - ind) / bps) - lapse)


        NS = min(lengths) - 30000          

        ntr = len(self.file_list_z) 

        maxVal = ntr

        self.traces_z = np.zeros((NS, ntr))
        self.traces_x = np.zeros((NS, ntr))
        self.traces_y = np.zeros((NS, ntr))  
       

        itr = 0

        for fz, fx, fy in zip(self.file_list_z, self.file_list_x, self.file_list_y):

        

            lapse = lapses[itr]

         
    
            filepath_z = self.map_dict_z[fz]
            filepath_x = self.map_dict_x[fx]
            filepath_y = self.map_dict_y[fy]

            

            self.traces_z[:,itr] = copy.deepcopy(self.getTraceData(filepath_z, lapse, NS))
            self.traces_x[:,itr] = copy.deepcopy(self.getTraceData(filepath_x, lapse, NS))
            self.traces_y[:,itr] = copy.deepcopy(self.getTraceData(filepath_y, lapse, NS))

            print("Loading #" + str(itr+1) + " file...")  
            itr += 1

            

     

         

    def exportSegy(self):


        zdata = self.traces_z
        xdata = self.traces_x
        ydata = self.traces_y      


        # deal with time lapses
        timestamp = max(self.timelist)

        interval = 60 # second

        NS, _ = zdata.shape

        nfile = int(NS/(interval * 1000)) - 1 

        maxVal = nfile
        
        for i in range(nfile):            
    
            istart = i * interval * 1000 
            iend = (i + 1) * interval * 1000 
            ztrace = zdata[istart:iend,:]  
            xtrace = xdata[istart:iend,:]  
            ytrace = ydata[istart:iend,:]  

            trace = np.concatenate((ztrace, xtrace, ytrace), axis = 1)

     

            ## prepare SEGY header
            dt = 1000
            ns, ntr = trace.shape
            

            SH = pssegy.getDefaultSegyHeader(ntr, ns)
            STH = pssegy.getDefaultSegyTraceHeaders(ntr, ns, dt) 

            STH['TraceIdentificationCode'][0:int(ntr/3)] = 12.0
            STH['TraceIdentificationCode'][int(ntr/3): 2*int(ntr/3)] = 13.0
            STH['TraceIdentificationCode'][2*int(ntr/3): 3*int(ntr/3)] = 14.0

            STH['Inline3D'][0:int(ntr/3)] = np.array(self.rcvlist)
            STH['Inline3D'][int(ntr/3): 2*int(ntr/3)] = np.array(self.rcvlist)
            STH['Inline3D'][2*int(ntr/3): 3*int(ntr/3)] = np.array(self.rcvlist)


            # deal with date time
            
            ns_start = int(istart/1000) # delayed seconds
            # delay_hour = (ns_start/1000/60)//60
            # delay_min = floor(ns_start/1000/60)%60)
            # delay_sec = (ns_start/1000/60)%60 - delay_min) * 60

            
            d = datetime.timedelta(seconds=ns_start)
            new_timestamp = timestamp+d

            record_day = datetime.datetime(2018,12,1)
            day_of_year = (record_day - datetime.datetime(record_day.year, 1, 1)).days + 1
            #print(day_of_year)
            

            STH['YearDataRecorded'] = np.ones((ntr,), dtype = np.float) * 2018.0
            STH['DayOfYear'] = np.ones((ntr,), dtype = np.float) * day_of_year
            STH['HourOfDay'] = np.ones((ntr,), dtype = np.float) * new_timestamp.hour
            STH['MinuteOfHour'] = np.ones((ntr,), dtype = np.float) * new_timestamp.minute
            STH['SecondOfMinute'] = np.ones((ntr,), dtype = np.float) * new_timestamp.second
            

            base_name = new_timestamp.strftime("%Y%m%d_%H%M%S")

            filename = os.path.join(self.outpath, base_name + '.sgy')  

            pssegy.writeSegy(filename, Data= trace, dt = 1000, STHin=STH, SHin=SH)


            
       

    def datParser(self, root):

    
        file_list_z = []
        map_dict_z = {} # key = folder name; value = full folder path
        
        time_list = []
        rcv_list = []
        size_list = []

        file_list_x = []
        map_dict_x = {}

        file_list_y = []
        map_dict_y = {}

        for root, dirs, files in os.walk(root):            

            for file_name in files:     

                suffix =  os.path.splitext(file_name)[1]     

                if suffix == '.dat' and 'ch01' in file_name:    

                    ss = file_name.split('_')  
                    rname = float(ss[0])
                    rcv_list.append(rname)
                    dates = ss[2]                    
                    times = ss[3]

                    time_list.append(datetime.datetime(int(dates[0:4]), int(dates[4:6]), int(dates[6:8]),
                                                    int(times[0:2]), int(times[2:4]), int(times[4:6])))

                    file_list_z.append(file_name)

                    file = transform_separator(os.path.join(root, file_name))

                    size = os.path.getsize(file)
                    size_list.append(size)

                    map_dict_z[file_name] = file 

                elif suffix == '.dat' and 'ch02' in file_name:      

                    file_list_x.append(file_name)

                    file = transform_separator(os.path.join(root, file_name))

                    map_dict_x[file_name] = file 

                elif suffix == '.dat' and 'ch03' in file_name:      

                    file_list_y.append(file_name)

                    file = transform_separator(os.path.join(root, file_name))

                    map_dict_y[file_name] = file 

        

        return file_list_z, file_list_x, file_list_y, map_dict_z, map_dict_x, map_dict_y, rcv_list, time_list, size_list   

         

  
