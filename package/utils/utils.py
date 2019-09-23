import numpy as np
import csv
import re
import linecache
import os
import dis
import inspect
import sys
import copy
import _pickle as pickle

from datetime import datetime
import logging
from math import isnan, isinf, sqrt
import pandas as pd
from scipy.signal import butter, lfilter, filtfilt

Nan = float("nan") # Not-a-number capitalized like None, True, False
Inf = float("inf") # infinite value capitalized ...





def list_folders(root):

    folder_list = []
    map_dict = {} # key = folder name; value = full folder path

    for root, dirs, files in os.walk(root):            

        for folder_name in dirs:                

            folder_list.append(folder_name)

            folder = os.path.join(root, folder_name)

            map_dict[folder_name] = folder 

    return folder_list, map_dict 


def list_files_without_suffix(root):

    file_list = []
    map_dict = {} # key = folder name; value = full folder path

    for root, dirs, files in os.walk(root):            

        for file_name in files:  

            fname =  os.path.splitext(file_name)[0]              

            file_list.append(fname)

            file = transform_separator(os.path.join(root, file_name))

            map_dict[fname] = file 

    return file_list, map_dict

def list_files(root):

    file_list = []
    map_dict = {} # key = folder name; value = full folder path

    for root, dirs, files in os.walk(root):            

        for file_name in files:                

            file_list.append(file_name)

            file = transform_separator(os.path.join(root, file_name))

            map_dict[file_name] = file 

    

    return file_list, map_dict   


def list_files_with_suffix(root, suffix_list):

    file_list = []
    map_dict = {} # key = folder name; value = full folder path

    for root, dirs, files in os.walk(root):            

        for file_name in files: 

            suffix =  os.path.splitext(file_name)[1]

            if suffix in suffix_list:                    

                file_list.append(file_name)

                file = transform_separator(os.path.join(root, file_name))

                map_dict[file_name] = file 

    

    return file_list, map_dict   


def relative_path(path):

    rpath = path.split('DataFiles/', 1)[1] 

    return rpath

def absolute_path(root, path):

    return os.path.join(root, path)

def renewed_path(new, old_path):

    rpath = old_path.split('DataFiles/', 1)[1] 

    return os.path.join(new, rpath)



def transform_separator(windows_path):
    linux_path = ''
    if windows_path != '':
        path_list = windows_path.split('\\')
        linux_path = '/'.join(path_list)
    else:
        print("it is null")
    return linux_path

def listDirectory(dirname):
    """Returns list of full paths to files and dirs in the given dir.
    Replaces '\' (backslash) and '\\' (double backslash) with '/' (slash)
    in returned paths to unify the path notation.
    """
    import glob
    
    full_names = glob.glob(os.path.join(dirname, '*'))
    for idx in range(len(full_names)):
        full_names[idx] = full_names[idx].replace('\\\\', '/')
        full_names[idx] = full_names[idx].replace('\\', '/')
    return full_names

def convert2underline(string):
    
    if "\\" in string:
        return string.replace('\\', '_', 1)
    elif "\\\\" in string:
        return string.replace('\\\\', '_', 1)
    elif '/' in string:
        return string.replace('/', '_' ,1)

    else:
        return string

def convert2filesep(string):
    
    sep = os.sep    

    if "_" in string:
        return string.replace('_', sep, 1)
        
    else:
        return string
        

def amp2rgb(Amp, minAmp,maxAmp):
    if Amp >= maxAmp:
        cindex = float(255)
    elif Amp <= minAmp:
        cindex = float(0)
    else:
        cindex = float(((255.0/(maxAmp-minAmp))*(Amp-minAmp)))

    vrgb=cm.seismic(int(cindex))
    return vrgb


def inverse_kron(K = np.array([]), array=np.array([]), input_id = 1):
    if input_id == 1:
        out = K[0:int(K.shape[0]/array.shape[0]), 0: int(K.shape[1]/array.shape[1])]/array[0][0]
    elif input_id == 2:
        out = K[0:K.shape[0]:array.shape[0], 0:K.shape[1]:array.shape[1]]/array[0][0] # a[start:end:step] 
    else:
        print('Error: The Input ID must be either 1 or 2')

    return out


 
 
# numerical txt to double-column format [[...],[...],[...]], i.e. dynamic 2D array
# then double-column format to numerical array via numpy
def txt_strtonum_feed(filename):
    data = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            eachline = line.split()
            read_data = [ float(x) for x in eachline[0:7] ] 
            lable = [ int(x) for x in eachline[-1] ]
            read_data.append(lable[0])
            #read_data = list(map(float, eachline))
            data.append(read_data)
            line = f.readline()
        return data #
 
