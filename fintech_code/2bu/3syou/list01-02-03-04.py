# ���X�g1���烊�X�g4���܂Ƃ߂��\�[�X�R�[�h�ł�

import datetime
import zipfile
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

def __gaincap_datetime_parser(str_dt):
    try:
        return datetime.strptime(str_dt[:-3],'%Y-%m-%d %H:%M:%S.%f')
    except Exception:
        return datetime.strptime(str_dt,'%Y-%m-%d %H:%M:%S')


import requests
import pandas as pd
from datetime import datetime, date

def download_gaincap(filename,path):
    tsdflg=True
    url_gc_path = "http://ratedata.gaincapital.com/"

    for i in range(len(filename)):

        url_file_path = filename[i]
        url_date_path="2017/01 January/"
        url =  url_gc_path + url_date_path+url_file_path
        res = requests.get(url)


        hd_path = path + url_file_path
        f = open(hd_path, 'wb')
        f.write(res.content)
        f.close()


        file_csv = "USD_JPY_Week%d.csv" %(i+1)
        try:
            f = zipfile.ZipFile(hd_path).open(file_csv)
            dfx = pd.read_csv(f, index_col=3, \
                date_parser=__gaincap_datetime_parser)[['RateBid']]
            f.close()
            if tsdflg:
                tsd=dfx.copy()
                tsdflg=False
            else:
                tsd=tsd.append(dfx)
        except Exception:
            print("Error open zip file %s. The error is" %filename[i])
    return tsd

if __name__ == '__main__':
    filename0=["USD_JPY_Week1.zip",
             "USD_JPY_Week2.zip",
             "USD_JPY_Week3.zip",
             "USD_JPY_Week4.zip",
             "USD_JPY_Week5.zip"]
    # �d�v�I�I�I
    # ���s�̍ۂɂ͈ȉ��̃p�X��K�؂ɏC�����Ă�������
    path0="C:\\users\\moriya\\documents\\Database\\gaincap\\"
    ts=download_gaincap(filename0,path0)
    print("end----------------------------------",len(ts))

    tsd=ts['RateBid'].resample('min').ohlc()
    print(len(tsd))
    print(tsd.head(1))

    n=30
    rw_nr,rwc_nr,rwct_nr,j=np.zeros(4)
    alpha=0.1

    lntsd=np.log(tsd.close).dropna()
    for i in range(0,len(lntsd),n):
        y=lntsd.iloc[i:i+n]
        rw=sm.tsa.adfuller(y,regression='nc')[1]
        rwc=sm.tsa.adfuller(y,regression='c')[1]
        rwct=sm.tsa.adfuller(y,regression='ct')[1]
        if rw<alpha:
            rw_nr+=1
        if rwc<alpha:
            rwc_nr+=1
        if rwct<alpha:
            rwct_nr+=1
        j+=1

    print("���Ԃ̐�",j)
    print("�h���t�g����: ���p���Ԃ̊���",rw_nr/j)
    print("�h���t�g�t��: ���p���Ԃ̊���",rwc_nr/j)
    print("�h���t�g�{���ԃg�����h�t��: ���p���Ԃ̊���",rwct_nr/j)

    n=30
    rwct_nr,j=np.zeros(2)
    alpha=0.1
    a=[]

    for i in range(0,len(lntsd),n):
        y=lntsd.iloc[i:i+n]
        rwct=sm.tsa.adfuller(y,regression='ct',maxlag=0)[1]
        if rwct<alpha:
            x=y.shift(1).dropna()          # �����ϐ��̍쐬
            x=sm.add_constant(x).dropna()  # �ؕЂ̍쐬
            yy=y.iloc[1:].dropna()         # ������ϐ��̍쐬
            x['time']=range(len(yy))       # ���ԃg�����h�̍쐬
            results=sm.OLS(yy,x).fit()     # ��A�̍œK��
            a.append(results.params[1])
            rwct_nr+=1
        j+=1

    print("���Ԃ̐�",j)
    print("�h���t�g�{���ԃg�����h�t��: ���p���Ԃ̊���",rwct_nr/j)
    plt.plot(a)