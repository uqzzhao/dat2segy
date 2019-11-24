# -*- coding: utf-8 -*-
"""
Data format conversion from .dat to SEG-Y format.

@author:     Zhengguang Zhao
@copyright:  Copyright 2016-2019, Zhengguang Zhao.
@license:    MIT
@contact:    zg.zhao@outlook.com


"""

from __future__ import division
from __future__ import print_function

import os
import struct, sys 
import re

import datetime
import numpy as np
import pandas as pd



from PyQt5.QtWidgets import QMessageBox

from ..utils.utils import load_dict, transform_separator



endian='>' # Big Endian  
endian='<' # Little Endian
endian='=' # Native


NUMPY_DTYPES = {'ibm':     np.dtype('>f4'),

                'int32':   np.dtype('>i4'),

                'int16':   np.dtype('>i2'),

                'uint16':   np.dtype('>u2'),

                'float32': np.dtype('>f4'),

                'int8':    np.dtype('>i1')}




SEGY_ASCII_REEL_HEADER_BYTES=3200
SEGY_ASCII_REEL_HEADER_RECORD_BYTES=80
SEGY_BIN_REEL_HEADER_BYTES=400
# TRACES_HEADER_TYPE = np.dtype( [ ('tracl' , '>i4'), ('tracr' , '>i4'), ('fldr' , '>i4'), ('tracf' , '>i4'), ('ep' , '>i4'), ('cdp' , '>i4'), ('cdpt' , '>i4'), ('trid' , '>u2'), ('nvs' , '>u2'), ('nhs' , '>u2'), ('duse' , '>u2'), ('offset' , '>i4'), ('gelev' , '>i4'), ('selev' , '>i4'), ('sdepth' , '>i4'), ('gdel' , '>i4'), ('sdel' , '>i4'), ('swdep' , '>i4'), ('gwdep' , '>i4'), ('scalel' , '>u2'), ('scalco' , '>u2'), ('sx' , '>i4'), ('sy' , '>i4'), ('gx' , '>i4'), ('gy' , '>i4'), ('counit' , '>u2'), ('wevel' , '>u2'), ('swevel' , '>u2'), ('sut' , '>u2'), ('gut' , '>u2'), ('sstat' , '>u2'), ('gstat' , '>u2'), ('tstat' , '>u2'), ('laga' , '>u2'), ('lagb' , '>u2'), ('delrt' , '>u2'), ('muts' , '>u2'), ('mute' , '>u2'), ('ns' , '>u2'), ('dt' , '>u2'), ('gain' , '>u2'), ('igc' , '>u2'), ('igi' , '>u2'), ('corr' , '>u2'), ('sfs' , '>u2'), ('sfe' , '>u2'), ('slen' , '>u2'), ('styp' , '>u2'), ('stas' , '>u2'), ('stae' , '>u2'), ('tatyp' , '>u2'), ('afilf' , '>u2'), ('afils' , '>u2'), ('nofilf' , '>u2'), ('nofils' , '>u2'), ('lcf' , '>u2'), ('hcf' , '>u2'), ('lcs' , '>u2'), ('hcs' , '>u2'), ('year' , '>u2'), ('day' , '>u2'), ('hour' , '>u2'), ('minute' , '>u2'), ('sec' , '>u2'), ('timbas' , '>u2'), ('trwf' , '>u2'), ('grnors' , '>u2'), ('grnofr' , '>u2'), ('grnlof' , '>u2'), ('gaps' , '>u2'), ('ofrav' , '>u2'), ('d1' , '>f4'), ('f1' , '>f4'), ('d2' , '>f4'), ('f2' , '>f4'), ('ungpow' , '>i4'), ('unscale' , '>i4'), ('ntr' , '>i4'), ('mark' , '>u2'), ('shortpad' , '>u2'), ('unass' , 'a28') ])

VOLUME_HEADER_TYPE = np.dtype([('Job', '>i4'),\
                            ('Line', '>i4'),\
                            ('Reel', '>i4'),\
                            ('DataTracePerEnsemble', '>i2'),\
                            ('AuxiliaryTracePerEnsemble', '>i2'),\
                            ('dt', '>u2'),\
                            ('dtOrig', '>u2'),\
                            ('ns', '>u2'),\
                            ('nsOrig', '>u2'),\
                            ('DataSampleFormat', '>i2'),\
                            ('EnsembleFold', '>i2'),\
                            ('TraceSorting', '>i2'),\
                            ('VerticalSumCode', '>i2'),\
                            ('SweepFrequencyStart', '>i2'),\
                            ('SweepFrequencyEnd', '>i2'),\
                            ('SweepLength', '>i2'),\
                            ('SweepType', '>i2'),\
                            ('SweepChannel', '>i2'),\
                            ('SweepTaperlengthStart', '>i2'),\
                            ('SweepTaperLengthEnd', '>i2'),\
                            ('TaperType', '>i2'),\
                            ('CorrelatedDataTraces', '>i2'),\
                            ('BinaryGain', '>i2'),\
                            ('AmplitudeRecoveryMethod', '>i2'),\
                            ('MeasurementSystem', '>i2'),\
                            ('ImpulseSignalPolarity', '>i2'),\
                            ('VibratoryPolarityCode', '>i2')                            
                            ])


TRACES_HEADER_TYPE = np.dtype( [ ('TraceSequenceLine' , '>i4'), \
                                ('TraceNumber' , '>i4'), \
                                ('FieldRecord' , '>i4'), \
                                 ('TraceSequenceFile' , '>i4'),\
                                 ('EnergySourcePoint' , '>i4'), \
                                 ('cdp' , '>i4'), \
                                ('cdpTrace' , '>i4'), \
                                ('TraceIdentificationCode' , '>u2'), \
                                ('NSummedTraces' , '>u2'), \
                                ('NStackedTraces' , '>u2'), \
                                ('DataUse' , '>u2'),\
                                ('offset' , '>i4'), \
                                ('ReceiverGroupElevation' , '>i4'), \
                                ('SourceSurfaceElevation' , '>i4'), \
                                ('SourceDepth' , '>i4'), \
                                ('ReceiverDatumElevation' , '>i4'), \
                                ('SourceDatumElevation' , '>i4'), \
                                ('SourceWaterDepth' , '>i4'), \
                                ('GroupWaterDepth' , '>i4'),\
                                ('ElevationScalar' , '>i2'), \
                                ('SourceGroupScalar' , '>i2'), \
                                ('SourceX' , '>i4'), \
                                ('SourceY' , '>i4'), \
                                ('GroupX' , '>i4'), \
                                ('GroupY' , '>i4'), \
                                ('CoordinateUnits' , '>u2'),\
                                ('WeatheringVelocity' , '>u2'), \
                                ('SubWeatheringVelocity' , '>u2'), \
                                ('SourceUpholeTime' , '>u2'), \
                                ('GroupUpholeTime' , '>u2'), \
                                ('SourceStaticCorrection' , '>u2'), \
                                ('GroupStaticCorrection' , '>u2'), \
                                ('TotalStaticApplied' , '>u2'), \
                                ('LagTimeA' , '>i2'), \
                                ('LagTimeB' , '>i2'), \
                                ('DelayRecordingTime' , '>i2'), \
                                ('MuteTimeStart' , '>u2'), \
                                ('MuteTimeEND' , '>u2'), \
                                ('ns' , '>u2'), \
                                ('dt' , '>u2'), \
                                ('GainType' , '>u2'), \
                                ('InstrumentGainConstant' , '>u2'), \
                                ('InstrumentInitialGain' , '>u2'), \
                                ('Correlated' , '>u2'), \
                                ('SweepFrequenceStart' , '>u2'), \
                                ('SweepFrequenceEnd' , '>u2'), \
                                ('SweepLength' , '>u2'), \
                                ('SweepType' , '>u2'), \
                                ('SweepTraceTaperLengthStart' , '>u2'), \
                                ('SweepTraceTaperLengthEnd' , '>u2'), \
                                ('TaperType' , '>u2'), \
                                ('AliasFilterFrequency' , '>u2'), \
                                ('AliasFilterSlope' , '>u2'), \
                                ('NotchFilterFrequency' , '>u2'), \
                                ('NotchFilterSlope' , '>u2'), \
                                ('LowCutFrequency' , '>u2'), \
                                ('HighCutFrequency' , '>u2'), \
                                ('LowCutSlope' , '>u2'), \
                                ('HighCutSlope' , '>u2'), \
                                ('YearDataRecorded' , '>u2'), \
                                ('DayOfYear' , '>u2'), \
                                ('HourOfDay' , '>u2'), \
                                ('MinuteOfHour' , '>u2'), \
                                ('SecondOfMinute' , '>u2'), \
                                ('TimeBaseCode' , '>u2'), \
                                ('TraceWeightningFactor' , '>u2'), \
                                ('GeophoneGroupNumberRoll1' , '>u2'), \
                                ('GeophoneGroupNumberFirstTraceOrigField' , '>u2'), \
                                ('GeophoneGroupNumberLastTraceOrigField' , '>u2'), \
                                ('GapSize' , '>u2'), \
                                ('OverTravel' , '>u2'),\
                                ('cdpX' , '>i4'),\
                                ('cdpY' , '>i4'),\
                                ('Inline3D' , '>i4'),\
                                ('Crossline3D' , '>i4'),\
                                ('ShotPoint' , '>i4'),\
                                ('ShotPointScalar' , '>i2'),\
                                ('TraceValueMeasurementUnit' , '>u2'),\
                                ('TransductionConstantMantissa' , '>i4'),\
                                ('TransductionConstantPower' , '>u2'),\
                                ('TransductionUnit' , '>u2'),\
                                ('TraceIdentifier' , '>u2'),\
                                ('ScalarTraceHeader' , '>i2'),\
                                ('SourceType' , '>u2'),\
                                ('SourceEnergyDirectionMantissa' , '>i4'),\
                                ('SourceEnergyDirectionExponent' , '>u2'),\
                                ('SourceMeasurementMantissa' , '>i4'),\
                                ('SourceMeasurementExponent' , '>u2'),\
                                ('SourceMeasurementUnit' , '>u2'),\
                                ('UnassignedInt1' , '>i4'),\
                                ('UnassignedInt2' , '>i4')])






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

