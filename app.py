from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, url_for, request, redirect
import jsonify
import json
import re
app = Flask(__name__)


@app.route("/getEs/<query>")
def get_es(query, category, omited):
    es = Elasticsearch(['http://localhost:9200'], request_timeout=3600)

    sort = [
        {
            "selling_price": {"order": "asc"}
        }
    ]

    query = {
        "bool": {
            "must":     [{"match": {"product_name": query}}],

            "should": [
                # {
                #     "match": {
                #         "product_name": {
                #             "query": query,
                #             "boost": 5
                #         }
                #     }
                # }
                # },
                {
                    "match": {
                        "about_product": {
                            "query": query,
                            "boost": 0.5
                        }
                    }
                }
            ]
        }
    }

    data = es.search(index='amazon_products', query=query,
                     size=20, sort=sort)
    address_data = data['hits']['hits']
    print(data['hits'])
    address_list = []
    for item in address_data:
        address_list.append(
            {'product_name': item['_source']['product_name'], 'category': item['_source']['category'], 'about_product': item['_source']['about_product'], 'selling_price': item['_source']['selling_price'], 'image': item['_source']['image']})
    new_data = json.dumps(address_list)

    if category != "":
        sortList = []
        for item in address_list:
            if category in item['category']:
                sortList.append(item)
        return sortList
    if omited != "":
        sortList = []
        for item in address_list:
            if omited not in item['category']:
                sortList.append(item)
        return sortList
    if category == '' and omited == '':
        return address_list


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'GET':
        return render_template('index.html')
    else:
        query = request.form['content']
        category = request.form['category']
        omited = request.form['omited']

        tasks = get_es(query, category, omited)

        return render_template('index.html', tasks=tasks)


if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=True)
