# -*- coding: utf-8 -*-
from serial.tools import list_ports
import fnmatch
import serial
import mysql.connector
import time,sys,json
import csv,os
# Form implementation generated from reading ui file 'luncherUI.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Settings(QtWidgets.QWidget):
    def __init__(self,parent,mode=1): #1 is standalone 2 is embeded in luncher
        super().__init__()
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

        self.mode=mode

        jsondat = open('settings.json').read()
        self.jsettings=json.loads(jsondat)

        self.setupUi(self)
        self.parent=parent

        dispGroup=QtWidgets.QButtonGroup(self)
        dispGroup.addButton(self.d1tBox)
        dispGroup.addButton(self.d1bBox)
        dispGroup.addButton(self.d2tBox)
        dispGroup.addButton(self.d2bBox)
        if self.jsettings['session_default']['position'] == 0:
            self.d1tBox.setChecked(True)
        elif self.jsettings['session_default']['position'] == 1:
            self.d1bBox.setChecked(True)
        elif self.jsettings['session_default']['position'] == 2:
            self.d2tBox.setChecked(True)
        elif self.jsettings['session_default']['position'] == 3:
            self.d2bBox.setChecked(True)

        self.transitionBox.setValue(self.jsettings['mcu_config']['transition'])
        self.trainingPhaseBox.setValue(self.jsettings['mcu_config']['training_phase'])
        self.dripBox.setValue(self.jsettings['mcu_config']['drip_delay_time'])
        self.punishBox.setValue(self.jsettings['mcu_config']['punishment_duration'])
        self.delayBox.setValue(self.jsettings['mcu_config']['delay_duration'])
        self.toneBox.setValue(self.jsettings['mcu_config']['tone_duration'])
        self.betweenToneBox.setValue(self.jsettings['mcu_config']['time_between_tones'])
        self.valveBoxL.setValue(self.jsettings['mcu_config']['valve_open_time_L'])
        self.valveBoxR.setValue(self.jsettings['mcu_config']['valve_open_time_R'])
        self.lickBox.setValue(self.jsettings['mcu_config']['lickwindow_duration'])
        self.trailBox.setValue(self.jsettings['mcu_config']['trial_number'])
        self.minBox.setValue(self.jsettings['mcu_config']['min_difficulty'])
        self.maxBox.setValue(self.jsettings['mcu_config']['max_difficulty'])
        self.encourageBox.setValue(self.jsettings['mcu_config']['encourage'])
        self.encourageDelayBox.setValue(self.jsettings['mcu_config']['encourage_delay'])
        self.song1.setText(self.jsettings['mcu_config']['song1'])
        self.song2.setText(self.jsettings['mcu_config']['song2'])
        self.song3.setText(self.jsettings['mcu_config']['song3'])
        self.song4.setText(self.jsettings['mcu_config']['song4'])
        self.song5.setText(self.jsettings['mcu_config']['song5'])
        self.song6.setText(self.jsettings['mcu_config']['song6'])
        if mode==1:
            self.downloadButton.clicked.connect(self.getout)
        self.minBox.valueChanged.connect(self.repairLimit)
        self.maxBox.valueChanged.connect(self.repairLimit)

        self.show()


    def repairLimit(self):
        self.maxBox.setMinimum(self.minBox.value())
        self.minBox.setMaximum(self.maxBox.value())
    def getout(self):
        self.dict2json()

        self.download()
        with open('settings.json', 'w') as outfile:
            json.dump(self.jsettings, outfile)
        if self.mode==1:
            self.close()
    def dict2json(self):
        self.jsettings['mcu_config']['song1'] = self.song1.text()
        self.jsettings['mcu_config']['song2'] = self.song2.text()
        self.jsettings['mcu_config']['song3'] = self.song3.text()
        self.jsettings['mcu_config']['song4'] = self.song4.text()
        self.jsettings['mcu_config']['song5'] = self.song5.text()
        self.jsettings['mcu_config']['song6'] = self.song6.text()

        self.jsettings['mcu_config']['encourage_delay'] = self.encourageDelayBox.value()
        self.jsettings['mcu_config']['encourage'] = self.encourageBox.value()

        self.jsettings['mcu_config']['drip_delay_time'] = self.dripBox.value()
        self.jsettings['mcu_config']['punishment_duration'] = self.punishBox.value()
        self.jsettings['mcu_config']['delay_duration'] = self.delayBox.value()
        self.jsettings['mcu_config']['tone_duration'] = self.toneBox.value()
        self.jsettings['mcu_config']['time_between_tones'] = self.betweenToneBox.value()
        self.jsettings['mcu_config']['valve_open_time_L'] = self.valveBoxL.value()
        self.jsettings['mcu_config']['valve_open_time_R'] = self.valveBoxR.value()
        self.jsettings['mcu_config']['lickwindow_duration'] = self.lickBox.value()
        self.jsettings['mcu_config']['trial_number'] = self.trailBox.value()
        self.jsettings['mcu_config']['min_difficulty'] = self.minBox.value()
        self.jsettings['mcu_config']['max_difficulty'] = self.maxBox.value()
        self.jsettings['mcu_config']['training_phase'] = self.trainingPhaseBox.value()
        self.jsettings['mcu_config']['transition'] = self.transitionBox.value()

        self.jsettings['session_default']['position'] += 1
        if self.jsettings['session_default']['position'] == 5:
            self.jsettings['session_default']['position'] = 1
    def download(self):
        try:
            print("download step 1")
            thepoop=self.buildConfig()
            print("download step 2")
            return thepoop

        except Exception as e:
            print("download string build error"+str(e))
    def buildConfig(self):
        TONETRAN={'C8':0,'Db8':1,'D8':2,'Eb8':3,'E8':4,'F8':5,'Gb8':6,'G8':7,'Ab8':8,'A8':9,'Bb8':10,'B8':11,'C9':12,'Db9':13,'D9':14,'Eb9':15,'E9':16,'0':255}
        self.dict2json()
        self.config=[]
        # 0th char: 0x11, send this so that the mcu knows you're about to send setting
        self.config.append(b'\x11')
        #1st char: training phase

        self.config.append(bytearray([self.jsettings['mcu_config']['training_phase']]))
        self.config.append(bytearray([self.jsettings['mcu_config']['min_difficulty']]))
        self.config.append(bytearray([self.jsettings['mcu_config']['max_difficulty']]))

        self.config.append(bytearray([TONETRAN[self.song1.text()]]))
        self.config.append(bytearray([TONETRAN[self.song2.text()]]))
        self.config.append(bytearray([TONETRAN[self.song3.text()]]))
        self.config.append(bytearray([TONETRAN[self.song4.text()]]))
        self.config.append(bytearray([TONETRAN[self.song5.text()]]))##TODO: replace after GUI is updated for 5&6
        self.config.append(bytearray([TONETRAN[self.song6.text()]]))


        #trail number 10th, 11th char: number of trials, int (i.e. 6th: 0x01, 7th: 0x2C) --> 300
        self.config.append(bytearray([int(self.jsettings['mcu_config']['trial_number']/256)]))
        self.config.append(bytearray([int(self.jsettings['mcu_config']['trial_number'] % 256)]))
        #delay duration 12th, 13th char: duration of delay (units of 10 ms)

        self.config.append(bytearray([int(self.jsettings['mcu_config']['delay_duration']*100 / 256)]))
        self.config.append(bytearray([int(self.jsettings['mcu_config']['delay_duration']*100 % 256)]))
        #14th, 15th char: duration of punishment if mouse licks incorrectly (units of 10 ms)

        self.config.append(bytearray([int(self.jsettings['mcu_config']['punishment_duration'] / 256*100)]))
        self.config.append(bytearray([int(self.jsettings['mcu_config']['punishment_duration']*100 % 256)]))
        #16th, 17th char: lick window duration (units of 10 ms)
        self.config.append(bytearray([int(self.jsettings['mcu_config']['lickwindow_duration'] / 256*100)]))
        self.config.append(bytearray([int(self.jsettings['mcu_config']['lickwindow_duration']*100 % 256)]))

