from flask import Flask, render_template, request, redirect, url_for, send_file
import boleto_processor2
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    pasta_boletos = request.form['pasta_boletos']
    boletos = boleto_processor2.processar_boletos(pasta_boletos)
    boleto_processor2.exportar_csv(boletos, 'boletos.csv')
    return render_template('resultado2.html', boletos=boletos)

@app.route('/download')
def download():
    return send_file('boletos.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
