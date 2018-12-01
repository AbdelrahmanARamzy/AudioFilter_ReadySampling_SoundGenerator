# 2nd Task DSP/ Group 6/ Abdelrahman Ramzy, Bassel Samer & Mostafa Kingham/Feb-2018
# Imported Libraries
import sys
import pyaudio
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QApplication
from PyQt5 import QtCore, QtGui, uic

from ctypes import *
import ctypes

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import pyqtgraph as pg

from scipy import signal
import plotly
time_of_view = 1.0  # s.
analog_time = np.linspace(0, time_of_view, 10e5)  # s.
sampling_rate = 50.0  # Hz
sampling_period = 1.0 / sampling_rate  # s
sample_number = time_of_view / sampling_period
sampling_time = np.linspace(0, time_of_view, sample_number)
carrier_frequency = 9.0
amplitude = 1
phase = 0
global clickedd  # checker
clickedd = 0

def OpenedFile(fileName):
    i = len(fileName)-1
    j = -1
    x = 1

    while x == 1:
            if fileName[i] != '/':
                j += 1
                i -= 1
            else:
                x = 0
    File_Names = np.zeros(j+1)

    # Convert from Float to a list of strings
    File_Name = ["%.2f" % number for number in File_Names]
    for k in range(0, j+1):
        File_Name[k] = fileName[len(fileName)-1+k-j]  # List of Strings
    # Convert list of strings to a string
    FileName = ''.join(File_Name)  # String
    return FileName
# Used For C Wrapping
def our_function(numbers):
    global libtest
    num_numbers = len(numbers)
    array_type = ctypes.c_int * num_numbers
    result = libtest.our_function(ctypes.c_int(num_numbers), array_type(*numbers))
    return int(result)

