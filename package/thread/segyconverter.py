# -*- coding: utf-8 -*-

import os
import copy

from PyQt5.QtCore import pyqtSignal, QThread
from ..psmodule import pssegy 
from ..utils.utils import save_dict, transform_separator

import numpy as np
import time
import struct
import datetime

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



class SegyConverterThread(QThread):
    """
    Thread for merging SEGY files
    """
    labelSignal_ = pyqtSignal(str)
    progressSignal_ = pyqtSignal(int, int)
    
    finishSignal_ = pyqtSignal(int, str)

    sendError_ = pyqtSignal(str)


    def __init__(self, file_list_z, file_list_x, file_list_y, map_dict_z, map_dict_x, map_dict_y, rcvlist, timelist, sizelist, outpath, parent=None):
        super(SegyConverterThread, self).__init__(parent)

        
        self.running = True

        
        
        self.file_list_z = file_list_z
        self.file_list_x = file_list_x
        self.file_list_y = file_list_y
        self.map_dict_z =  map_dict_z
        self.map_dict_x =  map_dict_x
        self.map_dict_y = map_dict_y
        self.rcvlist = rcvlist
        self.timelist =  timelist
        self.sizelist = sizelist

        self.outpath = outpath


        self.traces_z = None
        self.traces_x = None
        self.traces_y = None
        


    
    def run(self):

        try:

            self.readDat()
            self.exportSegy()

        except  Exception as reason:
            
            self.sendError_.emit(str(reason))

    def stop(self):
    
        self.running = False
        
        self.terminate()
    
    def __del__(self):

        self.quit()
        self.wait()


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

        

        return np.array(traceData[lapse:lapse + ns]).astype(np.float)

    
    def readDat(self):

        self.labelSignal_.emit("Loading .dat files in process...")

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


        self.progressSignal_.emit(0, maxVal)

        itr = 0

        for fz, fx, fy in zip(self.file_list_z, self.file_list_x, self.file_list_y):

            if not self.running:                                       
                self.running = True
                break
                                
           

            lapse = lapses[itr]

            self.labelSignal_.emit("Loading #" + str(itr+1) + " file...")                         
    
            filepath_z = self.map_dict_z[fz]
            filepath_x = self.map_dict_x[fx]
            filepath_y = self.map_dict_y[fy]

            

            self.traces_z[:,itr] = copy.deepcopy(self.getTraceData(filepath_z, lapse, NS))
            self.traces_x[:,itr] = copy.deepcopy(self.getTraceData(filepath_x, lapse, NS))
            self.traces_y[:,itr] = copy.deepcopy(self.getTraceData(filepath_y, lapse, NS))

            self.progressSignal_.emit(itr + 1, maxVal)
            
            
            itr += 1

        
        self.labelSignal_.emit('Loading .dat files completed.')        
         

    def exportSegy(self):

        self.labelSignal_.emit("Writing to SEG-Y files in process...")

        zdata = self.traces_z
        xdata = self.traces_x
        ydata = self.traces_y      


        # deal with time lapses
        timestamp = max(self.timelist)

        interval = 60 # second

        NS, _ = zdata.shape

        nfile = int(NS/(interval * 1000)) - 1

        maxVal = nfile
        self.progressSignal_.emit(0, maxVal)

        for i in range(nfile):

            if not self.running:                                       
                self.running = True
                break
                                
            
    
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

            filename = transform_separator(os.path.join(self.outpath, base_name + '.sgy'))  

            pssegy.writeSegy(filename, Data= trace, dt = 1000, STHin=STH, SHin=SH)

            self.labelSignal_.emit('Writing SEG-Y file: ' + filename)                         
            self.progressSignal_.emit(i+1, maxVal)     



            
        self.finishSignal_.emit(int(1), 'SEG-Y files conversion completed.')  
           

    
    
    
    