##############
# INIT

##############
# %%  Initialize SEGY HEADER
TFH = 'This is a SEG-Y file created by DeepListen software. Visit www.deep-listen.com for more information.'
SH_def = {"Job": {"pos": 3200, "type": "int32", "def": 0}}
SH_def["Line"] = {"pos": 3204, "type": "int32", "def": 0}
SH_def["Reel"] = {"pos": 3208, "type": "int32", "def": 0}
SH_def["DataTracePerEnsemble"] = {"pos": 3212, "type": "int16", "def": 0}
SH_def["AuxiliaryTracePerEnsemble"] = {"pos": 3214, "type": "int16", "def": 0}
SH_def["dt"] = {"pos": 3216, "type": "uint16", "def": 1000}
SH_def["dtOrig"] = {"pos": 3218, "type": "uint16", "def": 1000}
SH_def["ns"] = {"pos": 3220, "type": "uint16", "def": 0}
SH_def["nsOrig"] = {"pos": 3222, "type": "uint16", "def": 0}
SH_def["DataSampleFormat"] = {"pos": 3224, "type": "int16", "def": 5}

SH_def["DataSampleFormat"]["descr"] = {0: {
    1: "IBM Float",
    2: "32 bit Integer",
    3: "16 bit Integer",
    8: "8 bit Integer"}}

SH_def["DataSampleFormat"]["descr"][1] = {
    1: "IBM Float",
    2: "32 bit Integer",
    3: "16 bit Integer",
    4: "32 bit Fixed Point",
    5: "IEEE",
    8: "8 bit Integer"}

SH_def["DataSampleFormat"]["descr"][0] = { # added by Z Zhao
    1: "IBM Float",
    2: "32 bit Integer",
    3: "16 bit Integer",
    4: "32 bit Fixed Point"
    }

SH_def["DataSampleFormat"]["bps"] = {0: {
    1: 4,
    2: 4,
    3: 2,
    4: 4,
    8: 1}}
SH_def["DataSampleFormat"]["bps"][1] = {
    1: 4,
    2: 4,
    3: 2,
    4: 4,
    5: 4,
    8: 1}

SH_def["DataSampleFormat"]["bps"][0] = {  # added by Z Zhao
    1: 4,
    2: 4,
    3: 2,
    4: 4
    }   
SH_def["DataSampleFormat"]["datatype"] = {0: {
    1: 'ibm',
    2: 'l',
    3: 'h',
    8: 'B'}}
SH_def["DataSampleFormat"]["datatype"][1] = {
    1: 'ibm',
    2: 'l',
    3: 'h',
    #    5: 'float',
    5: 'f',
    8: 'B'}

SH_def["EnsembleFold"] = {"pos": 3226, "type": "int16", "def": 0}
SH_def["TraceSorting"] = {"pos": 3228, "type": "int16", "def": 0}
SH_def["VerticalSumCode"] = {"pos": 3230, "type": "int16", "def": 0}
SH_def["SweepFrequencyStart"] = {"pos": 3232, "type": "int16", "def": 0}
SH_def["SweepFrequencyEnd"] = {"pos": 3234, "type": "int16", "def": 0}
SH_def["SweepLength"] = {"pos": 3236, "type": "int16", "def": 0}
SH_def["SweepType"] = {"pos": 3238, "type": "int16", "def": 0}
SH_def["SweepChannel"] = {"pos": 3240, "type": "int16", "def": 0}
SH_def["SweepTaperlengthStart"] = {"pos": 3242, "type": "int16", "def": 0}
SH_def["SweepTaperLengthEnd"] = {"pos": 3244, "type": "int16", "def": 0}
SH_def["TaperType"] = {"pos": 3246, "type": "int16", "def": 0}
SH_def["CorrelatedDataTraces"] = {"pos": 3248, "type": "int16", "def": 0}
SH_def["BinaryGain"] = {"pos": 3250, "type": "int16", "def": 0}
SH_def["AmplitudeRecoveryMethod"] = {"pos": 3252, "type": "int16", "def": 0}
SH_def["MeasurementSystem"] = {"pos": 3254, "type": "int16", "def": 0}
SH_def["ImpulseSignalPolarity"] = {"pos": 3256, "type": "int16", "def": 0}
SH_def["VibratoryPolarityCode"] = {"pos": 3258, "type": "int16", "def": 0}
SH_def["Unassigned1"] = {"pos": 3260, "type": "int16", "n": 120, "def": 0}
SH_def["SegyFormatRevisionNumber"] = {"pos": 3500, "type": "uint16", "def": 100}
SH_def["FixedLengthTraceFlag"] = {"pos": 3502, "type": "uint16", "def": 0}
SH_def["NumberOfExtTextualHeaders"] = {"pos": 3504, "type": "uint16", "def": 0}
SH_def[" "] = {"pos": 3506, "type": "int16", "n": 47, "def": 0}

##############
# %%  Initialize SEGY TRACE HEADER SPECIFICATION
STH_def = {"TraceSequenceLine": {"pos": 0, "type": "int32"}}
STH_def["TraceSequenceFile"] = {"pos": 4, "type": "int32"}
STH_def["FieldRecord"] = {"pos": 8, "type": "int32"}
STH_def["TraceNumber"] = {"pos": 12, "type": "int32"}
STH_def["EnergySourcePoint"] = {"pos": 16, "type": "int32"}
STH_def["cdp"] = {"pos": 20, "type": "int32"}
STH_def["cdpTrace"] = {"pos": 24, "type": "int32"}
STH_def["TraceIdentificationCode"] = {"pos": 28, "type": "uint16"}  # 'int16'); % 28
STH_def["TraceIdentificationCode"]["descr"] = {0: {
    1: "Seismic data",
    2: "Dead",
    3: "Dummy",
    4: "Time Break",
    5: "Uphole",
    6: "Sweep",
    7: "Timing",
    8: "Water Break"}}
STH_def["TraceIdentificationCode"]["descr"][1] = {
    -1: "Other",
    0: "Unknown",
    1: "Seismic data",
    2: "Dead",
    3: "Dummy",
    4: "Time break",
    5: "Uphole",
    6: "Sweep",
    7: "Timing",
    8: "Waterbreak",
    9: "Near-field gun signature",
    10: "Far-field gun signature",
    11: "Seismic pressure sensor",
    12: "Multicomponent seismic sensor - Vertical component",
    13: "Multicomponent seismic sensor - Cross-line component",
    14: "Multicomponent seismic sensor - In-line component",
    15: "Rotated multicomponent seismic sensor - Vertical component",
    16: "Rotated multicomponent seismic sensor - Transverse component",
    17: "Rotated multicomponent seismic sensor - Radial component",
    18: "Vibrator reaction mass",
    19: "Vibrator baseplate",
    20: "Vibrator estimated ground force",
    21: "Vibrator reference",
    22: "Time-velocity pairs"}
STH_def["NSummedTraces"] = {"pos": 30, "type": "int16"}  # 'int16'); % 30
STH_def["NStackedTraces"] = {"pos": 32, "type": "int16"}  # 'int16'); % 32
STH_def["DataUse"] = {"pos": 34, "type": "int16"}  # 'int16'); % 34
STH_def["DataUse"]["descr"] = {0: {
    1: "Production",
    2: "Test"}}
STH_def["DataUse"]["descr"][1] = STH_def["DataUse"]["descr"][0]
STH_def["offset"] = {"pos": 36, "type": "int32"}  # 'int32');             %36
STH_def["ReceiverGroupElevation"] = {"pos": 40, "type": "int32"}  # 'int32');             %40
STH_def["SourceSurfaceElevation"] = {"pos": 44, "type": "int32"}  # 'int32');             %44
STH_def["SourceDepth"] = {"pos": 48, "type": "int32"}  # 'int32');             %48
STH_def["ReceiverDatumElevation"] = {"pos": 52, "type": "int32"}  # 'int32');             %52
STH_def["SourceDatumElevation"] = {"pos": 56, "type": "int32"}  # 'int32');             %56
STH_def["SourceWaterDepth"] = {"pos": 60, "type": "int32"}  # 'int32');  %60
STH_def["GroupWaterDepth"] = {"pos": 64, "type": "int32"}  # 'int32');  %64
STH_def["ElevationScalar"] = {"pos": 68, "type": "int16"}  # 'int16');  %68
STH_def["SourceGroupScalar"] = {"pos": 70, "type": "int16"}  # 'int16');  %70
STH_def["SourceX"] = {"pos": 72, "type": "int32"}  # 'int32');  %72
STH_def["SourceY"] = {"pos": 76, "type": "int32"}  # 'int32');  %76
STH_def["GroupX"] = {"pos": 80, "type": "int32"}  # 'int32');  %80
STH_def["GroupY"] = {"pos": 84, "type": "int32"}  # 'int32');  %84
STH_def["CoordinateUnits"] = {"pos": 88, "type": "int16"}  # 'int16');  %88
STH_def["CoordinateUnits"]["descr"] = {1: {
    1: "Length (meters or feet)",
    2: "Seconds of arc"}}
