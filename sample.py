from flask import Flask, render_template, request, flash, redirect, url_for
import pandas as pd

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/GetData', methods = ['POST', 'GET'])
def GetData():
    if request.method == 'POST':
        data = request.form
        if int(data['means']) is 1:
            df = RenderCSV('simhash')
            means = 1
        elif int(data['means']) is 2:
            df = RenderCSV('noise')
            means = 2
        else:
            return redirect(url_for('home'))

        return render_template("index.html", tables=[df.to_html(classes='data')], titles=df.columns.values, means=means, enable=1)
    
    return render_template("index.html")

def RenderCSV(means):
    where = './static/input/' + means + '/result.csv'
    data = pd.read_csv(where, encoding='euc-kr')
    data.index += 1
    data.columns.names = ['번호']
    return data

if __name__ == "__main__":              
    app.run(host="localhost", port=5000, use_reloader=False, debug=True)
