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
        print(data)
        df = RenderCSV()
        
        flash('Good', 'success')
        return render_template("index.html", tables=[df.to_html(classes='data')], titles=df.columns.values)
    
    return render_template("index.html")

def RenderCSV():
    df = pd.read_csv('./static/output/output.csv', encoding= 'euc-kr')
    return df

if __name__ == "__main__":              
    app.run(host="localhost", port=5000, use_reloader=False, debug=True)