# numerical txt to matrix array
def txt_to_matrix(filename):
    file=open(filename)
    lines=file.readlines()
    #print lines
    #['0.94\t0.81\t...0.62\t\n', ... ,'0.92\t0.86\t...0.62\t\n']形式
    rows=len(lines)
 
    datamat=np.zeros((rows,8))
 
    row=0
    for line in lines:
        line=line.strip().split('\t')#strip() remove spaces etc in strings
        datamat[row,:]=line[:]
        row+=1
 
    return datamat
 
 
# numerical txt to matrix array
def text_read(filename):
    # Try to read a txt file and return a matrix.Return [] if there was a mistake.
    try:
        file = open(filename,'r')
    except IOError:
        error = []
        return error
    content = file.readlines()
 
    rows=len(content)# number of rows
    datamat=np.zeros((rows,8))
    row_count=0
    
    for i in range(rows):
        content[i] = content[i].strip().split('\t')
        datamat[row_count,:] = content[i][:]
        row_count+=1
 
    file.close()
    return datamat
 
 

def loadCSV(filename):
        data = []
        with open(filename) as csvfile:
            csv_reader = csv.reader(csvfile)  
            header = next(csv_reader)  # read column titles of first row
            for row in csv_reader:   
                data.append(row)


        data = [[float(x) for x in row] for row in data]  # convert string type to float type


        data = np.array(data)  # convert default list type to array type
        header = np.array(header)
        # print(data.shape)  
        # print(header.shape)
        return data, header

def load_rcv_dict(filename):

    data = []
    with open(filename) as csvfile:
        csv_reader = csv.reader(csvfile)  
        header = next(csv_reader)  # read column titles of first row
        for row in csv_reader:   
            data.append(row)


    data = [[float(x) for x in row] for row in data]  # convert string type to float type


    data = np.array(data)  # convert default list type to array type
    header = np.array(header)

    geonames = data[:,0].astype(np.int_) # convert float type to string type

     
    
    rcv_dict = {'name': geonames,
            'x': data[:,1],
            'y': data[:,2],
            'z': data[:,3] }
    

    return rcv_dict


def loadCSV(filename):
        data = []
        with open(filename) as csvfile:
            csv_reader = csv.reader(csvfile)  
            header = next(csv_reader)  # read column titles of first row
            for row in csv_reader:   
                data.append(row)


        data = [[float(x) for x in row] for row in data]  # convert string type to float type


        data = np.array(data)  # convert default list type to array type
        header = np.array(header)
        # print(data.shape)  
        # print(header.shape)
        return data, header

def load_csv(filename, skipt = 1):
        
    data = []
    with open(filename) as csvfile:
        csv_reader = csv.reader(csvfile)  

        for i in range(skipt):
            header = next(csv_reader)  # read column titles of first row
        
        for row in csv_reader:   
            data.append(row)


    
    #data = [[float(x) for x in row] for row in data]  # convert string type to float type


    data = np.array(data)  # convert default list type to array type
    
    return data

def load_vm_dict(filename):

    data = []
    with open(filename) as csvfile:
        csv_reader = csv.reader(csvfile)  
        header = next(csv_reader)  # read column titles of first row
        for row in csv_reader:   
            data.append(row)


    data = [[float(x) for x in row] for row in data]  # convert string type to float type


    data = np.array(data)  # convert default list type to array type
    header = np.array(header)
    
    vm_dict = {'z': data[:,0],
            'vp': data[:,1],
            'vs': data[:,2] }
    

    return vm_dict

def nargout():
    """
    Return how many values the caller is expecting
    taken from
    http://stackoverflow.com/questions/16488872/python-check-for-the-number-of-output-arguments-a-function-is-called-with
    """
    if sys.version_info[1] > 5:
        off = 1
    else:
        off = 0
    f = inspect.currentframe()
    f = f.f_back.f_back
    c = f.f_code
    i = f.f_lasti
    bytecode = c.co_code
    instruction = bytecode[i+3-off]
    if instruction == dis.opmap['UNPACK_SEQUENCE']:
        howmany = bytecode[i+4-off]
        return howmany
    elif instruction == dis.opmap['POP_TOP']:
        return 0
    return 1

    
