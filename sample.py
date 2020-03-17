from flask import Flask, render_template, request, flash, redirect, url_for

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

        

        flash('Good', 'success') 
        return redirect(url_for('home'))
    
    return render_template("index.html")
 
if __name__ == "__main__":              
    app.run(host="localhost", port=5000, use_reloader=False, debug=True)