STH_def["CoordinateUnits"]["descr"][1] = {
    1: "Length (meters or feet)",
    2: "Seconds of arc",
    3: "Decimal degrees",
    4: "Degrees, minutes, seconds (DMS)"}
STH_def["WeatheringVelocity"] = {"pos": 90, "type": "int16"}  # 'int16');  %90
STH_def["SubWeatheringVelocity"] = {"pos": 92, "type": "int16"}  # 'int16');  %92
STH_def["SourceUpholeTime"] = {"pos": 94, "type": "int16"}  # 'int16');  %94
STH_def["GroupUpholeTime"] = {"pos": 96, "type": "int16"}  # 'int16');  %96
STH_def["SourceStaticCorrection"] = {"pos": 98, "type": "int16"}  # 'int16');  %98
STH_def["GroupStaticCorrection"] = {"pos": 100, "type": "int16"}  # 'int16');  %100
STH_def["TotalStaticApplied"] = {"pos": 102, "type": "int16"}  # 'int16');  %102
STH_def["LagTimeA"] = {"pos": 104, "type": "int16"}  # 'int16');  %104
STH_def["LagTimeB"] = {"pos": 106, "type": "int16"}  # 'int16');  %106
STH_def["DelayRecordingTime"] = {"pos": 108, "type": "int16"}  # 'int16');  %108
STH_def["MuteTimeStart"] = {"pos": 110, "type": "int16"}  # 'int16');  %110
STH_def["MuteTimeEND"] = {"pos": 112, "type": "int16"}  # 'int16');  %112
STH_def["ns"] = {"pos": 114, "type": "uint16"}  # 'uint16');  %114
STH_def["dt"] = {"pos": 116, "type": "uint16"}  # 'uint16');  %116
STH_def["GainType"] = {"pos": 119, "type": "int16"}  # 'int16');  %118
STH_def["GainType"]["descr"] = {0: {
    1: "Fixes",
    2: "Binary",
    3: "Floating point"}}
STH_def["GainType"]["descr"][1] = STH_def["GainType"]["descr"][0]
STH_def["InstrumentGainConstant"] = {"pos": 120, "type": "int16"}  # 'int16');  %120
STH_def["InstrumentInitialGain"] = {"pos": 122, "type": "int16"}  # 'int16');  %%122
STH_def["Correlated"] = {"pos": 124, "type": "int16"}  # 'int16');  %124
STH_def["Correlated"]["descr"] = {0: {
    1: "No",
    2: "Yes"}}
STH_def["Correlated"]["descr"][1] = STH_def["Correlated"]["descr"][0]

STH_def["SweepFrequenceStart"] = {"pos": 126, "type": "int16"}  # 'int16');  %126
STH_def["SweepFrequenceEnd"] = {"pos": 128, "type": "int16"}  # 'int16');  %128
STH_def["SweepLength"] = {"pos": 130, "type": "int16"}  # 'int16');  %130
STH_def["SweepType"] = {"pos": 132, "type": "int16"}  # 'int16');  %132
STH_def["SweepType"]["descr"] = {0: {
    1: "linear",
    2: "parabolic",
    3: "exponential",
    4: "other"}}
STH_def["SweepType"]["descr"][1] = STH_def["SweepType"]["descr"][0]

STH_def["SweepTraceTaperLengthStart"] = {"pos": 134, "type": "int16"}  # 'int16');  %134
STH_def["SweepTraceTaperLengthEnd"] = {"pos": 136, "type": "int16"}  # 'int16');  %136
STH_def["TaperType"] = {"pos": 138, "type": "int16"}  # 'int16');  %138
STH_def["TaperType"]["descr"] = {0: {
    1: "linear",
    2: "cos2c",
    3: "other"}}
STH_def["TaperType"]["descr"][1] = STH_def["TaperType"]["descr"][0]

STH_def["AliasFilterFrequency"] = {"pos": 140, "type": "int16"}  # 'int16');  %140
STH_def["AliasFilterSlope"] = {"pos": 142, "type": "int16"}  # 'int16');  %142
STH_def["NotchFilterFrequency"] = {"pos": 144, "type": "int16"}  # 'int16');  %144
STH_def["NotchFilterSlope"] = {"pos": 146, "type": "int16"}  # 'int16');  %146
STH_def["LowCutFrequency"] = {"pos": 148, "type": "int16"}  # 'int16');  %148
STH_def["HighCutFrequency"] = {"pos": 150, "type": "int16"}  # 'int16');  %150
STH_def["LowCutSlope"] = {"pos": 152, "type": "int16"}  # 'int16');  %152
STH_def["HighCutSlope"] = {"pos": 154, "type": "int16"}  # 'int16');  %154
STH_def["YearDataRecorded"] = {"pos": 156, "type": "int16"}  # 'int16');  %156
STH_def["DayOfYear"] = {"pos": 158, "type": "int16"}  # 'int16');  %158
STH_def["HourOfDay"] = {"pos": 160, "type": "int16"}  # 'int16');  %160
STH_def["MinuteOfHour"] = {"pos": 162, "type": "int16"}  # 'int16');  %162
STH_def["SecondOfMinute"] = {"pos": 164, "type": "int16"}  # 'int16');  %164
STH_def["TimeBaseCode"] = {"pos": 166, "type": "int16"}  # 'int16');  %166
STH_def["TimeBaseCode"]["descr"] = {0: {
    1: "Local",
    2: "GMT",
    3: "Other"}}
STH_def["TimeBaseCode"]["descr"][1] = {
    1: "Local",
    2: "GMT",
    3: "Other",
    4: "UTC"}
STH_def["TraceWeightningFactor"] = {"pos": 168, "type": "int16"}  # 'int16');  %170
STH_def["GeophoneGroupNumberRoll1"] = {"pos": 170, "type": "int16"}  # 'int16');  %172
STH_def["GeophoneGroupNumberFirstTraceOrigField"] = {"pos": 172, "type": "int16"}  # 'int16');  %174
STH_def["GeophoneGroupNumberLastTraceOrigField"] = {"pos": 174, "type": "int16"}  # 'int16');  %176
STH_def["GapSize"] = {"pos": 176, "type": "int16"}  # 'int16');  %178
STH_def["OverTravel"] = {"pos": 178, "type": "int16"}  # 'int16');  %178
STH_def["OverTravel"]["descr"] = {0: {
    1: "down (or behind)",
    2: "up (or ahead)",
    3: "other"}}
STH_def["OverTravel"]["descr"][1] = STH_def["OverTravel"]["descr"][0]

STH_def["cdpX"] = {"pos": 180, "type": "int32"}  # 'int32');  %180
STH_def["cdpY"] = {"pos": 184, "type": "int32"}  # 'int32');  %184
STH_def["Inline3D"] = {"pos": 188, "type": "int32"}  # 'int32');  %188
STH_def["Crossline3D"] = {"pos": 192, "type": "int32"}  # 'int32');  %192
STH_def["ShotPoint"] = {"pos": 192, "type": "int32"}  # 'int32');  %196
STH_def["ShotPointScalar"] = {"pos": 200, "type": "int16"}  # 'int16');  %200
STH_def["TraceValueMeasurementUnit"] = {"pos": 202, "type": "int16"}  # 'int16');  %202
STH_def["TraceValueMeasurementUnit"]["descr"] = {1: {
    -1: "Other",
    0: "Unknown (should be described in Data Sample Measurement Units Stanza) ",
    1: "Pascal (Pa)",
    2: "Volts (V)",
    3: "Millivolts (v)",
    4: "Amperes (A)",
    5: "Meters (m)",
    6: "Meters Per Second (m/s)",
    7: "Meters Per Second squared (m/&s2)Other",
    8: "Newton (N)",
    9: "Watt (W)"}}
STH_def["TransductionConstantMantissa"] = {"pos": 204, "type": "int32"}  # 'int32');  %204
STH_def["TransductionConstantPower"] = {"pos": 208, "type": "int16"}  # 'int16'); %208
STH_def["TransductionUnit"] = {"pos": 210, "type": "int16"}  # 'int16');  %210
STH_def["TransductionUnit"]["descr"] = STH_def["TraceValueMeasurementUnit"]["descr"]
STH_def["TraceIdentifier"] = {"pos": 212, "type": "int16"}  # 'int16');  %212
STH_def["ScalarTraceHeader"] = {"pos": 214, "type": "int16"}  # 'int16');  %214
STH_def["SourceType"] = {"pos": 216, "type": "int16"}  # 'int16');  %216
STH_def["SourceType"]["descr"] = {1: {
    -1: "Other (should be described in Source Type/Orientation stanza)",
    0: "Unknown",
    1: "Vibratory - Vertical orientation",
    2: "Vibratory - Cross-line orientation",
    3: "Vibratory - In-line orientation",
    4: "Impulsive - Vertical orientation",
    5: "Impulsive - Cross-line orientation",
    6: "Impulsive - In-line orientation",
    7: "Distributed Impulsive - Vertical orientation",
    8: "Distributed Impulsive - Cross-line orientation",
    9: "Distributed Impulsive - In-line orientation"}}

