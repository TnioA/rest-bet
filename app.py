# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import json
import os
import collections

app = Flask(__name__)
CORS(app)

@app.route('/api/numbers', methods=['GET'])
def umbers():
    html_doc = requests.get("http://www.resultadosmegasena.com.br/resultados-anteriores")
    soup = BeautifulSoup(html_doc.text, "html.parser")
    data = []
    for dataBox in soup.find_all("tr", class_="rstable_td"):
        itens = dataBox.find_all("td")
        date = itens[0].text.strip()
        info = itens[1].text.strip().split("\t\t\t\t\t\t")
        concurse = info[0].replace("\n", "").strip()
        winners = info[1].replace("Ganhadores:", "").strip()
        value = info[2].replace("Prêmio:", "").strip()
        numbers = [item.text for item in itens[2].find_all("div")]

        data.append({ 
            'date': date,
            'concurse': concurse,
            'winners': winners,
            'value': value,
            'numbers': numbers
        })
        

    return jsonify({'results': data})


@app.route('/api/bestnumber', methods=['GET'])
def BestNumber():
    html_doc = requests.get("http://www.resultadosmegasena.com.br/resultados-anteriores")
    soup = BeautifulSoup(html_doc.text, "html.parser")
    data = []
    number_list = []
    object_list = {}
    final_list = []
    for dataBox in soup.find_all("tr", class_="rstable_td"):
        itens = dataBox.find_all("td")
        number = [int(item.text) for item in itens[2].find_all("div")]
        number_list.extend(number)

    for item in range(1, 60):
        object_list.update({
            str(item): number_list.count(item)
        })
        
    sorted_list = sorted(
        object_list.items(),
        key = lambda x: x[1],
        reverse = True
    )

    for i in range(0, 5):
        final_list.append(i)
    
    return jsonify({'results': final_list})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
