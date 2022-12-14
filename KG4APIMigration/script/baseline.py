
import urllib.request
import json


def run_baseline():
    global data
    data = {
        "Inputs": {
            "input1":
                [
                    {
                        '1': "1",
                        '2': "1",
                        '3': "1",
                        '4': "1",
                        '5': "1",
                        '6': "1",
                        '7': "1",
                        '8': "1",
                        'output': "0",
                    }
                ],
        },
        "GlobalParameters": {
        }
    }
    body = str.encode(json.dumps(data))
    url = 'https://ussouthcentral.services.azureml.net/workspaces/fd769a98302c4c5d88faec13f23806f4/services/c8bd65a25e0f4b11b09a2f3226262d3a/execute?api-version=2.0&format=swagger'
    api_key = 'J9RWXmUb14jvpWnfewsQam15EfCiKv2vaT+apVfr3Jzf7IfWWsOLoMCkYg5YTFJM3Ha8Ri8lzDYjv5Mr3eWivg=='  # Replace this with the API key for the web service
    headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key)}
    req = urllib.request.Request(url, body, headers)
    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        json_data = json.loads(result)['Results']['output1'][0]
        # print(result)
        print(json_data)
        print('Scored Labels: ' + json_data['Scored Labels'])
        print('Scored Probabilities: ' + json_data['Scored Probabilities'])
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))

if __name__=="__main__":
    run_baseline()