#         18th char: tone duration (units of 10 ms)
        self.config.append(bytearray([int(self.jsettings['mcu_config']['tone_duration']*100)]))

    # 19th char: duration of time between tones (units of 10 ms)
        self.config.append(bytearray([int(self.jsettings['mcu_config']['time_between_tones']*100)]))
#
# 20th char: duration of right valve open time (units of 10 ms)
        self.config.append(bytearray([int(self.jsettings['mcu_config']['valve_open_time_R']*100)]))

# 21th char: duration of left valve open time (units of 10 ms)
        self.config.append(bytearray([int(self.jsettings['mcu_config']['valve_open_time_L']*100)]))

    # 22th char: duration of time between song and reward for training phase 1
        self.config.append(bytearray([int(self.jsettings['mcu_config']['encourage_delay']*100)]))
    # 23th char: number of no lick trials until mouse is given an encouragement drop
        self.config.append(bytearray(b'\x00'))
    #24th char: how likely mouse is to get encouragement drop
        self.config.append(bytearray([int(self.jsettings['mcu_config']['encourage'])])) ###############################################TODO: change after update GUI
##      25th: transition
        self.config.append(bytearray([self.jsettings['mcu_config']['transition']])) ###############################################TODO: change after update GUI


    # 26th, 27th char: checksum. I'm pretty sure that two chars should be enough to sum all the parameters
        summ=0
        print("the built string is: "+str(self.config))
        iterchars = iter(self.config)
        next(iterchars)
        for item in iterchars:
            summ=summ+int.from_bytes(item, byteorder='big', signed=False)
           # print(sum)
