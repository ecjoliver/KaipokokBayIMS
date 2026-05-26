'''
    Global variables for running the IMS code
    This is loaded in by each script
'''

import pandas as pd
import numpy as np
import scipy
import xarray as xr
from netCDF4 import Dataset
import datetime
from datetime import date
import glob
import os
import sys
import pickle
from scipy import io
from scipy.interpolate import UnivariateSpline
import warnings; warnings.simplefilter('ignore')
from matplotlib import pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.ticker as tkr
import matplotlib as mpl
mpl.interactive(True)
from windrose import WindroseAxes, plot_windrose
import cmocean
import gsw
from pyrsktools import RSK as RSK
sys.path.append(os.path.abspath('../'))
from functions import IMS_toolbox as IMS

year = '2026'
pathroot = os.path.abspath('../../')
