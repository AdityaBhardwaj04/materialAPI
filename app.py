from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import json_util

app = Flask(__name__)
mongo_uri = "mongodb://localhost:27017/"
db_name = "materials_database"
collection_name = "materials_data"
client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]


@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Materials Informatics API!"


@app.route('/materials', methods=['GET'])
def get_materials():
    # Get the query parameter for formula_pretty, if provided
    formula = request.args.get('formula_pretty')

    # Query the collection based on the formula if provided
    if formula:
        materials = collection.find({"formula_pretty": formula})
    else:
        materials = collection.find()

    documents = list(materials)
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return {"materials": json_util.dumps(documents)}


@app.route('/materials/<mpid>', methods=['GET'])
def search_by_mpid(mpid):
    document = collection.find_one({"material_id.string": mpid})
    if document:
        document["_id"] = str(document["_id"])
        return {"material": json_util.dumps(document)}
    else:
        return {"error": "Material not found!"}


@app.route('/materials/<formula>', methods=['GET'])
def search_by_formula(formula):
    if formula:
        materials = collection.find({"formula_pretty": formula})
        documents = [json_util.dumps(doc) for doc in materials]
        return {"materials": documents}
    else:
        return {"error": "Please provide a formula in the URL path for the search."}


@app.route('/materials/fields', methods=['POST'])
def get_materials_with_fields():
    if request.content_type != 'application/json':
        return {"error": "Unsupported Media Type. Content-Type must be application/json"}, 415

    try:
        data = request.get_json()
    except Exception as e:
        return {"error": f"Invalid JSON data: {str(e)}"}, 400

    formula = data.get('formula_pretty')
    fields = data.get('fields')
    filter_criteria = data.get('filter', {})

    if not fields:
        return {"error": "Please provide a list of fields to retrieve."}, 400

    projection = {field: 1 for field in fields}
    projection["_id"] = 0  # Exclude the MongoDB _id field from the result

    query = filter_criteria
    if formula:
        query['formula_pretty'] = formula

    materials = collection.find(query, projection)
    documents = list(materials)

    for doc in documents:
        doc["_id"] = str(doc["_id"])

    return {"materials": json_util.dumps(documents)}


if __name__ == '__main__':
    app.run(debug=True)
