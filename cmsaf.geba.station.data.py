#!/usr/bin/env python
"""
========
Ctang, A map of mean max and min of ensembles
        from CMSAF AFR-44, in Southern Africa
        Data was restored on titan
========
"""
import pdb
import math
import subprocess
import datetime
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from matplotlib.ticker import AutoMinorLocator
from matplotlib.dates import YearLocator,MonthLocator,DateFormatter,drange
from mpl_toolkits.basemap import Basemap , addcyclic
import textwrap

# to load my functions
import sys 
sys.path.append('/Users/ctang/Code/Python/')
import ctang

#================================================== Definitions

N_model = 1
VAR ='rsds' 
LINE=423

OUTPUT='CMSAF.GEBA.station.data'
#=================================================== reading data
# reading CMSAF

obs='cmsaf.rsds.csv'
Dir='/Users/ctang/climate/GLOBALDATA/OBSDATA/CM_SAF/validation.CM_SAF.SA/'
CMSAFfile=Dir+obs

CMSAF = np.array(pd.read_csv(CMSAFfile,index_col=False))
#ID,StaID,year,Jan,Feb,Mar,Api,May,Jun,July,Aug,Sep,Oct,Nov,Dec

CMSAF_Data = CMSAF[:,3:15]
STATION=CMSAF[:,1]

print CMSAF_Data.shape # (462,12)

#=================================================== 
# reading GEBA

GEBA_flag='flag.mon.GEBA.csv'
GEBA_rsds='rsds.mon.GEBA.csv'

print Dir+GEBA_flag

GEBA_FLAG = np.array(pd.read_csv(Dir+GEBA_flag,index_col=False)) # (462,18)
GEBA_RSDS = np.array(pd.read_csv(Dir+GEBA_rsds,index_col=False))
#StaID,obsID,year,Jan,Feb,Mar,Api,May,Jun,July,Aug,Sep,Oct,Nov,Dec,sta,country,ID

print GEBA_FLAG.shape
#=================================================== 
# reading station

stationfile = 'cmsaf.vld.sta.mab.csv'
station = np.array(pd.read_csv(Dir+stationfile,index_col=False))
#NO,MAB,NO,sta_ID,lat,lon,N_month,NO,sta_ID,lat,lon,N_month,sta_ID,altitude

station_id = station[:,3]
lats = station[:,4]
lons = station[:,5]
altitude = station[:,13]
print station.shape

# get station_name:
station_name=[ 't' for i in range(len(station_id))]
for i in range(len(station_id)):
    for j in range(LINE):
        if GEBA_FLAG[j,0] == station_id[i]:
            station_name[i] = str(GEBA_FLAG[j,16])+"@"+str(GEBA_FLAG[j,17])
print station_name

#--------------------------------------------------- 
# good data: 1
# bad data: -1
# missing data: 0

def justice(flag):
    jjj=90908                     # default
    s=list(str(int(flag)))
    if len(s) > 1:
        if s[4] == '8':
            if s[3] == '7' or s[3] == '8' :
                if s[2] == '5' or s[2] == '7' or s[2] == '8':
                    if s[1] == '5':
                        if s[0] == '5':
                            jjj = 1
                        else:
                            jjj = -1
                    else:
                        jjj = -1
                else:
                    jjj = -1
            else:
                jjj = -1
        else:
            jjj = -1
    else:                             # single flag 0 or 8
        if s[0] > 0:
            jjj = -1
        else:
            jjj = 0
    return jjj 
#--------------------------------------------------- 

