# -*- coding: utf-8 -*-
from http import HTTPStatus
from flask import Flask
from flask_restx import Resource, Api, fields
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
CORS(app)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}
api = Api(
    app, 
    version='1.0', 
    title='Rest Bet API', 
    description='Serviço para retorno de dados da mega-sena.',
    authorizations=authorizations
)

person_fields = api.model('NumbersResponseItem', {
    'date': fields.DateTime(dt_format='rfc822', example= "7/06/2023"),
    'concurse': fields.String(example="231"),
    'winners': fields.String(example="1"),
    'value': fields.String(example="1.123,00"),
    'numbers': fields.List(fields.String(example="1"))
})

numbers = api.model('NumbersResponse', {
    'results': fields.List(fields.Nested(person_fields))
})

best_number_response_model = api.model('BestNumberResponse', {
    'results': fields.List(fields.String(example="1"))
})

bets = api.namespace('bets', ordered=True)

@bets.route('/numbers')
@bets.response(int(HTTPStatus.OK), 'Returned the content list', numbers)
@bets.response(int(HTTPStatus.BAD_REQUEST), 'Validation errors')
class Numbers(Resource):
    # @api.expect(response_fields, validate=True)
    # @api.marshal_with(response_fields, code=200)
    # @api.marshal_list_with(person_fields, envelope='results')
    def get(self):
        """
        Retorna a lista de jogos da mega-sena
        """
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
@bets.response(int(HTTPStatus.OK), 'Returned the content list', best_number_response_model)
@bets.response(int(HTTPStatus.BAD_REQUEST), 'Validation errors')
class BestNumber(Resource):
    def get(self):
        """
        Retorna os 6 melhores números para jogo
        """
        html_doc = requests.get("http://www.resultadosmegasena.com.br/resultados-anteriores")
        soup = BeautifulSoup(html_doc.text, "html.parser")
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