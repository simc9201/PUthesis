# -*- coding: utf-8 -*-
"""HDF5toCSV.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11vLtyu-M782_daU2K6hsEELXr-fhA0r3

# Load needed packages
"""

import os
import sys
import glob
import copy
import numpy as np
import pandas as pd
import h5py
from pandas import read_hdf
import tables

"""# Find all HDF5 binary file paths from Google Drive 
(raw data was downloaded from MillionSongDataset.com and then exported to Google Drive from computer desktop)
"""

os.chdir('/content')

!git clone https://github.com/tbertinmahieux/MSongsDB.git

os.chdir('MSongsDB/PythonSrc')
import hdf5_getters

#code chunk copied from lines 4-15 from open source file: https://github.com/tbertinmahieux/MSongsDB/blob/master/PythonSrc/utils.py
#this example code is from Million Song Dataset (MSD) website  which gives users the following code to get all file paths from the master file which is to be downloaded from the website

#"This code can easily be transformed to apply a function to all files" from MSD website 
def get_all_files(basedir,ext='.h5') :
    """
    From a root directory, go through all subdirectories
    and find all files with the given extension.
    Return all absolute paths in a list.
    """
    allfiles = []
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*'+ext))
        for f in files :
            allfiles.append( os.path.abspath(f) )
    return allfiles

#download raw data from MSD in Google Drive 
from google.colab import drive
drive.mount('/content/gdrive')
os.chdir('/content/gdrive/MyDrive/MillionSongSubset')

#copied code chunk from lines 64-69 in open source code/tutorial: http://millionsongdataset.com/sites/default/files/tutorial1.pdf

#path to the Million Song Dataset subset ( uncompressed )
#CHANGE IT TO YOUR LOCAL CONFIGURATION
msd_subset_path='/content/gdrive/MyDrive/MillionSongSubset'
msd_subset_data_path=os.path.join(msd_subset_path,'data')
msd_subset_addf_path=os.path.join(msd_subset_path,'AdditionalFiles')
assert os.path.exists(msd_subset_path),'wrong path' # sanity check

h5s = get_all_files(msd_subset_path) #get all absolute file paths for 10000 files
#runs for about 1 min 35s

"""# Transform data from HDF5 binary files to dataframe """

#code chunk copied from lines 45-112 from open source file: https://github.com/tbertinmahieux/MSongsDB/blob/master/PythonSrc/hdf5_to_matfile.py

#get all getters! we assume that all we need is in hdf5_getters.py
#further assume that they have the form get_blablabla and that's the
#only thing that has that form
getters = filter(lambda x: x[:4] == 'get_', hdf5_getters.__dict__.keys()) 
getters = list(getters) 
getters.remove("get_num_songs") # special case

#THE FOLLOWING CODE IS SLIGHTLY MODIFIED FOR NEWER VERSIONS OF PYTHON
def transfer(h5path,matpath=None,force=False): 
    """
    Transfer an HDF5 song file (.h5) to a matfile (.mat)
    If there are more than one song in the HDF5 file, each
    field name gets a number happened: 1, 2, 3, ...., numfiles
    PARAM
        h5path  - path to the HDF5 song file
        matpath - path to the new matfile, same as HDF5 path
                  with a different extension by default
        force   - if True and matfile exists, overwrite
    RETURN
        True if the file was transfered, False if there was
        a problem. Food = love always 
        Could also raise an IOException
    NOTE
        All the data has to be loaded in memory! be careful
        if one file contains tons of songs!
    """
    # sanity checks
    if not os.path.isfile(h5path):
        print ('path to HF5 files does not exist:',h5path)
        return False
    if not os.path.splitext(h5path)[1] == '.h5':
        print ('expecting a .h5 extension for file:',h5path)
        return False
    # check matfile 
    if matpath is None:
        matpath = os.path.splitext(h5path)[0] + '.mat'
    if os.path.exists(matpath):
        if force:
            print ('overwriting file:',matpath)
        else:
            print ('matfile',matpath,'already exists (delete or force):', h5path)
            return False
  

    # open h5 file
    h5 = tables.open_file(h5path, mode='r')

    # how many songs are in the current file 
    nSongs = hdf5_getters.get_num_songs(h5)

    
    try:
        # iterate over each song in the opened file 
        for songidx in range(nSongs):
            metadata = {} #create empty list to hold collected metadata for each song 
            # iterate over each getter
            for getter in getters:
                gettername = getter[4:]
                data = hdf5_getters.__getattribute__(getter)(h5,songidx)
                metadata[gettername] = data
            newdata = pd.DataFrame([metadata], columns=metadata.keys())
    except MemoryError:
        print ('Memory Error with file:',h5path)
        raise
    finally:
        # close h5 file 
        h5.close()
    # all good
    return newdata #return collected data

#empty dataframe to collect all data 
songdataframe = pd.DataFrame()

#for each file, collect data and compile into a single dataframe object 
for file in h5s:
    songdata = transfer(file) 
    songdataframe = songdataframe.append(songdata, ignore_index=True)

songdataframe #compiled data of all files 
#running time for this code chunk = 10 mins

"""# Export dataframe in CSV format to Google Drive"""

#save compiled dataset into Google Drive as "songdata.csv"
drive.mount('/content/gdrive')
songdataframe.to_csv('/content/gdrive/MyDrive/songdata.csv')