def create_folder(directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print ('Error: Creating directory. ' +  directory)

def createFile(file):
        try:
            if not os.path.exists(file):
                fp = open(file, 'w')
                fp.close()
        except OSError:
            print ('Error: Creating file. ' +  file)


def _ignorable_(line):
    line = line.strip()
    if not line or (len(line) >= 2 and line[:2] == "--"):
        return True # ignorable, yes
    return False

def read_next_tokenline(f):
    token = ""
    while _ignorable_(token):
        token = f.readline()
        if not token:
            return None
        token = strip_line(token)
    return token

def strip_line(l):
    """strips string and replace tabs and multiple spaces with single space."""
    l = l.replace("\t", " ")
    while "  " in l:
        l = l.replace("  ", " ")
    return l.strip()

def parse_date(s):
    """Returns a datetime string if input is either YYYY, YYYY-MM or YYYY-MM-DD.
    """
    d = None
    try:
        d = datetime.strptime(s, '%Y-%m-%d')
    except Exception:
        pass
    try:
        d = datetime.strptime(s, '%Y-%m')
    except Exception:
        pass
    try:
        d = datetime.strptime(s, '%Y')
    except Exception:
        pass

    if d is None:
        raise ValueError('Provide a datetime string on the form YYYY-MM-DD, YYYY-MM, or YYYY, not %s'
                         % str(s))
    return d

def read_config(fname):
    """Reads given file (as filename) and yields every non-empty line not
       starting with --, whitespaces ignored."""
    with open(fname, "r") as f:
        for line in f:
            l = line.strip()
            if len(l) == 0 or (len(l) >= 2 and l[:2] == "--"):
                continue
            else:
                yield strip_line(l)


def roundAwayFromEven(val):
    """Eclipse cannot deal with values close to even integers.  We
       (in)sanitize the value so that it always will be at least 0.1m away
       from an even integer.
       This function only makes sense should you assume cell floors are at even
       integers.
    """
    epsilon = 0.1
    r = val%2.0
    if r < epsilon:
        return round(val) + epsilon
    if r > (2.0 - epsilon):
        return round(val) - epsilon
    return val


def findRestartStep(restart, date):
    """Finds the last restart step in the given restart file before the given date.
    """
    # start at 1, since we return step - 1
    for step in range( 1, restart.num_report_steps() ):
        new_date = restart.iget_restart_sim_time(step) # step date
        if new_date > date:
            return step - 1

    # did not find it, return len - 1
    return step

def findKeyword(kw, restart, date, step = None):
    """Find and return kw (EclKW) from restart file at the last step before given
       date.
    """
    if not step:
        step = findRestartStep(restart, date)
    if not (0 <= step < restart.num_report_steps()):
        raise ValueError('restart step out of range 0 <= %d < steps' % step)
    return restart.iget_named_kw(kw, step)


def enterSnapMode(mode, wp, idx):
    """Checks if we are in snap mode.  This happens if we are already snapping, or
       if we have reached a prescribed window depth.
    """
    if mode or not wp.depthType():
        return True
    t = wp.depthType()

    return wp[t][idx] >= wp.windowDepth()

def finiteFloat(elt):
    return not (isinf(elt) or isnan(elt))

def close(f1, f2, epsilon=0.0001):
    """Checks if f1~f2 with epsilon accuracy."""
    return abs(f1-f2) <= epsilon

def tryFloat(val, ret = 0):
    try:
        return float(val)
    except ValueError:
        return ret

def dist(p1,p2):
    """Returns Euclidean distance between p1 and p2, i.e. Pythagoras.
       Works on coordinates of any dimension.  If p1 and p2 have different
       dimensionality, we pick the min(len(p1), len(p2)) first points of each
       coordinate.
    """
    return sqrt(sum([(e[0] - e[1])**2 for e in zip(p1,p2)]))

def save_dict(di_, filename_):
    with open(filename_, 'wb') as f:
        pickle.dump(di_, f)
        return True

def load_dict(filename_):

    size = os.path.getsize(filename_)
    if size != 0:             
        with open(filename_, 'rb') as f:
            ret_di = pickle.load(f)
        return ret_di
    else:
        return {}

def unique_list(listA):
    return sorted(set(listA), key = listA.index)

def reduce_list(listA, listB): # sequence of elements will change randomly
     return list(set(listA) - set(listB))


def find_commons(aa, bb):

    a = aa.copy()
    b = bb.copy()   

    commons = set(a)&set(b)            

    sorter = np.argsort(aa)
    a_inds = sorter[np.searchsorted(aa, np.array(list(commons)), sorter=sorter)]
   
    sorter = np.argsort(bb)
    b_inds = sorter[np.searchsorted(bb, np.array(list(commons)), sorter=sorter)]

    
    return a_inds, b_inds


def transform_dict(dic):

    if len(dic):
        
        
        for key, value in dic.items():

            if isinstance(value, float) or isinstance(value, dict):
        
                dic[key] = np.array([value])

            elif isinstance(value, list):

                dic[key] = copy.deepcopy(np.array(value))

    return dic