#--------------------------------------------------- 
# functino to plot GEBA vs OBS
def VS(x,x1,y,i):

    # rename the x, x1, y and convert to np.array
    rsds=np.zeros((x.shape[0],x.shape[1]))
    flag=np.zeros((x.shape[0],x.shape[1]))
    cmsaf=np.zeros((x.shape[0],x.shape[1]))

    for k in range(x.shape[0]):
        for j in range(x.shape[1]):
            rsds[k,j]=x[k,j]
            flag[k,j]=x1[k,j]
            cmsaf[k,j]=y[k,j]

    # to get x , y, and date for plot
    x_plot=[]
    y_plot=[]
    date_plot=[]

    years = x[:,0]
    for j in range(len(years)):
        year = int(years[j]-1)
        dates=pd.date_range((pd.datetime(year,12,1)\
            +pd.DateOffset(months=1)), periods=12, freq='MS')

        # print years[j],dates

        # remove bad data: justice function
        rsds_plot=[]
        cmsaf_plot=[]
        date=[]

        for k in range(1,13,1):
            if cmsaf[j,k] > 0:              # rm missing data 1988-12
                if justice(flag[j,k]) == 1:
                    rsds_plot.append(rsds[j,k])
                    cmsaf_plot.append(cmsaf[j,k])
                    date.append(dates[k-1])
                else:
                    a=000
            else:
                print k,dates[k-1],"removing missing value 1988-12"

        x_plot+=rsds_plot
        y_plot+=cmsaf_plot
        date_plot+=date

    geba=x_plot
    cmsaf=y_plot

    x=geba
    y=cmsaf
    print "==========="
    print x,y

    # no. of records
    N_mon=len(list(x))

    # mean bias of records
    bias=np.array([y[l]-x[l] for l in range(len(x))])
    meanbias=bias.mean()

    meanbias1=bias[bias<0].mean()
    meanbias2=bias[bias>0].mean()


    # mean absolute bias of records
    ab=np.array([np.abs(y[l]-x[l]) for l in range(len(x))])
    mab=ab.mean()

    # linear regression:
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

    # output sequence:
    # staID, N_mon, lat, lon, alt, sta_name, MeanBias, MAB,
    # slope, intercept, r_value, P_value, std_err

    output=[]
    output.append(int(station_id[i]))
    output.append(N_mon)
    output.append(float(format(lats[i],".2f")))
    output.append(float(format(lons[i],".2f")))
    output.append(int(altitude[i]))
    output.append(station_name[i])

    output.append(float(format(meanbias,'.2f')))
    output.append(float(format(meanbias1,'.2f')))
    output.append(float(format(meanbias2,'.2f')))
    output.append(float(format(mab,'.2f')))

    output.append(float(format(slope,'.2f')))
    output.append(float(format(intercept,'.2f')))
    output.append(float(format(r_value,'.2f')))
    output.append(float(format(p_value,'.2f')))
    output.append(float(format(std_err,'.2f')))

    output+=bias
    output+=ab


    return output
#--------------------------------------------------- 

#=================================================== plot by 21 models

def plot_array(title):
    COF=np.zeros((len(station_id),276))
    COF=[[]]

    for j in range(len(station_id)):
        sta=station_id[j]

        # prepare cm_saf
        CMSAF_array=CMSAF
        CMSAF_sta1=np.array(CMSAF_array[np.where(CMSAF_array[:,1]==sta)])
        CMSAF_sta=CMSAF_sta1[:,2:15]

        # prepare obs
        GEBA_PlotFlag1=np.array(GEBA_FLAG[np.where(GEBA_FLAG[:,0]==sta)])
        GEBA_PlotFlag=GEBA_PlotFlag1[:,2:15]

        GEBA_PlotRsds1=np.array(GEBA_RSDS[np.where(GEBA_RSDS[:,0]==sta)])
        GEBA_PlotRsds=GEBA_PlotRsds1[:,2:15]

        # check
        print("-------input:",j,sta,CMSAF_sta.shape,GEBA_PlotRsds.shape)

#=================================================== 
        # to send plot data
        COF.append(VS(\
            np.array(np.float32(GEBA_PlotRsds)),\
            np.array(np.float32(GEBA_PlotFlag)),\
            np.array(np.float32(CMSAF_sta)),\
            j))

#=================================================== save cof
    headers=['Sta_'+str(i+1) for i in range(len(station_id))]
    with open(OUTPUT+'.csv', 'w') as fp:
        # fp.write(','.join(headers) + '\n')
        np.savetxt(fp, COF, delimiter=" ", fmt="%s")
        # np.savetxt(fp, COF, '%5.2f', ',')
#=================================================== end plot by model
plot_array(station_name)
#=================================================== end
quit()
