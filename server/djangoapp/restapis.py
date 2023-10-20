import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    response = None
    try:
        # Call get method of requests library with URL and parameters
        api_key = kwargs.get('api_key')
        if api_key:
            params = dict()
            params["version"] = kwargs["version"]
            params["text"] = kwargs["text"]
            params["features"] = kwargs["features"]

            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
            print(response.url)
        else:
            params = dict()
            for key, value in kwargs.items():
                params[key] = value
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'})
    except Exception as err:
        # If any error occurs
        print(err)
        print("Network exception occurred")

    if response:
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    return ''

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(json_payload)
    print(kwargs)
    print("POST from {} ".format(url))
    response = None
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except Exception as err:
        print(err)
        print("Network exception occurred")

    if response:
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    return ''

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    dealerId = kwargs.get('dealerId')
    state = kwargs.get('state')
    if dealerId:
        json_result = get_request(url, id=dealerId)
    elif state:
        json_result = get_request(url, state=state)
    else:
        json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


def get_dealer_by_id(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, id=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


def get_dealers_by_state(url, state):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, state=state)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        for review in json_result:
            sentiment = analyze_review_sentiments(review['review'])
            review_obj = DealerReview(dealership=review['dealership'],
            name=review['name'], purchase=review['purchase'],
            review=review['review'], purchase_date=review['purchase_date'],
            car_make=review['car_make'], car_model=review['car_model'],
            car_year=review['car_year'], sentiment=sentiment, id=review['id'])
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    url = 'https://api.jp-tok.natural-language-understanding.watson.cloud.ibm.com/instances/e58cf71e-99e8-4eaa-9d19-1619db4e7fed/v1/analyze'
    api_key = 'D9t5wdgIFLkBONKPcCmRmYyPmD5MIhA7zgb9GyXsBV-R'
    version = '2022-04-07'
    features = ['sentiment']
    json_result = get_request(url, api_key=api_key, version=version,
    features=features, text=text+"hello hello hello")
    if json_result:
        return json_result['sentiment']['document']['label']
    return ''

    # url = 'https://api.jp-tok.natural-language-understanding.watson.cloud.ibm.com/instances/e58cf71e-99e8-4eaa-9d19-1619db4e7fed'
    # api_key = "D9t5wdgIFLkBONKPcCmRmYyPmD5MIhA7zgb9GyXsBV-R"
    # authenticator = IAMAuthenticator(api_key)
    # natural_language_understanding = NaturalLanguageUnderstandingV1(version='2022-04-07',authenticator=authenticator)
    # natural_language_understanding.set_service_url(url)
    # response = natural_language_understanding.analyze( text=text+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result()
    # label=json.dumps(response, indent=2)
    # label = response['sentiment']['document']['label']
    # return(label)