##        summ = summ - 17
        self.config.append(bytearray([int(summ / 256)]))
        self.config.append(bytearray([int(summ % 256)]))
        print("### The Lengh of Download Command is " , str(len(self.config)))
        print("### " + str(self.config))
        cris=b''
        for con in self.config:
            cris=cris+con
        return cris
    #
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(404, 584)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_2.addWidget(self.line, 2, 0, 1, 1)
##        self.downloadButton = QtWidgets.QPushButton(Form)
##        self.downloadButton.setObjectName("downloadButton")
##        self.gridLayout_2.addWidget(self.downloadButton, 3, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.betweenToneBox = QtWidgets.QDoubleSpinBox(Form)
        self.betweenToneBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.betweenToneBox.setMaximum(5.0)
        self.betweenToneBox.setSingleStep(0.05)
        self.betweenToneBox.setObjectName("betweenToneBox")
        self.horizontalLayout_4.addWidget(self.betweenToneBox)
        self.label_13 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_4.addWidget(self.label_13)
        self.gridLayout.addLayout(self.horizontalLayout_4, 7, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.punishBox = QtWidgets.QDoubleSpinBox(Form)
        self.punishBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.punishBox.setMaximum(5.0)
        self.punishBox.setSingleStep(0.05)
        self.punishBox.setObjectName("punishBox")
        self.horizontalLayout_2.addWidget(self.punishBox)
        self.label_16 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_2.addWidget(self.label_16)
        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.toneBox = QtWidgets.QDoubleSpinBox(Form)
        self.toneBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.toneBox.setMaximum(5.0)
        self.toneBox.setSingleStep(0.05)
        self.toneBox.setObjectName("toneBox")
        self.horizontalLayout_3.addWidget(self.toneBox)
        self.label_14 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_3.addWidget(self.label_14)
        self.gridLayout.addLayout(self.horizontalLayout_3, 5, 0, 1, 1)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_10 = QtWidgets.QLabel(Form)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_8.addWidget(self.label_10)
        self.label_25 = QtWidgets.QLabel(Form)
        self.label_25.setObjectName("label_25")
        self.horizontalLayout_8.addWidget(self.label_25, 0, QtCore.Qt.AlignRight)
        self.valveBoxL = QtWidgets.QDoubleSpinBox(Form)
        self.valveBoxL.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.valveBoxL.setMaximum(5.0)
        self.valveBoxL.setSingleStep(0.05)
        self.valveBoxL.setObjectName("valveBoxL")
        self.horizontalLayout_8.addWidget(self.valveBoxL)
        self.label_11 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_8.addWidget(self.label_11)
        self.line_7 = QtWidgets.QFrame(Form)
        self.line_7.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.horizontalLayout_8.addWidget(self.line_7)
        self.label_26 = QtWidgets.QLabel(Form)
        self.label_26.setObjectName("label_26")
        self.horizontalLayout_8.addWidget(self.label_26, 0, QtCore.Qt.AlignRight)
        self.valveBoxR = QtWidgets.QDoubleSpinBox(Form)
        self.valveBoxR.setMaximum(5.0)
        self.valveBoxR.setSingleStep(0.05)
        self.valveBoxR.setObjectName("valveBoxR")
        self.horizontalLayout_8.addWidget(self.valveBoxR)
        self.label_24 = QtWidgets.QLabel(Form)
        self.label_24.setObjectName("label_24")
        self.horizontalLayout_8.addWidget(self.label_24)
        self.gridLayout.addLayout(self.horizontalLayout_8, 9, 0, 1, 1)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_17 = QtWidgets.QLabel(Form)
        self.label_17.setObjectName("label_17")
        self.horizontalLayout_13.addWidget(self.label_17)
        self.trailBox = QtWidgets.QSpinBox(Form)
        self.trailBox.setMaximum(999)
        self.trailBox.setSingleStep(5)
        self.trailBox.setObjectName("trailBox")
        self.horizontalLayout_13.addWidget(self.trailBox)
        self.gridLayout.addLayout(self.horizontalLayout_13, 18, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_20 = QtWidgets.QLabel(Form)
        self.label_20.setObjectName("label_20")
        self.horizontalLayout_5.addWidget(self.label_20)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.d1tBox = QtWidgets.QRadioButton(Form)
        self.d1tBox.setObjectName("d1tBox")
        self.gridLayout_3.addWidget(self.d1tBox, 0, 0, 1, 1)
        self.d2tBox = QtWidgets.QRadioButton(Form)
        self.d2tBox.setObjectName("d2tBox")
        self.gridLayout_3.addWidget(self.d2tBox, 0, 1, 1, 1)
        self.d1bBox = QtWidgets.QRadioButton(Form)
        self.d1bBox.setObjectName("d1bBox")
        self.gridLayout_3.addWidget(self.d1bBox, 1, 0, 1, 1)
        self.d2bBox = QtWidgets.QRadioButton(Form)
        self.d2bBox.setObjectName("d2bBox")
        self.gridLayout_3.addWidget(self.d2bBox, 1, 1, 1, 1)
        self.horizontalLayout_5.addLayout(self.gridLayout_3)
        self.gridLayout.addLayout(self.horizontalLayout_5, 21, 0, 1, 1)
        self.line_3 = QtWidgets.QFrame(Form)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 15, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 20, 0, 1, 1)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_18 = QtWidgets.QLabel(Form)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_12.addWidget(self.label_18)
        self.dripBox = QtWidgets.QDoubleSpinBox(Form)
        self.dripBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.dripBox.setMaximum(5.0)
        self.dripBox.setSingleStep(0.05)
        self.dripBox.setObjectName("dripBox")
        self.horizontalLayout_12.addWidget(self.dripBox)
        self.label_19 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_12.addWidget(self.label_19)
        self.gridLayout.addLayout(self.horizontalLayout_12, 10, 0, 1, 1)
        self.line_4 = QtWidgets.QFrame(Form)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout.addWidget(self.line_4, 13, 0, 1, 1)
        self.line_5 = QtWidgets.QFrame(Form)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.gridLayout.addWidget(self.line_5, 1, 0, 1, 1)
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.label_29 = QtWidgets.QLabel(Form)
        self.label_29.setObjectName("label_29")
        self.horizontalLayout_17.addWidget(self.label_29)
        self.encourageDelayBox = QtWidgets.QDoubleSpinBox(Form)
        self.encourageDelayBox.setMaximum(255)
        self.encourageDelayBox.setSingleStep(1)
        self.encourageDelayBox.setObjectName("encourageDelayBox")
        self.horizontalLayout_17.addWidget(self.encourageDelayBox)
        self.label_30 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_30.sizePolicy().hasHeightForWidth())
        self.label_30.setSizePolicy(sizePolicy)
        self.label_30.setObjectName("label_30")
        self.horizontalLayout_17.addWidget(self.label_30)
        self.gridLayout.addLayout(self.horizontalLayout_17, 12, 0, 1, 1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_7.addWidget(self.label_5)
        self.lickBox = QtWidgets.QDoubleSpinBox(Form)
        self.lickBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.lickBox.setMaximum(5.0)
        self.lickBox.setSingleStep(0.05)
        self.lickBox.setObjectName("lickBox")
        self.horizontalLayout_7.addWidget(self.lickBox)
        self.label_12 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_7.addWidget(self.label_12)
        self.gridLayout.addLayout(self.horizontalLayout_7, 8, 0, 1, 1)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.delayBox = QtWidgets.QDoubleSpinBox(Form)
        self.delayBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.delayBox.setMaximum(5.0)
        self.delayBox.setSingleStep(0.05)
        self.delayBox.setObjectName("delayBox")
        self.horizontalLayout_6.addWidget(self.delayBox)
        self.label_15 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_6.addWidget(self.label_15)
        self.gridLayout.addLayout(self.horizontalLayout_6, 4, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.trainingPhaseBox = QtWidgets.QSpinBox(Form)
        self.trainingPhaseBox.setMaximumSize(QtCore.QSize(80, 16777215))
        self.trainingPhaseBox.setObjectName("trainingPhaseBox")
        self.horizontalLayout.addWidget(self.trainingPhaseBox)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_10.addWidget(self.label_7)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_8 = QtWidgets.QLabel(Form)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_11.addWidget(self.label_8)
        self.maxBox = QtWidgets.QSpinBox(Form)
        self.maxBox.setObjectName("maxBox")
        self.horizontalLayout_11.addWidget(self.maxBox)
        self.horizontalLayout_10.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_9 = QtWidgets.QLabel(Form)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_9.addWidget(self.label_9)
        self.minBox = QtWidgets.QSpinBox(Form)
        self.minBox.setObjectName("minBox")
        self.horizontalLayout_9.addWidget(self.minBox)
        self.horizontalLayout_10.addLayout(self.horizontalLayout_9)
        self.gridLayout.addLayout(self.horizontalLayout_10, 14, 0, 1, 1)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.label_27 = QtWidgets.QLabel(Form)
        self.label_27.setObjectName("label_27")
        self.horizontalLayout_16.addWidget(self.label_27)
        self.encourageBox = QtWidgets.QSpinBox(Form)
        self.encourageBox.setObjectName("encourageBox")
        self.horizontalLayout_16.addWidget(self.encourageBox)
     ##   self.label_28 = QtWidgets.QLabel(Form)
     ##   self.label_28.setObjectName("label_28")
     ##   self.horizontalLayout_16.addWidget(self.label_28)
        self.gridLayout.addLayout(self.horizontalLayout_16, 11, 0, 1, 1)
        self.line_6 = QtWidgets.QFrame(Form)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.gridLayout.addWidget(self.line_6, 17, 0, 1, 1)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_23 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_23.sizePolicy().hasHeightForWidth())
        self.label_23.setSizePolicy(sizePolicy)
        self.label_23.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label_23.setObjectName("label_23")
        self.horizontalLayout_14.addWidget(self.label_23, 0, QtCore.Qt.AlignLeft)
        self.song1 = QtWidgets.QLineEdit(Form)
        self.song1.setMaximumSize(QtCore.QSize(30, 16777215))
        self.song1.setObjectName("song1")
        self.horizontalLayout_14.addWidget(self.song1)
        self.song2 = QtWidgets.QLineEdit(Form)
        self.song2.setMaximumSize(QtCore.QSize(30, 16777215))
        self.song2.setObjectName("song2")
        self.horizontalLayout_14.addWidget(self.song2)
        self.song3 = QtWidgets.QLineEdit(Form)
        self.song3.setMaximumSize(QtCore.QSize(30, 16777215))
        self.song3.setObjectName("song3")
        self.horizontalLayout_14.addWidget(self.song3)
        self.song4 = QtWidgets.QLineEdit(Form)
        self.song4.setMaximumSize(QtCore.QSize(30, 16777215))
        self.song4.setObjectName("song4")
        self.horizontalLayout_14.addWidget(self.song4)
        self.song5 = QtWidgets.QLineEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.song5.sizePolicy().hasHeightForWidth())
        self.song5.setSizePolicy(sizePolicy)
        self.song5.setMaximumSize(QtCore.QSize(30, 16777215))
        self.song5.setObjectName("song5")
        self.horizontalLayout_14.addWidget(self.song5)
        self.song6 = QtWidgets.QLineEdit(Form)
        self.song6.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.song6.sizePolicy().hasHeightForWidth())
        self.song6.setSizePolicy(sizePolicy)
        self.song6.setMaximumSize(QtCore.QSize(30, 16777215))
        self.song6.setMaxLength(3)
        self.song6.setObjectName("song6")
        self.horizontalLayout_14.addWidget(self.song6)
        self.gridLayout.addLayout(self.horizontalLayout_14, 16, 0, 1, 1)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_21 = QtWidgets.QLabel(Form)
        self.label_21.setObjectName("label_21")
        self.horizontalLayout_15.addWidget(self.label_21)
        self.transitionBox = QtWidgets.QSpinBox(Form)
        self.transitionBox.setMaximum(100)
        self.transitionBox.setObjectName("transitionBox")
        self.horizontalLayout_15.addWidget(self.transitionBox)
        self.gridLayout.addLayout(self.horizontalLayout_15, 19, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)