STH_def["SourceEnergyDirectionMantissa"] = {"pos": 218, "type": "int32"}  # 'int32');  %218
STH_def["SourceEnergyDirectionExponent"] = {"pos": 222, "type": "int16"}  # 'int16');  %222
STH_def["SourceMeasurementMantissa"] = {"pos": 224, "type": "int32"}  # 'int32');  %224
STH_def["SourceMeasurementExponent"] = {"pos": 228, "type": "int16"}  # 'int16');  %228
STH_def["SourceMeasurementUnit"] = {"pos": 230, "type": "int16"}  # 'int16');  %230
STH_def["SourceMeasurementUnit"]["descr"] = {1: {
    -1: "Other (should be described in Source Measurement Unit stanza)",
    0: "Unknown",
    1: "Joule (J)",
    2: "Kilowatt (kW)",
    3: "Pascal (Pa)",
    4: "Bar (Bar)",
    4: "Bar-meter (Bar-m)",
    5: "Newton (N)",
    6: "Kilograms (kg)"}}
STH_def["UnassignedInt1"] = {"pos": 232, "type": "int32"}  # 'int32');  %232
STH_def["UnassignedInt2"] = {"pos": 236, "type": "int32"}  # 'int32');  %236



##############
def getDefaultSegyHeader(ntraces=100, ns=100, dt = 1000):
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """
    # INITIALIZE DICTIONARY   
    SH = {"Job": {"pos": 3200, "type": "int32", "def": 0}}

    for key in SH_def.keys():

        tmpkey = SH_def[key]
        if ('def' in tmpkey):
            val = tmpkey['def']
        else:
            val = 0
        SH[key] = val

    SH["ntraces"] = ntraces
    SH["ns"] = ns
    SH["dt"] = dt

    return SH


# %%
def getDefaultSegyTraceHeaders(ntraces=100, ns=100, dt=1000):
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """
    # INITIALIZE DICTIONARY
    STH = {"TraceSequenceLine": {"pos": 0, "type": "int32"}}

    for key in STH_def.keys():

        tmpkey = STH_def[key]
        if ('def' in tmpkey):
            val = tmpkey['def']
        else:
            val = 0
        STH[key] = np.zeros(ntraces)

    for a in range(ntraces):
        STH["TraceSequenceLine"][a] = a + 1
        STH["TraceSequenceFile"][a] = a + 1
        STH["FieldRecord"][a] = 1000
        STH["TraceNumber"][a] = a + 1
        STH["ns"][a] = ns
        STH["dt"][a] = dt
    return STH


# %%
def getSegyTraceHeader(SH, THN='cdp', data='none', endian='>'):  
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """

    bps = getBytePerSample(SH)

    if (data == 'none'):
        data = open(SH["filename"], 'rb').read()

    # MAKE SOME LOOKUP TABLE THAT HOLDS THE LOCATION OF HEADERS
    #    THpos=TraceHeaderPos[THN]
    THpos = STH_def[THN]["pos"]
    THformat = STH_def[THN]["type"]
    ntraces = int(SH["ntraces"])
    thv = np.zeros(ntraces)
    for itrace in range(1, ntraces + 1, 1):
        i = itrace
        pos = THpos + 3600 + (SH["ns"] * bps + 240) * (itrace - 1)

       

        thv[itrace - 1], index = getValue(data, pos, THformat, endian, 1)
      
        

    return thv


# %%
def getLastSegyTraceHeader(SH, THN='cdp', data='none', endian='>'): 
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """

    bps = getBytePerSample(SH)

    if (data == 'none'):
        data = open(SH["filename"]).read()

    # SET PARAMETERS THAT DEFINE THE LOCATION OF THE LAST HEADER
    # AND THE TRACE NUMBER KEY FIELD
    THpos = STH_def[THN]["pos"]
    THformat = STH_def[THN]["type"]
    ntraces = SH["ntraces"]

    pos = THpos + 3600 + (SH["ns"] * bps + 240) * (ntraces - 1);

    txt = "getLastSegyTraceHeader : Reading last trace header " + THN + " " + str(pos)

   
    thv, index = getValue(data, pos, THformat, endian, 1)
    txt = "getLastSegyTraceHeader : " + THN + "=" + str(thv)
    

    return thv


# %%
def getAllSegyTraceHeaders(SH, data='none'):

    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """

    SegyTraceHeaders = {'filename': SH["filename"]}

    
    
    if (data == 'none'):
        data = open(SH["filename"], 'rb').read()

    for key in STH_def.keys():
        sth = getSegyTraceHeader(SH, key, data)
        SegyTraceHeaders[key] = sth
        txt = "getAllSegyTraceHeaders :  " + key
        

    return SegyTraceHeaders


# %%
def readSegy(filename, endian='>', rev = None, dsf = None):  
    """
    Data,SegyHeader,SegyTraceHeaders=getSegyHeader(filename)

    Function codes modified from https://github.com/cultpenguin/segypy

    """

    Data = None
    SH = None
    SegyTraceHeaders = None

   
    fs = open(filename, 'rb')
    data = fs.read()

    filesize = len(data)

    SH = getSegyHeader(filename, endian, rev, dsf)  

    bps = getBytePerSample(SH)

    ntraces = (filesize - 3600) / (SH['ns'] * bps + 240)
   

   
    SH["ntraces"] = int(ntraces)

    ndummy_samples=240/bps  
   
    # GET TRACE
    index = 3600
    nd = int((filesize - 3600) / bps)



    Data, SH, SegyTraceHeaders = loadSegyData(fs, SH, bps, endian)

   

    return Data, SH, SegyTraceHeaders




def make_dtype(data_sample_format): 

    """
    Convert a SEG Y data sample format to a compatible numpy dtype.

    Note :

        IBM float data sample formats ('ibm') will correspond to IEEE float data types.

    Args:

        data_sample_format: A data sample format string.

    Returns:

        A numpy.dtype instance.


    Raises:

        ValueError: For unrecognised data sample format strings.

    """

    try:

        return NUMPY_DTYPES[data_sample_format]

    except KeyError:

        raise ValueError("Unknown data sample format string {!r}".format(data_sample_format))

def parseDataBuffer(fs, dsf = 'float32', endian = '>'):

    fs.seek(0)

    TRACES_TRACE_TYPE =  NUMPY_DTYPES[dsf]
    
    TRACES_TRACE_TYPE.newbyteorder(endian)
    TRACES_HEADER_TYPE.newbyteorder(endian)

    TRACES_HEADER_BYTES = TRACES_HEADER_TYPE.itemsize
    TRACES_TRACE_BYTES = TRACES_TRACE_TYPE.itemsize
    
    headers=[]
    traces=[]
    nt=0
    ns = 0
    # first we need to jump over the headers:
    fs.seek(SEGY_ASCII_REEL_HEADER_BYTES+SEGY_BIN_REEL_HEADER_BYTES)

    while True:
        l=fs.read(TRACES_HEADER_BYTES)
        if len(l) == TRACES_HEADER_BYTES:
            rec=np.frombuffer(l, TRACES_HEADER_TYPE)
            ns=rec['ns'][0]
            #print(ns)
            trcstr=fs.read(ns *TRACES_TRACE_BYTES )
            headers.append(rec)
            traces.append(np.frombuffer( trcstr, TRACES_TRACE_TYPE ))
            nt+=1
        else:
            break
    #print("%s record read."%nt)

    

    headers=np.stack(headers).reshape(-1)
    traces=np.stack(traces, axis = 1)

    if dsf == 'int8':
    
        for i in range(ns):
            for j in range(nt):
                if traces[i][j] > 128:
                    traces[i][j] = traces[i][j] - 256

    return traces, headers


def loadSegyData(data, SH, bps, endian='>'):  # added by A Squelch
    """
    Function codes modified from https://github.com/cultpenguin/segypy
    
    This function separated out from readSegy so that it can also be
    called from other external functions.

    """

    # Calulate number of dummy samples needed to account for Trace Headers
    ndummy_samples = int(240 / bps)
   

    # READ ALL DATA EXCEPT FOR SEGY HEADER
    

    revision = SH["SegyFormatRevisionNumber"]
    if (revision == 100):
        revision = 1
    if (revision == 256):  
        revision = 1

    dsf = SH["DataSampleFormat"]


    DataDescr = SH_def["DataSampleFormat"]["descr"][revision][dsf]
    

    if (SH["DataSampleFormat"] == 1):        
        Data, HD = parseDataBuffer(data, 'ibm', endian)
    elif (SH["DataSampleFormat"] == 2):
        Data, HD = parseDataBuffer(data, 'int32', endian)
    elif (SH["DataSampleFormat"] == 3):
        Data, HD = parseDataBuffer(data, 'int16', endian)
    elif (SH["DataSampleFormat"] == 5):
        Data, HD = parseDataBuffer(data, 'float32', endian)
    elif (SH["DataSampleFormat"] == 8):
        Data, HD = parseDataBuffer(data, 'int8', endian)
    else:
        print("loadSegyData : DSF=" + str(SH["DataSampleFormat"]) + ", NOT SUPORTED", 2)

    STH = {}
    for key in TRACES_HEADER_TYPE.names:       

        STH[key] = HD[key]

    return Data, SH, STH


# %%
def readSegyData(data, SH, nd, bps, index, endian='>'):  
    """
   
    Function codes modified from https://github.com/cultpenguin/segypy


    """

    # Calulate number of dummy samples needed to account for Trace Headers
    ndummy_samples = int(240 / bps)
    
    # READ ALL SEGY TRACE HEADRES
    STH = getAllSegyTraceHeaders(SH, data)

    

    # READ ALL DATA EXCEPT FOR SEGY HEADER
    # Data = np.zeros((SH['ns'],ntraces))

    revision = SH["SegyFormatRevisionNumber"]
    if (revision == 100):
        revision = 1
    if (revision == 256):  # added by A Squelch
        revision = 1

    dsf = SH["DataSampleFormat"]


    DataDescr = SH_def["DataSampleFormat"]["descr"][revision][dsf]
    

    if (SH["DataSampleFormat"] == 1):
        
        Data1 = getValue(data, index, 'ibm', endian, nd)
    elif (SH["DataSampleFormat"] == 2):
        Data1 = getValue(data, index, 'l', endian, nd)
    elif (SH["DataSampleFormat"] == 3):
        Data1 = getValue(data, index, 'h', endian, nd)
    elif (SH["DataSampleFormat"] == 5):
        Data1 = getValue(data, index, 'float', endian, nd)
    elif (SH["DataSampleFormat"] == 8):
        Data1 = getValue(data, index, 'B', endian, nd)
    else:
        print("readSegyData : DSF=" + str(SH["DataSampleFormat"]) + ", NOT SUPORTED", 2)

    Data = Data1[0]

    
    Data = np.reshape(np.array(Data), (SH['ntraces'], SH['ns'] + ndummy_samples))
    

    
    Data = Data[:, ndummy_samples:(SH['ns'] + ndummy_samples)]
    
    Data = np.transpose(Data)

    # SOMEONE NEEDS TO IMPLEMENT A NICER WAY DO DEAL WITH DSF=8
    if (SH["DataSampleFormat"] == 8):
        for i in np.arange(SH['ntraces']):
            for j in np.arange(SH['ns']):
                if Data[i][j] > 128:
                    Data[i][j] = Data[i][j] - 256

   

    return Data, SH, STH


# %%
def getSegyTrace(SH, itrace, endian='>'):  
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """
    data = open(SH["filename"], 'rb').read()

    bps = getBytePerSample(SH)

    # GET TRACE HEADER
    index = 3200 + (itrace - 1) * (240 + SH['ns'] * bps)
    SegyTraceHeader = []
    

    # GET TRACE
    index = 3200 + (itrace - 1) * (240 + SH['ns'] * bps) + 240
    SegyTraceData = getValue(data, index, 'float', endian, SH['ns'])
    return SegyTraceHeader, SegyTraceData


