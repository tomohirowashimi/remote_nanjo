from flask import Flask, render_template, request, session
import pandas as pd
import json
import plotly
import plotly.express as px
import datetime
import os

app = Flask(__name__)

key = os.urandom(21)
app.secret_key = key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/monitor', methods=['POST'])
def monitor():
    date = request.form['date']
    select_date = date
    session['select_date'] = date

    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    date_start = date.replace(hour=8, minute=0, second=0)
    date_end = date_start + datetime.timedelta(days=1)

    df = pd.read_pickle('color_log.pkl')
#    df['time_1'] = pd.to_datetime(df['time_1'])
#    df['time_2'] = pd.to_datetime(df['time_2'])

    df_refine = df[df['time_1'] > date_start]
    df_refine = df_refine[df_refine['time_1'] < date_end]

    print(df_refine.iloc[:, 2])

    product_time = float(df_refine.iloc[:, 2].sum())
    product_rate = round((product_time / 24 / 60 / 60) * 100, 1)
    session['product_rate'] = product_rate

    fig = px.timeline(df_refine, x_start='time_1', x_end='time_2', y='color', color='color')
    color_discrete_map={'green':'#0000ff', 'yellow':'#000000', 'red':'#ff0000', 'off':'#696969'},
    category_orders={'color':['green','yellow','red','off']}

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('monitor.html', graphJSON=graphJSON, select_date=select_date, product_rate=product_rate)

if __name__ == '__main__':
    app.run(debug=True)