####
        if self.mode ==1:
            self.downloadButton = QtWidgets.QPushButton(Form)
            self.downloadButton.setObjectName("downloadButton")
            self.gridLayout_2.addWidget(self.downloadButton, 3, 0, 1, 1)

####
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)


    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
    ##    self.downloadButton.setText(_translate("Form", "Download Settings"))
        self.label_4.setText(_translate("Form", "Time Between Tones"))
        self.label_13.setText(_translate("Form", "Seconds"))
        self.label_2.setText(_translate("Form", "Punishment Duration"))
        self.label_16.setText(_translate("Form", "Seconds"))
        self.label_3.setText(_translate("Form", "Tone Duration"))
        self.label_14.setText(_translate("Form", "Seconds"))
        self.label_10.setText(_translate("Form", "Valve Open Time"))
        self.label_25.setText(_translate("Form", "L"))
        self.label_11.setText(_translate("Form", "Seconds"))
        self.label_26.setText(_translate("Form", "R"))
        self.label_24.setText(_translate("Form", "Seconds"))
        self.label_17.setText(_translate("Form", "Trail Number"))
        self.label_20.setText(_translate("Form", "GUI Position"))
        self.d1tBox.setText(_translate("Form", "Disp1 Top"))
        self.d2tBox.setText(_translate("Form", "Disp2 Top"))
        self.d1bBox.setText(_translate("Form", "Disp1 Bottom"))
        self.d2bBox.setText(_translate("Form", "Disp2 Bottom"))
        self.label_18.setText(_translate("Form", "Drip Delay Time"))
        self.label_19.setText(_translate("Form", "Seconds"))
        self.label_29.setText(_translate("Form", "Encouragment Reward Delay"))
        self.label_30.setText(_translate("Form", "Seconds"))
        self.label_5.setText(_translate("Form", "Lickwindow Duration"))
        self.label_12.setText(_translate("Form", "Seconds"))
        self.label_6.setText(_translate("Form", "Delay Duration"))
        self.label_15.setText(_translate("Form", "Seconds"))
        self.label.setText(_translate("Form", "Training Phase"))
        self.label_7.setText(_translate("Form", "Difference"))
        self.label_8.setText(_translate("Form", "Max"))
        self.label_9.setText(_translate("Form", "Min"))
        self.label_27.setText(_translate("Form", "Encouragement Drop          1/"))
    ##    self.label_28.setText(_translate("Form", "No licks"))
        self.label_23.setText(_translate("Form", "Song"))
        self.song1.setText(_translate("Form", "C8"))
        self.song2.setText(_translate("Form", "B"))
        self.song3.setText(_translate("Form", "C"))
        self.song4.setText(_translate("Form", "C9"))

        self.label_21.setText(_translate("Form", "Phase 1-2 Transitioning"))
####
        self.song5.setText(_translate("Form", "0"))
        self.song6.setText(_translate("Form", "0"))
        if self.mode ==1:
            self.downloadButton.setText(_translate("Form", "Download Settings"))
####

# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     prep = Settings("COM4")
#     app.exec_()
