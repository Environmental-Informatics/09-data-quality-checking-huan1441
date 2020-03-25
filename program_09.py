# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Author: Tao Huang (huan1441)
#
# Created: Mar 20, 2020
#
# Script: program_09.py
#
# Purpose: Script to check the dataset(DataQualityChecking.txt) for removing no data
#          values, gross errors, inconsistencies in variables, and range problems
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "Date", "Precip", "Max Temp", "Min Temp", "Wind Speed". Function
    returns the completed DataFrame, and a dictionary designed to contain all 
    missing value counts."""
    
    # define column names
    colNames = ['Date','Precip','Max Temp', 'Min Temp','Wind Speed']

    # open and read the file
    DataDF = pd.read_csv("DataQualityChecking.txt",header=None, names=colNames,  
                         delimiter=r"\s+",parse_dates=[0])
    DataDF = DataDF.set_index('Date')
    
    # define and initialize the missing data dictionary
    ReplacedValuesDF = pd.DataFrame(0.0, index=["1. No Data",
                                                "2. Gross Error",
                                                "3. Swapped",
                                                "4. Range Fail"], columns=colNames[1:])
     
    return( DataDF, ReplacedValuesDF )
 
def Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF ):
    """This check replaces the defined No Data value with the NumPy NaN value
    so that further analysis does not use the No Data values.  Function returns
    the modified DataFrame and a count of No Data values replaced."""

    # replace the defined No Data value (-999) with NaN

    DataDF[DataDF==-999]=np.nan

    # record the number of values replaced with NaN for each data type

    for i in range(DataDF.shape[1]):
        ReplacedValuesDF.iloc[0,i]= DataDF.iloc[:,i].isna().sum()

    return( DataDF, ReplacedValuesDF )
    
def Check02_GrossErrors( DataDF, ReplacedValuesDF ):
    """This function checks for gross errors, values well outside the expected 
    range, and removes them from the dataset.  The function returns modified 
    DataFrames with data the has passed, and counts of data that have not 
    passed the check."""
 
    # find the index of the gross errors for Precipitation and record the number
    # the threshold is 0 ≤ P ≤ 25

    index=(DataDF['Precip']<0) | (DataDF['Precip']>25)

    ReplacedValuesDF.iloc[1,0]= index.sum()

    # replace the gross errors with NaN

    DataDF['Precip'][index]=np.nan

    # find the index of the gross errors for air temperature and record the number
    # the threshold is -25≤ T ≤ 35

    for i in range(1,3):
        index=(DataDF.iloc[:,i]<-25) | (DataDF.iloc[:,i]>35)
        
        ReplacedValuesDF.iloc[1,i]= index.sum()
        
        #replaced the gross errors with NaN
        
        DataDF.iloc[:,i][index]=np.nan

    # find the index of the gross errors for wind speed and record the number
    # the threshold is 0 ≤ WS ≤ 10

    index=(DataDF['Wind Speed']<0) | (DataDF['Wind Speed']>10)

    ReplacedValuesDF.iloc[1,3]= index.sum()

    # replace the gross errors with NaN

    DataDF['Wind Speed'][index]=np.nan
       
    return( DataDF, ReplacedValuesDF )
    
def Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture is less than
    minimum air temperature, and swaps the values when found.  The function 
    returns modified DataFrames with data that has been fixed, and with counts 
    of how many times the fix has been applied."""
    
    # find the index where Max Temp is less then for Min Temp and record the number

    index=(DataDF['Max Temp']<DataDF['Min Temp'])

    ReplacedValuesDF.iloc[2,1]= index.sum()
    ReplacedValuesDF.iloc[2,2]= index.sum()

    # swap the wrong pair of Max Temp and Min Temp

    DataDF['Max Temp'][index],DataDF['Min Temp'][index]=\
                DataDF['Min Temp'][index],DataDF['Max Temp'][index]

    return( DataDF, ReplacedValuesDF )
    
def Check04_TmaxTminRange( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture minus 
    minimum air temperature exceeds a maximum range, and replaces both values 
    with NaNs when found.  The function returns modified DataFrames with data 
    that has been checked, and with counts of how many days of data have been 
    removed through the process."""
    
    # find the index where Max Temp - Min Temp > 25 and record the number

    index=(DataDF['Max Temp']-DataDF['Min Temp']>25)

    ReplacedValuesDF.iloc[3,1]= index.sum()
    ReplacedValuesDF.iloc[3,2]= index.sum()

    # replace the range exceedance values with NaN
    
    DataDF['Max Temp'][index]=np.nan
    DataDF['Min Temp'][index]=np.nan

    return( DataDF, ReplacedValuesDF )
    

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    fileName = "DataQualityChecking.txt"
    DataDF, ReplacedValuesDF = ReadData(fileName)
    
    print("\nRaw data.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF )
    
    print("\nMissing values removed.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check02_GrossErrors( DataDF, ReplacedValuesDF )
    
    print("\nCheck for gross errors complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF )
    
    print("\nCheck for swapped temperatures complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check04_TmaxTminRange( DataDF, ReplacedValuesDF )
    
    print("\nAll processing finished.....\n", DataDF.describe())
    print("\nFinal changed values counts.....\n", ReplacedValuesDF)

    # store the original dataframe into "RawDataDF"

    RawDataDF = ReadData(fileName)[0]

    # store the checked dataframe into "CheckDataDF"

    CheckDataDF = DataDF

    # plot each dataset before and after correction
    # figure of precipitation comparison

    RawDataDF['Precip'].plot(figsize=(12,6),style='r')
    CheckDataDF['Precip'].plot(style='g')
    plt.legend(["Orinigal","Checked"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Precipitation (mm)")

    plt.savefig("Precipitation Comparison.jpeg")

    plt.close()
    
    # figure of max air temperature comparison

    RawDataDF['Max Temp'].plot(figsize=(12,6),style='r')
    CheckDataDF['Max Temp'].plot(style='g')
    plt.legend(["Orinigal","Checked"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Max Air Temperature (°C)")

    plt.savefig("Max Air Temperature Comparison.jpeg")

    plt.close()

    # figure of min air temperature comparison

    RawDataDF['Min Temp'].plot(figsize=(12,6),style='r')
    CheckDataDF['Min Temp'].plot(style='g')
    plt.legend(["Orinigal","Checked"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Min Air Temperature (°C)")

    plt.savefig("Min Air Temperature Comparison.jpeg")

    plt.close()

    # figure of wind speed comparison

    RawDataDF['Wind Speed'].plot(figsize=(12,6),style='r')
    CheckDataDF['Wind Speed'].plot(style='g')
    plt.legend(["Orinigal","Checked"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Wind Speed (m/s)")

    plt.savefig("Wind Speed Comparison.jpeg")

    plt.close()

    # output data that has passed the quality check into a new file

    DataDF.to_csv('Checked_Data.txt', sep=" ", header=None)

    #  create a new output file,"Checked_Results.txt", to store the checked results

    ReplacedValuesDF.to_csv("Checked_Results.txt", sep="\t")