# %%
def getSegyHeader(filename, endian='>', rev = None, dsf = None):  
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """

    data = open(filename, 'rb').read()

    SegyHeader = {'filename': filename}

    if rev != None:
        SegyHeader["SegyFormatRevisionNumber"] = rev
    

    j = 0
    for key in SH_def.keys():
        j = j + 1
        pos = SH_def[key]["pos"]
        format = SH_def[key]["type"]

        txt = "i=%3d, pos=%5d, format=%2s, key=%s" % (j, pos, format, key)


        SegyHeader[key], index = getValue(data, pos, format, endian)

        txt = "SegyHeader[%s] = %f" % (key, SegyHeader[key])
       

    if dsf != None:
        SegyHeader["DataSampleFormat"] = dsf    
    # SET NUMBER OF BYTES PER DATA SAMPLE
    bps = getBytePerSample(SegyHeader)

    filesize = len(data)
    ntraces = (filesize - 3600) / (SegyHeader['ns'] * bps + 240)
    SegyHeader["ntraces"] = ntraces
    SegyHeader["time"]=np.arange(SegyHeader['ns']) * SegyHeader['dt'] / 1e+6


   

    return SegyHeader


# %%
def writeSegy(filename, Data, dt=1000, STHin={}, SHin={}):
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """

    N = Data.shape
    ns = N[0]
    ntraces = N[1]
    
    if not len(SHin):
        SH = getDefaultSegyHeader(ntraces, ns, dt)
    else:
        SH = SHin
    if not len(STHin):
        STH = getDefaultSegyTraceHeaders(ntraces, ns, dt)
    else:    
        STH = STHin 
 

    writeSegyStructure(filename, Data, SH, STH)


# %%
def writeSegyStructure(filename, Data, SH, STH, endian='>'):  
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """

    

    f = open(filename, 'wb')

    # VERBOSE INF
    revision = SH["SegyFormatRevisionNumber"]
    dsf = SH["DataSampleFormat"]
    if (revision == 100):
        revision = 1
    if (revision == 256):  
        revision = 1

   
    # WRITE SEGY HEADER

    for key in SH_def.keys():
        pos = SH_def[key]["pos"]
        format = SH_def[key]["type"]
        value = SH[key]

        
        putValue(value, f, pos, format, endian)

        txt = str(pos) + " " + str(format) + "  Reading " + key + "=" + str(value)
   

    # SEGY TRACES

    ctype = SH_def['DataSampleFormat']['datatype'][revision][dsf]
    bps = SH_def['DataSampleFormat']['bps'][revision][dsf]

    sizeT = 240 + SH['ns'] * bps

    for itrace in range(SH['ntraces']):
        index = 3600 + itrace * sizeT
    
        # WRITE SEGY TRACE HEADER
        for key in STH_def.keys():
            pos = index + STH_def[key]["pos"]
            format = STH_def[key]["type"]
            value = STH[key][itrace]
            txt = str(pos) + " " + str(format) + "  Writing " + key + "=" + str(value)

            
            putValue(value, f, pos, format, endian)

            # Write Data
        cformat = endian + ctype
        for s in range(SH['ns']):
            strVal = struct.pack(cformat, Data[s, itrace])
            f.seek(index + 240 + s * struct.calcsize(cformat))
            f.write(strVal)

    f.close

   

def convert2Segy(filename, Data, SH, STH, endian='>'):  

    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """

   
    f = open(filename, 'wb')

    # VERBOSE INF
    revision = SH["SegyFormatRevisionNumber"]
    dsf = SH["DataSampleFormat"]
    if (revision == 100):
        revision = 1
    if (revision == 256):  # added by A Squelch
        revision = 1

   

    # WRITE SEGY Texual File HEADER (3200 bytes)
    # f.seek(0)
    # import ebcdic
    # f.write(TFH.encode('cp1141'))

    # WRITE SEGY HEADER

    for key in SH_def.keys():
        pos = SH_def[key]["pos"]
        format = SH_def[key]["type"]
        value = SH[key]

        
        putValue(value, f, pos, format, endian)

        txt = str(pos) + " " + str(format) + "  Reading " + key + "=" + str(value)
    

    # SEGY TRACES

    ctype = SH_def['DataSampleFormat']['datatype'][revision][dsf]
    bps = SH_def['DataSampleFormat']['bps'][revision][dsf]

    sizeT = 240 + SH['ns'] * bps

    for itrace in range(SH['ntraces']):
        index = 3600 + itrace * sizeT
        
        # WRITE SEGY TRACE HEADER
        for key in STH_def.keys():
            pos = index + STH_def[key]["pos"]
            format = STH_def[key]["type"]
            value = STH[key][itrace]
            txt = str(pos) + " " + str(format) + "  Writing " + key + "=" + str(value)

            
            putValue(value, f, pos, format, endian)

        # Write Data
        cformat = endian + ctype
        for s in range(SH['ns']):
            strVal = struct.pack(cformat, Data[s, itrace])
            f.seek(index + 240 + s * struct.calcsize(cformat))
            f.write(strVal)

    f.close

def mergeSegy(filename, filelist):

    for i, path in enumerate(filelist):
        
        if os.path.isfile(path):
            
            Data,SegyHeader,SegyTraceHeaders = readSegy(path)

  
            if i == 0:

                ss1 = Data.shape
                D = Data
                SH = SegyHeader
                STH = SegyTraceHeaders

            else:

                ss = Data.shape

                if ss != ss1:

                    print("Error: data size of " + str(i) + " differ from " + str(i-1) + "!\n" + path + " was skipped in this merging process.")

                else:

                    j = len(SegyTraceHeaders['TraceNumber']) * i
                    STH['TraceNumber'] = np.append(STH['TraceNumber'], [j+1, j+2, j+3])
                    for key in STH.keys():  
                        if key != 'TraceNumber':    
                            STH[key] = np.append(STH[key], SegyTraceHeaders[key])                        
                    
                    D = np.append(D,Data, axis = 1)  

           
    SH['ntraces'] = len(STH['TraceNumber'])
    writeSegyStructure(filename, D, SH, STH) 
        