# GUI
class Signal_Plot(QDialog):
    def __init__(self):
        super(Signal_Plot, self).__init__()
        loadUi('Signal_Plot.ui', self)

        # 6 Buttons, Button_2 is initiated when load is pressed in the GUI & Button is initiated when filter is pressed
        self.pushButton.clicked.connect(self.set_filter)
        self.pushButton_2.clicked.connect(self.get_files)
        self.pushButton_3.clicked.connect(self.generate)
        self.pushButton_4.clicked.connect(self.decay)
        self.pushButton_5.clicked.connect(self.sine)
        self.pushButton_6.clicked.connect(self.cosine)
        self.pushButton_7.clicked.connect(self.expo)
        self.pushButton_8.clicked.connect(self.sumup)
        #self.dataplot = self.graphicsView.addPlot(title="My Data")

    def compute_initial_figure(self):
        pass

    @pyqtSlot()
    # The function called when Load File or Button 2 is pressed
    def get_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # QFileDialog.getOpenFileName(Path,Filter) we used [0] as we want the path itself
        fileName = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]  # , '*.csv'
        # To get the file name itself without the path

        global file_name
        file_name = OpenedFile(fileName)
        print(file_name)
        # make sure the extension is correct
        if (file_name[len(file_name) - 1] != 'v' and file_name[len(file_name) - 2] != 's' and
                file_name[len(file_name) - 3] != 'c'):
            QMessageBox.about(self, "Error!", "Please choose a .csv file")
            return

        # Read csv file
        global Signal_Set  # Global to be moved or used between functions
        Signal_Set01 = pd.read_csv(fileName)
        Signal_Set02 = np.array(Signal_Set01)
        Signal_Set03 = Signal_Set02.transpose()
        Signal_Set   = Signal_Set03[1][1:].astype(np.float)
        global clickedd
        clickedd = 1

        # Plot Signal
        plt.figure(1)  # the first figure
        plt.plot(Signal_Set, 'r')
        plt.title(file_name + " Unfiltered")
        plt.grid()
        plt.show()
        self.graphicsView.clear()
        self.graphicsView.plot(Signal_Set)

    # The function called when Filter or Button 1 is pressed
    def set_filter(self):
        # Filter parameters
        global clickedd
        if(clickedd == 0):
            QMessageBox.about(self, "Error!", "Please choose a .csv file")
            return
        line1 = self.lineEdit.text()
        line2 = self.lineEdit_2.text()
        line3 = self.lineEdit_3.text()
        global Signal_Set
        # Setting up the filter
        FilterPar = [int(line1), int(line2), int(line3)]
        Filtered_Signal = signal.convolve(Signal_Set, FilterPar)
        # Plot The Filtered Signal
        plt.figure(2)
        plt.plot(Filtered_Signal, 'r')
        plt.title(file_name + " filtered")
        plt.grid()
        plt.show()
        self.graphicsView_2.clear()
        self.graphicsView_2.plot(Filtered_Signal)

    def generate(self):
        p = pyaudio.PyAudio()
        freq1 = self.lineEdit_4.text()
        freq2 = self.lineEdit_5.text()
        time = self.lineEdit_6.text()
        f1 = float(freq1)
        f2 = float(freq2)
        volume = 0.5  # range [0.0, 1.0]
        fs = 44100  # sampling rate, Hz, must be integer
        duration = float(time)  # in seconds, may be float
        if (f1 < 20 or f1 > 20000):
            QMessageBox.about(self, "Error!", "Please Write the Frequency in the range of 20 : 20000 Hz")
            return
        if (f2 < 20 or f2 > 20000):
            QMessageBox.about(self, "Error!", "Please Write the Frequency in the range of 20 : 20000 Hz")
            return
        if (duration > 300):
            QMessageBox.about(self, "Error!", "Please Write the Time less than 300 seconds")
            return


        # generate samples, note conversion to float32 array
        samples = (np.sin(2 * np.pi * np.arange(fs * duration) * f1 / fs) + np.sin(
            2 * np.pi * np.arange(fs * duration) * f2 / fs)).astype(
            np.float32)

        # for paFloat32 sample values must be in range [-1.0, 1.0]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=fs,
                        output=True)

        # play. May repeat with different volume values (if done interactively)
        stream.write(volume * samples)

        stream.stop_stream()
        stream.close()

        p.terminate()

    def decay(self):

        p = pyaudio.PyAudio()
        freq1 = self.lineEdit_4.text()
        freq2 = self.lineEdit_5.text()
        time = self.lineEdit_6.text()
        expo = self.lineEdit_7.text()
        f1 = float(freq1)
        f2 = float(freq2)
        expo_ = float(expo) * -1
        volume = 0.5  # range [0.0, 1.0]
        fs = 44100  # sampling rate, Hz, must be integer
        duration = float(time)  # in seconds, may be float
        # 440.0  # sine frequency, Hz, may be float

        if f1 < 20 or f1 > 20000:
            self.label_9.setText("Please Write the Frequency in range between 20 and 20000 ")
            return
        if f2 < 20 or f2 > 20000:
            self.label_9.setText("Please Write the Frequency in range between 20 and 20000")
            return
        if duration > 300:
            self.label_9.setText("Please Write the Time less than 300 seconds")
            return

        # generate samples, note conversion to float32 array
        samples = (np.sin(2 * np.pi * np.arange(fs * duration) * f1 / fs) + np.sin(
            2 * np.pi * np.arange(fs * duration) * f2 / fs) + np.exp(np.arange(fs * duration) * expo_ / fs)).astype(
            np.float32)

        # for paFloat32 sample values must be in range [-1.0, 1.0]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=fs,
                        output=True)

        # play. May repeat with different volume values (if done interactively)
        stream.write(volume * samples)

        stream.stop_stream()
        stream.close()

        p.terminate()

    def sine(self):
        def sin_signal(time_point):
            return amplitude * np.sin(2 * carrier_frequency * time_point + phase)

        Sin_sampling_signal = sin_signal(sampling_time)
        fig = plt.figure(3)
        plt.plot(analog_time, sin_signal(analog_time))
        plt.stem(sampling_time, Sin_sampling_signal, linefmt='r', markerfmt='rs', basefmt='y-')
        plt.title(" Sine Signal after sampling")
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        plt.show()

    def cosine(self):
        def cos_signal(time_point):
            return amplitude * np.cos(2 * carrier_frequency * time_point + phase)

        cos_sampling_signal = cos_signal(sampling_time)
        fig = plt.figure(4)
        plt.plot(analog_time, cos_signal(analog_time))
        plt.stem(sampling_time, cos_sampling_signal, linefmt='b', markerfmt='rs', basefmt='y-')
        plt.title("cosine signal after sampling ")
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        plt.show()

    def expo(self):
        def Exp_signal(time_point):
            return amplitude * np.exp(2 * carrier_frequency * time_point + phase)

        fig = plt.figure(5)
        sampling_signal = Exp_signal(sampling_time)
        plt.plot(analog_time, Exp_signal(analog_time))
        plt.stem(sampling_time, sampling_signal, linefmt='g', markerfmt='rs', basefmt='y-')
        plt.title(" Exponential Signal after sampling")
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        plt.show()
    def sumup(self):
        global libtest
        libtest = cdll.LoadLibrary("dlltest102.dll")
        libtest.our_function.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_int))

        STR_Input_Array = self.lineEdit_8.text()
        PLT_Input_Array = (STR_Input_Array).split()
        INT_Input_Array = list(map(int, PLT_Input_Array))
        resultss = our_function(INT_Input_Array)
        QMessageBox.about(self, "Sum Array", str(resultss))
        return

if __name__ == "__main__":
    app = 0  # This is the solution As the Kernel died every time I restarted the consol
    app = QApplication(sys.argv)
    widget = Signal_Plot()
    widget.show()
    sys.exit(app.exec_())
