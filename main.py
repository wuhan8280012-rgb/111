import tushare as ts

import pandas as pd

import numpy as np

import os

import matplotlib.pyplot as plt

from dotenv import load_dotenv



# 1. 环境配置：自动加载 .env 文件中的 TOKEN

load_dotenv()

token = os.getenv('TUSHARE_TOKEN')

ts.set_token(token)

pro = ts.pro_api()



def run_wyckoff_analysis_flexible(ts_code, target_days=500):

    """

    ts_code: 股票代码变量，现在它从外部传入

    """

    print(f"🚀 开始处理股票: {ts_code} ...")

    

    # [此处保持您原来的逻辑代码不变...]

    df_raw = pro.daily(ts_code=ts_code, count=1000)

    if df_raw.empty:

        print(f"❌ 未获取到 {ts_code} 的任何数据。")

        return



    df = df_raw.sort_values('trade_date').reset_index(drop=True)

    actual_total_days = len(df)

    display_days = min(actual_total_days, target_days)

    

    df['MA50'] = df['close'].rolling(window=50).mean()

    df['MA200'] = df['close'].rolling(window=200).mean()

    df['vol_ma20'] = df['vol'].rolling(window=20).mean()



    df_final = df.tail(display_days).copy()



    # 存储 CSV

    csv_df = df_final.copy()

    csv_df['time'] = pd.to_datetime(csv_df['trade_date']).apply(lambda x: int(x.timestamp()))

    csv_export = csv_df[['time', 'open', 'high', 'low', 'close', 'vol']].rename(columns={'vol': 'Volume'})

    filename = f"{ts_code.replace('.', '_')}_data.csv"

    csv_export.to_csv(filename, index=False)

    

    # 威科夫事件识别逻辑

    events = []

    closes = df_final['close'].values

    vols = df_final['vol'].values

    vma = df_final['vol_ma20'].values

    lows = df_final['low'].values

    highs = df_final['high'].values

    dates = df_final['trade_date'].values



    for i in range(20, len(df_final)):

        lookback = lows[max(0, i-50):i]

        if len(lookback) > 0 and lows[i] < min(lookback) and closes[i] > min(lookback):

            events.append({'date': dates[i], 'price': lows[i], 'label': 'Spring'})

        lookback_h = highs[max(0, i-20):i]

        if len(lookback_h) > 0 and closes[i] > max(lookback_h) and vols[i] > vma[i] * 1.3:

            events.append({'date': dates[i], 'price': highs[i], 'label': 'SOS'})



    # 绘图逻辑

    plt.figure(figsize=(14, 7))

    plt.plot(pd.to_datetime(df_final['trade_date']), closes, color='black', label='Price', linewidth=1)

    plt.plot(pd.to_datetime(df_final['trade_date']), df_final['MA50'], label='MA50', alpha=0.7)

    if not df_final['MA200'].isnull().all():

        plt.plot(pd.to_datetime(df_final['trade_date']), df_final['MA200'], label='MA200', color='red')

    

    for e in events:

        plt.annotate(e['label'], (pd.to_datetime(e['date']), e['price']), 

                     xytext=(0, -15), textcoords='offset points', 

                     arrowprops=dict(arrowstyle='->', color='blue'),

                     ha='center', fontsize=9, color='blue')



    plt.title(f"Wyckoff Analysis: {ts_code} (Last {display_days} Days)")

    plt.legend()

    plt.grid(True, alpha=0.2)

    plt.show()



# ==========================================

# 在这里修改您想要分析的股票代码

# ==========================================

if __name__ == "__main__":

    MY_STOCK = '300773.SZ'  # 您只需修改这一行即可分析不同股票

    run_wyckoff_analysis_flexible(MY_STOCK)