# %%
def putValue(value, fileid, index, ctype='l', endian='>', number=1):
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """
    if (ctype == 'l') | (ctype == 'long') | (ctype == 'int32'):
        size = l_long
        ctype = 'l'
        value=int(value)
    elif (ctype == 'L') | (ctype == 'ulong') | (ctype == 'uint32'):
        size = l_ulong
        ctype = 'L'
        value=int(value)
    elif (ctype == 'h') | (ctype == 'short') | (ctype == 'int16'):
        size = l_short
        ctype = 'h'
        value=int(value)
    elif (ctype == 'H') | (ctype == 'ushort') | (ctype == 'uint16'):
        size = l_ushort
        ctype = 'H'
        value=int(value)
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
    else:
        printverbose('Bad Ctype : ' + ctype, -1)

    cformat = endian + ctype * number

    
    strVal = struct.pack(cformat, value)
    fileid.seek(index)
    fileid.write(strVal)

    return 1


# %%
def getValue(data, index, ctype='l', endian='>', number=1):
    """
    Function codes modified from https://github.com/cultpenguin/segypy

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
        printverbose('Bad Ctype : ' + ctype, -1)

    index_end = index + size * number

    
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

       

        Value = struct.unpack(cformat, data[index:index_end])

    if (ctype == 'B'):
        

        vtxt = 'getValue : ' + 'start=' + str(index) + ' size=' + str(size) + ' number=' + str(
            number) + ' Value=' + str(Value) + ' cformat=' + str(cformat)
        
    if number == 1:
        return Value[0], index_end
    else:
        return Value, index_end






##############
# MISC FUNCTIONS
def ibm2Ieee(ibm_float):
    """
    ibm2Ieee(ibm_float)
    Used by permission
    (C) Secchi Angelo
    with thanks to Howard Lightstone and Anton Vredegoor. 
    """
    """    
    I = struct.unpack('>I',ibm_float)[0]
    sign = [1,-1][bool(i & 0x100000000L)]
    characteristic = ((i >> 24) & 0x7f) - 64
    fraction = (i & 0xffffff)/float(0x1000000L)
    return sign*16**characteristic*fraction
    """


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


def getBytePerSample(SH):
    """
    Function codes modified from https://github.com/cultpenguin/segypy

    """


    revision = SH["SegyFormatRevisionNumber"]
    
    if (revision == 100):
        revision = 1
    if (revision == 256):  
        revision = 1


    dsf = SH["DataSampleFormat"]

    bps = SH_def["DataSampleFormat"]["bps"][revision][dsf]
    
   

    return bps


def parse_trace_headers(segyfile, n_traces):
    '''
    Parse the segy file trace headers into a pandas dataframe.
    Column names are defined from segyio internal tracefield
    One row per trace
    '''

    import segyio

    # Get all header keys
    headers = segyio.tracefield.keys
    # Initialize dataframe with trace id as index and headers as columns
    df = pd.DataFrame(index=range(1, n_traces + 1),
                      columns=headers.keys(), dtype = float)
    # Fill dataframe with all header values
    for k, v in headers.items():
        df[k] = segyfile.attributes(v)[:]
    return df

def parse_binary_header(segyfile, segyio_list, pssegy_list):
    '''
    Parse the segy file trace headers into a pandas dataframe.
    Column names are defined from segyio internal tracefield
    One row per trace
    '''

    import segyio
    
    bin_header = segyfile.bin
    n_traces = segyfile.tracecount

    dic = {}
    dic["ntraces"] = n_traces
    
    for k, v in bin_header.items():
        key = str(k) 
        if key in segyio_list:
            ind = segyio_list.index(key)
            kk = pssegy_list[ind]       
            dic[kk] = v

        else:

            dic[key] = v

    
    
    return dic

def parse_text_header(segyfile):
    '''
    Format segy text header into a readable, clean dict
    '''
    import segyio
    
    raw_header = segyio.tools.wrap(segyfile.text[0])
    # Cut on C*int pattern
    cut_header = re.split(r'C ', raw_header)[1::]
    # Remove end of line return
    text_header = [x.replace('\n', ' ') for x in cut_header]

    clean_header = {}

    if len(text_header):
        text_header[-1] = text_header[-1][:-2]
        # Format in dict
        
        i = 1
        for item in text_header:
            key = "C" + str(i).rjust(2, '0')
            i += 1
            clean_header[key] = item

    return clean_header

    


##############
# segy class

