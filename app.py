from flask import Flask, render_template
import pandas as pd
from datetime import datetime
import csv
import requests


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60


def data(symbol):
    time_frame = '1h'
    url = f"https://public.coindcx.com/market_data/candles?pair=B-{symbol}&interval={time_frame}"

    temp_data = requests.get(url)
    response = temp_data.json()
    response_list = []

    for i in response:
        response_list.append((i['time']/1000, i['open'], i['high'], i['low'], i['close'], i['volume']))

    with open(f'History/{symbol}.csv', 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        for i in response_list:
            writer.writerow(i)

    file.close()


def support(df1, l1, n1, n2):
    for i in range(l1-n1+1, l1+1):
        if df1.Low[i] > df1.Low[i - 1]:
            return False
    for i in range(l1 + 1, l1 + n2 + 1):
        if df1.Low[i] < df1.Low[i - 1]:
            return False
    return True


def resistance(df1, l1, n1, n2):
    for i in range(l1-n1+1, l1+1):
        if df1.High[i] < df1.High[i - 1]:
            return False
    for i in range(l1 + 1, l1 + n2 + 1):
        if df1.High[i] > df1.High[i - 1]:
            return False
    return True


def calc_main(sym):
    data(sym)
    df = pd.read_csv(f'History/{sym}.csv')
    sup = []
    res = []
    n1 = 3
    n2 = 2

    for row in range(n1, len(df) - n2 - 5):
        if support(df, row, n1, n2) is True:
            sup.append((df['Low'][row], datetime.fromtimestamp(int(df['Time'][row])).strftime('%d/%m/%Y %H:%M:%S')))
        if resistance(df, row, n1, n2) is True:
            res.append((df['High'][row], datetime.fromtimestamp(int(df['Time'][row])).strftime('%d/%m/%Y %H:%M:%S')))

    return sup[:3], res[:3]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/btcusdt')
def btcusdt():
    calc_list = calc_main('BTC_USDT')
    support_list = calc_list[0]
    resistance_list = calc_list[1]
    return render_template('btcusdt.html', support=support_list, resistance=resistance_list)


@app.route('/ethusdt')
def ethusdt():
    calc_list = calc_main('ETH_USDT')
    support_list = calc_list[0]
    resistance_list = calc_list[1]
    return render_template('ethusdt.html', support=support_list, resistance=resistance_list)


if __name__ == '__main__':
    app.run(debug=False)
