from cloudant.client import Cloudant
from cloudant.query import Query
from flask import Flask, jsonify, request
import atexit

#Add your Cloudant service credentials here
cloudant_username = 'b4bd68da-5f3f-4235-aea3-59e0ce226a88-bluemix'
cloudant_api_key = 'HzFd3MvvVw4Hp3DaH0uXjsAJGWlj4eqOJNT1ZM2W80z6'
cloudant_url = 'https://b4bd68da-5f3f-4235-aea3-59e0ce226a88-bluemix.cloudantnosqldb.appdomain.cloud'
client = Cloudant.iam(cloudant_username, cloudant_api_key, connect=True, url=cloudant_url)

session = client.session()
print('Databases:', client.all_dbs())

db = client['reviews']

app = Flask(__name__)

@app.route('/api/review', methods=['GET', 'POST'])
def handle_reviews():
    if request.method == 'GET':
        dealership_id = request.args.get('dealerId')

        if dealership_id is None:
            return jsonify({"error": "Missing 'id' parameter in the URL"}), 400

        try:
            dealership_id = int(dealership_id)
        except ValueError:
            return jsonify({"error": "'id' parameter must be an integer"}), 400

        selector = {
            'dealership': dealership_id
        }

        result = db.get_query_result(selector)

        data_list = []
        for doc in result:
            data_list.append(doc)

        return jsonify(data_list)
    else:
        if not request.json:
            abort(400, description='Invalid JSON data')

        review_data = request.json['review']

        required_fields = ['id', 'name', 'dealership', 'review', 'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']
        for field in required_fields:
            if field not in review_data:
                abort(400, description=f'Missing required field: {field}')

        db.create_document(review_data)

        return jsonify({"message": "Review posted successfully"}), 201


if __name__ == '__main__':
    app.run(debug=True)
