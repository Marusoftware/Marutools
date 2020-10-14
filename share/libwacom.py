######################################
#Marusoftware LibWacom python wrapper#
######################################
import ctypes
import ctypes.util
import os

libwacom = ctypes.cdll.LoadLibrary(ctypes.util.find_library("wacom"))
