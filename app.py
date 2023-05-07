# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask_restx import Resource, Api
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import json
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

api = Api(app, version='1.0', title='Rest Bet API', description='Serviço para retorno de dados da mega-sena.')
bets = api.namespace('bets', ordered=True)

@bets.route('/numbers')
@bets.response(200, 'Returned the content list')
@bets.response(400, 'Validation errors')
class Numbers(Resource):
    def get(self):
        html_doc = requests.get("http://www.resultadosmegasena.com.br/resultados-anteriores")
        soup = BeautifulSoup(html_doc.text, "html.parser")
        data = []
        for dataBox in soup.find_all("tr", class_="rstable_td"):
            itens = dataBox.find_all("td")
            date = itens[0].text.strip()
            info = itens[1].text.strip().split("\t\t\t\t\t\t")
            concurse = info[0].replace("\n", "").strip()
            winners = info[1].replace("Ganhadores:", "").strip()
            #value = info[2].replace("Prêmio:", "").strip()
            value = ''
            numbers = [item.text for item in itens[2].find_all("div")]

            data.append({ 
                'date': date,
                'concurse': concurse,
                'winners': winners,
                'value': value,
                'numbers': numbers
            })      

        return {'results': data}

@bets.route('/bestnumber')
@bets.response(200, 'Returned the content list')
@bets.response(400, 'Validation errors')
class BestNumber(Resource):
    def get(self):
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

        for i in range(0, 6):
            final_list.append(sorted_list[i][0])
        
        return {'results': final_list}

if __name__ == '__main__':
	host = os.environ.get('HOST', '0.0.0.0')
	port = int(os.environ.get('PORT', 5000))
	env = os.environ.get('ENV')

	app.run(host=host, port=port, debug=(not (env == 'PRODUCTION')), threaded=True)