class Segy:
    
    """
    A class contains the volume header, trace header and trace data.
    Various methods are designed to read and write a SEG-Y file and manipulate the trace data.

            
    """  
    def __init__(self, data, vheader, theader):

        self.traceData = data
        self.volumeHeader =  vheader
        self.traceHeader =  theader
        self.zTraces = None
        self.xTraces = None
        self.yTraces = None

        self.stats = {}

        self.df = None # unit is Hz
        self.dt = None # unit is second

        self.ns = None
        self.ntr = None

        #self.fileName = fileName 

        self.componentFlag = int(3) # default is 1C
        self.traceOrder = 'ZEN-ZEN-ZEN'

        #plot
        self.ax = None
        
        self._setStats()
        self._setComponentData()

    @classmethod
    def fromSegyFile(cls, filename):

        """
        Return a Segy class by reading a SEG-Y file with .sgy as its suffix.

        :param filename: absulute file path of the SEG-Y file to be loaded.
        :type filename: str.
                
        :returns: a Segy class
        :rtype: class
            
        """  
        filename = transform_separator(filename)

        traceData, volumeHeader, traceHeader =  readSegy(filename, endian = '>', rev = None, dsf = None)

        
        return cls(traceData, volumeHeader, traceHeader)

    @classmethod
    def fromDictFile(cls, filename):

        """
        Return a Segy class by reading a dict file with .mic as its suffix.

        :param filename: absulute file path of the dict file to be loaded.
        :type filename: str.
                
        :returns: a Segy class
        :rtype: class
            
        """  
        filename = transform_separator(filename)

        dic = load_dict(filename)

        traceData = dic['data']
        volumeHeader = dic['vh']
        traceHeader = dic['th']
                
        return cls(traceData, volumeHeader, traceHeader)

    def toDictFile(self, filename):

        """
        Write the SEG-Y data contained in Segy class to a Python dict file with .mic as its suffix.

        :param filename: absulute file path of the dict file to be written down.
        :type filename: str.
                
                    
        """  
        filename = transform_separator(filename)
        
        dic = {"data": self.traceData,
                "vh": self.volumeHeader,
                "th": self.traceHeader
                }


        import _pickle as pickle

        with open(filename, 'wb') as f:
            pickle.dump(dic, f)

    def toSegyFile_(self, filename,  endian='>'):  
        
        """
        Deprecated.

        Write the SEG-Y data contained in Segy class to a standard Rev1 SEG-Y file with .sgy as its suffix.

        :param filename: absulute file path of the dict file to be written down.
        :type filename: str.
        :param filename: endian setting for the file to be written down, with little endian as '<' and big endian as '>'.
        :type filename: str.

        """  

        Data = self.traceData
        
        SH = self.volumeHeader
        STH = self.traceHeader

        f = open(filename, 'wb')

        # VERBOSE INF
        revision = SH["SegyFormatRevisionNumber"]
        dsf = SH["DataSampleFormat"]
        revision = 1



    

        # WRITE SEGY Texual File HEADER (3200 bytes)
        f.seek(0)
        
        f.write(TFH.encode('cp1141'))

        # WRITE SEGY HEADER

        for key in SH_def.keys():
            pos = SH_def[key]["pos"]
            format = SH_def[key]["type"]
            value = SH[key]

            #        SegyHeader[key],index = putValue(value,f,pos,format,endian);
            putValue(value, f, pos, format, endian)

            txt = str(pos) + " " + str(format) + "  Reading " + key + "=" + str(value)
        

        # SEGY TRACES

        ctype = SH_def['DataSampleFormat']['datatype'][revision][dsf]
        bps = SH_def['DataSampleFormat']['bps'][revision][dsf]

        sizeT = 240 + SH['ns'] * bps

        for itrace in range(SH['ntraces']):
            index = 3600 + itrace * sizeT
            #printverbose('Writing Trace #' + str(itrace + 1) + '/' + str(SH['ntraces']), 10)
            # WRITE SEGY TRACE HEADER
            for key in STH_def.keys():
                
                pos = index + STH_def[key]["pos"]
                format = STH_def[key]["type"]             
    
                value = STH[key][itrace,0]
                # txt = str(pos) + " " + str(format) + "  Writing " + key + "=" + str(value)
                # print(txt)
                putValue(value, f, pos, format, endian)

                # Write Data
            cformat = endian + ctype
            print('cformat: ' + cformat)
            for s in range(SH['ns']):
                print(s)
                strVal = struct.pack(cformat, Data[s, itrace])
                print(strVal)
                f.seek(index + 240 + s * struct.calcsize(cformat))
                f.write(strVal)

        f.close()

    
    def toSegyFile(self, filename,  endian='>'):  
        
        """
        
        Write the SEG-Y data contained in Segy class to a standard Rev1 SEG-Y file with .sgy as its suffix.

        :param filename: absulute file path of the dict file to be written down.
        :type filename: str.
        :param filename: endian setting for the file to be written down, with little endian as '<' and big endian as '>'.
        :type filename: str.

        """  

        Data = self.traceData
        SH = self.volumeHeader
        STH = self.traceHeader

        f = open(filename, 'wb')

       
        # revision = SH["SegyFormatRevisionNumber"]
        
        revision = 1
        dsf = 5
        # if (revision == 100):
        #     revision = 1
        # if (revision == 256):  # added by A Squelch
        #     revision = 1

        

    

        # WRITE SEGY Texual File HEADER (3200 bytes)
        f.seek(0)
        # import ebcdic
        # f.write(TFH.encode('cp1141'))

        # WRITE SEGY HEADER

        for key in SH_def.keys():
            pos = SH_def[key]["pos"]
            format = SH_def[key]["type"]
            value = SH[key]

            #        SegyHeader[key],index = putValue(value,f,pos,format,endian);
            putValue(value, f, pos, format, endian)

            txt = str(pos) + " " + str(format) + "  Reading " + key + "=" + str(value)
        

        # SEGY TRACES

        ctype = SH_def['DataSampleFormat']['datatype'][revision][dsf]
        bps = SH_def['DataSampleFormat']['bps'][revision][dsf]

        sizeT = 240 + SH['ns'] * bps

        for itrace in range(SH['ntraces']):
            index = 3600 + itrace * sizeT
            #printverbose('Writing Trace #' + str(itrace + 1) + '/' + str(SH['ntraces']), 10)
            # WRITE SEGY TRACE HEADER
            for key in STH_def.keys():
                pos = index + STH_def[key]["pos"]
                format = STH_def[key]["type"]
                value = STH[key][itrace]
                txt = str(pos) + " " + str(format) + "  Writing " + key + "=" + str(value)

                #printverbose(txt, 40)
                putValue(value, f, pos, format, endian)

            # Write Data
            
            # method 1: using numpy tobytes, high speed
            cformat = endian + ctype * SH['ns']
            arr = Data[:, itrace].tolist()
            #arr_bytes = arr.tobytes('C')
            strVal = struct.pack(cformat, *arr)
            f.seek(index + 240)
            f.write(strVal)
            
            # # method 2: using struct.pack for each sample point, low speed      
            # cformat = endian + ctype               
            # for s in range(SH['ns']):
            #     strVal = struct.pack(cformat, Data[s, itrace])
            #     f.seek(index + 240 + s * struct.calcsize(cformat))
            #     f.write(strVal)

        f.close()

    def setTraceData(self, data):

        """
        Set the trace data of this Segy class.

        :param data: trace data.
        :type data: numpy ndarray.
        

        """  

        self.traceData = data

    def setVolumeHeader(self, vheader):

        """
        Set the 400 bytes volume header this Segy class.

        :param vheader: a Python dict containing 400 bytes volume header information.
        :type vheader: dict.
        

        """  

        self.volumeHeader = vheader

    def setTraceHeader(self, theader):

        """
        Set the 240 bytes trace header this Segy class.

        :param theader: a Python dict containing 240 bytes trace header information.
        :type theader: dict.
        

        """  
        self.traceHeader = theader

    def _setStats(self):
    
        self._setSampleRate(self.volumeHeader)
        self._setComponentFlag(self.traceHeader)
        self._setDateTime(self.traceHeader)
        self._setSampleNumber(self.volumeHeader)
        self._setTraceNumber(self.volumeHeader)

    def _setDateTime(self, th):

        
        tbc = int(th['TimeBaseCode'][0])

        if tbc == 1:
            self.stats['tzone'] = 'Local'

        elif tbc == 2:
            self.stats['tzone'] = 'GMT'

        elif tbc == 3:
            self.stats['tzone'] = 'Other'

        elif tbc == 4:
            self.stats['tzone'] = 'UTC'
        
        else:
            self.stats['tzone'] = 'GMT'

        
        year = int(th['YearDataRecorded'][0])

        if year == 0:
            year = 1        

        delta_day = int(th['DayOfYear'][0])

        if delta_day == 0:
            delta_day = 1

        hour = int(th['HourOfDay'][0])
        minute = int(th['MinuteOfHour'][0])
        second = int(th['SecondOfMinute'][0])

               
        self.stats['ymd'] = datetime.date(year,1,1) + datetime.timedelta(delta_day - 1)
        self.stats['hms'] = datetime.time(hour,minute,second)

        self.stats['ymdhms'] = datetime.datetime(self.stats['ymd'].year, self.stats['ymd'].month, self.stats['ymd'].day,
                                                    self.stats['hms'].hour, self.stats['hms'].minute, self.stats['hms'].second)

        

        
    def _setComponentData(self):

        ntr = self.stats['ntr']
        ns = self.stats['ns']

        if self.componentFlag == 3:

            self.stats['com'] = 3
        
            if self.traceHeader['TraceIdentificationCode'][0] == 12.0 and (self.traceHeader['TraceIdentificationCode'][1] == 13.0 or self.traceHeader['TraceIdentificationCode'][1] == 14.0): 
                self.zTraces = self.traceData[:,0:ntr:3] # indexing from first element to last element with increment(skipt) 3 
                self.xTraces = self.traceData[:,1:ntr:3] 
                self.yTraces = self.traceData[:,2:ntr:3]
                self.traceOrder = 'ZEN-ZEN-ZEN'
                self.stats['order'] = 'ZEN-ZEN-ZEN'
            
            elif self.traceHeader['TraceIdentificationCode'][2] == 12.0 and (self.traceHeader['TraceIdentificationCode'][0] == 13.0 or self.traceHeader['TraceIdentificationCode'][0] == 14.0):
                self.xTraces = self.traceData[:,0:ntr:3] # indexing from first element to last element with increment(skipt) 3 
                self.yTraces = self.traceData[:,1:ntr:3] 
                self.zTraces = self.traceData[:,2:ntr:3]
                self.traceOrder = 'ENZ-ENZ-ENZ' 
                self.stats['order'] = 'ENZ-ENZ-ENZ' 
            
            else:
                self.zTraces = self.traceData[:,0:int(ntr/3)] # indexing from first element to last element with increment(skipt) 3 
                self.xTraces = self.traceData[:,int(ntr/3):int(2*ntr/3)] 
                self.yTraces = self.traceData[:,int(2*ntr/3):ntr]
                self.traceOrder = 'ZZZ-EEE-NNN'
                self.stats['order'] = 'ZZZ-EEE-NNN'
        else:

            self.stats['com'] = 1
            self.zTraces = self.traceData
            self.xTraces = np.zeros((ns, ntr), dtype = np.float32)
            self.yTraces = np.zeros((ns, ntr), dtype = np.float32)
            self.traceOrder = 'ZZZ' 

    def getTraceOrder(self):

        return self.traceOrder


    def setTraceIdentificationCode(self, com, order):

               
        ntr = self.stats['ntr']
        ns = self.stats['ns']

        if com == '3C':           

            self.componentFlag = 3

            
            if order == 'ZEN-ZEN-ZEN':
                self.traceOrder = 'ZEN-ZEN-ZEN'
                self.traceHeader['TraceIdentificationCode'][0:ntr:3][:] = 12.0
                self.traceHeader['TraceIdentificationCode'][1:ntr:3][:] = 13.0
                self.traceHeader['TraceIdentificationCode'][2:ntr:3][:] = 14.0
                self.zTraces = self.traceData[:,0:ntr:3] # indexing from first element to last element with increment(skipt) 3 
                self.xTraces = self.traceData[:,1:ntr:3] 
                self.yTraces = self.traceData[:,2:ntr:3]
            
            elif order == 'ENZ-ENZ-ENZ':
                self.traceOrder = 'ENZ-ENZ-ENZ'
                self.traceHeader['TraceIdentificationCode'][0:ntr:3][:] = 13.0
                self.traceHeader['TraceIdentificationCode'][1:ntr:3][:] = 14.0
                self.traceHeader['TraceIdentificationCode'][2:ntr:3][:] = 12.0
                self.xTraces = self.traceData[:,0:ntr:3] # indexing from first element to last element with increment(skipt) 3 
                self.yTraces = self.traceData[:,1:ntr:3] 
                self.zTraces = self.traceData[:,2:ntr:3]
            
            else:
                
                self.traceOrder = 'ZZZ-EEE-NNN'
                self.traceHeader['TraceIdentificationCode'][0:int(ntr/3)][:] = 12.0
                self.traceHeader['TraceIdentificationCode'][int(ntr/3):int(2*ntr/3)][:] = 13.0
                self.traceHeader['TraceIdentificationCode'][int(2*ntr/3):ntr][:] = 14.0
                self.zTraces = self.traceData[:,0:int(ntr/3)] # indexing from first element to last element with increment(skipt) 3 
                self.xTraces = self.traceData[:,int(ntr/3):int(2*ntr/3)] 
                self.yTraces = self.traceData[:,int(2*ntr/3):ntr]


        else:

            self.componentFlag = 1

            self.zTraces = self.traceData
            self.xTraces = np.zeros((ns, ntr), dtype = np.float32)
            self.yTraces = np.zeros((ns, ntr), dtype = np.float32)
            self.traceOrder = 'ZZZ' 
            self.traceHeader['TraceIdentificationCode'][:] = 1.0


    


    def _setTraceNumber(self, vh ):
        '''
        vh: volume header

        '''
        self.ntr = vh['ntraces']
        self.stats['ntr'] = self.ntr

    def _setSampleNumber(self, vh ):
        '''
        vh: volume header

        '''
        self.ns = vh['ns']
        self.stats['ns'] = self.ns
    

    def _setComponentFlag(self, th):
        '''
        th: trace header

        '''
        # cdp = th['cdp']
        # inline3D = th['Inline3D']
        code = th['TraceIdentificationCode']        
        uniqueness = np.unique(code)        

        if  len(uniqueness) > 1:
            self.componentFlag = int(3)
        else:
            self.componentFlag = int(1)
        
    def getComponentFlag(self):

        return self.componentFlag    

    def _setSampleRate(self, vh):
        '''
        vh: volume header

        '''

        if not len(vh):
            dt = 1000

        dt = vh['dt']  # unit is us

        self.dt = dt*1e-6
        self.df = 1.0/self.dt

        self.stats['dt'] = self.dt
        self.stats['df'] = self.df

    def normalized(self, traces):
    
        arr = traces.copy()
        arr = arr - arr.mean(axis=0)
        arr = arr / np.abs(arr).max(axis=0)

        return arr  

    def normed(self, Data):
        
        dim = Data.ndim

        if dim == 1:
            Data = Data.reshape(len(Data), 1)
        
        (ns, nt) = Data.shape
        # find max of each trace to normalization
        normed = np.empty((ns, nt), dtype='float32')
        maxval = 0.0
        
        for i in range(0, nt, 1):
            trace = np.array(Data[:, i])
            
            if trace.max() > abs(trace.min()):
                maxval = trace.max()
            else:
                maxval = abs(trace.min())
                
            normed[:,i] = trace/(maxval - np.finfo(float).eps)     
        
        return normed 

    def resampledTraces(self, Data, src_fs, tar_fs):
        dim = Data.ndim

        if dim == 1:
            Data = Data.reshape(len(Data), 1)
        
        
        (ns, nt) = Data.shape
        dtp = np.float32
        signal_time_max = 1.0*(ns-1) / src_fs
        tar_sample_max = np.int(signal_time_max*tar_fs)
        output_signal = np.empty((tar_sample_max, nt), dtype = dtp)

        for i in range(0, nt, 1):
            
            input_signal = Data[:, i]
            signal_len = len(input_signal)
            
            signal_time_max = 1.0*(signal_len-1) / src_fs
            src_time = 1.0 * np.linspace(0,signal_len,signal_len) / src_fs
            tar_time = 1.0 * np.linspace(0,np.int(signal_time_max*tar_fs),np.int(signal_time_max*tar_fs)) / tar_fs
            output_signal[:,i] = np.interp(tar_time,src_time,input_signal).astype(dtp)

        return output_signal


    
    def pArrivals(self):
        return self.pPicks

    def sArrivals(self):
        return self.sPicks

    def pickPS(self, nsta, nlta , p_thres, s_thres, method):
        
        p_cfs, s_cfs = self.calcStaLtaCF(nsta, nlta, method)
        
        from ..psmodule.pspicker import trigger_onset

        count = 0
        sPicks = {}
        pPicks = {}

        ns, ntr = p_cfs.shape

        for i in range(ntr):
            
            p_on_off = trigger_onset(p_cfs[:,i], p_thres, p_thres)
            if len(p_on_off):
                pPicks[i] = p_on_off[:, 0]
            else:
                pPicks[i] = []
                

            s_on_off = trigger_onset(s_cfs[:,i], s_thres, s_thres)
            if len(s_on_off):
                sPicks[i] = s_on_off[:, 0]
            else:
                sPicks[i] = []

        return pPicks, sPicks
        

    def calcStaLta(self, traceData, nsta = 30, nlta = 80, method = 'classic_sta_lta', mode = 'continuous'):

        NS, NTR = traceData.shape   

        if mode == 'continuous':

            traceData = traceData.reshape(-1,1, order = 'F')

        ns, ntr = traceData.shape
        cfs = np.zeros((ns, ntr), dtype=np.float32) 
            
        if method == 'classic_sta_lta':
            
            for i in range(ntr):
                trace = traceData[:, i]                             
                cf = classic_sta_lta(trace, nsta, nlta)
                cfs[:,i] = cf

        elif method == 'delayed_sta_lta':
            for i in range(ntr):
                trace = traceData[:, i]                             
                cf = delayed_sta_lta(trace, nsta, nlta)
                cfs[:,i] = cf
            
        elif method == 'recursive_sta_lta':
            for i in range(ntr):
                trace = traceData[:, i]     
                cf = recursive_sta_lta(trace, nsta, nlta)
                cfs[:,i] = cf  

        if mode == 'continuous':
            cfs = cfs.reshape(NS, NTR, order = 'F')

        return cfs


    def _cfStaLta(self, phase = 'p', component = 'z', nsta = 30, nlta = 80, method = 'recursive_sta_lta'):
        
        ns, ntr = self.traceData.shape
        if self.componentFlag == 1:
            cfs = np.empty((ns, ntr), dtype=np.float32)            
            
            if method == 'classic_sta_lta':
                for i in range(ntr):
                    trace = self.traceData[:, i]                             
                    cf = classic_sta_lta(trace, nsta, nlta)
                    cfs[:,i] = cf

            elif method == 'delayed_sta_lta':
                for i in range(ntr):
                    trace = self.traceData[:, i]                             
                    cf = delayed_sta_lta(trace, nsta, nlta)
                    cfs[:,i] = cf
                
            elif method == 'recursive_sta_lta':
                for i in range(ntr):
                    trace = self.traceData[:, i]     
                    cf = recursive_sta_lta(trace, nsta, nlta)
                    cfs[:,i] = cf          
               

        else:
            cfs = np.empty((ns, int(ntr/3)), dtype=np.float32)
            
            if phase == 'p':

                traceData = self.zTraces

            else:

                if component == 'e':
                    traceData = self.xTraces
                else:
                    traceData = self.yTraces


            if method == 'classic_sta_lta':   

                trace = traceData[:, i]             
                cf = classic_sta_lta(trace, nsta, nlta)
                cfs[:,i] = cf 

            elif  method == 'delayed_sta_lta':
                
                trace = traceData[:, i]            
                cf = delayed_sta_lta(trace, nsta, nlta)
                cfs[:,i] = cf 
                
            elif  method == 'recursive_sta_lta':
                trace = traceData[:, i]            
                cf = recursive_sta_lta(trace, nsta, nlta)
                cfs[:,i] = cf 
                              


        return cfs

    
    

    def imagePlot(self, Data, SH = None):
        if SH == None:
            SH = self.volumeHeader
        image(Data, SH)
    
    def wigglePlot(self, Data, SH = None):
        if SH == None:
            SH = self.volumeHeader
        wiggle(Data, SH)

    def wiggle(self, Data, SH={}, maxval=-1, skipt=1, lwidth=.5, x=[], t=[], gain=1, type='VA', color='black', ntmax=1e+9, holdon = 'on'):
    
        """

        wiggle(Data,SH)

        """

        import matplotlib.pylab as plt

        import numpy as np

        import copy

        

        yl='Sample number'

        

        ns = Data.shape[0]

        ntraces = Data.shape[1]



        if ntmax<ntraces:

            skipt=int(np.floor(ntraces/ntmax))

            if skipt<1:

                    skipt=1





        if len(x)==0:

            x=range(0, ntraces)



        if len(t)==0:

            t=range(0, ns)

        else:

            yl='Time  [s]'

        

        

        # overrule time form SegyHeader

        if 'time' in SH:

            t = SH['time']

            yl='Time  [s]'

        

            

        dx = x[1]-x[0]    

        if (maxval<=0):

            Dmax = np.nanmax(Data)

            maxval = -1*maxval*Dmax

            #print('pssegy.wiggle: maxval = %g' % maxval)

            

        if self.ax == None:

            fig, self.ax = plt.subplots(1, 1)

        # fig = plt.gcf()

        # ax1 = plt.gca()

        

        for i in range(0, ntraces, skipt):

            # use copy to avoid truncating the data

            trace = copy.copy(Data[:, i])

            trace[0] = 0

            trace[-1] = 0

            self.ax.plot(x[i] + gain * skipt * dx * trace / maxval, t, color=color, linewidth=lwidth)

            

            if type=='VA':

                for a in range(len(trace)):

                    if (trace[a] < 0):

                        trace[a] = 0

                        # pylab.fill(i+Data[:,i]/maxval,t,color='k',facecolor='g')

                #ax1.fill(x[i] + dx * Data[:, i] / maxval, t, 'k', linewidth=0, color=color)

                self.ax.fill(x[i] + gain * skipt * dx * trace / (maxval), t, 'k', linewidth=0, color=color)



        #ax1.grid(True)

        self.ax.invert_yaxis()

        plt.ylim([np.max(t),np.min(t)])

        



        plt.xlabel('Trace number')

        plt.ylabel(yl)

        # if 'filename' in SH:

        #     plt.title(SH['filename'])

        self.ax.set_xlim(-1, ntraces)

        if holdon == 'off':

            plt.show()

    

