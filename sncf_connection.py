import json
import requests
import pandas as pd

class SNCF:

    def __init__(self, token_path='sncf.token'):
        self.api_key = self.__get_api_key(token_path)
        self.api_endpoint = 'https://ressources.data.sncf.com/api/records/1.0/search/'


    def __get_api_key(self, path='sncf.token'):
        with open(path, 'r') as file:
            api_key= file.read()
        return api_key


    def exec_request(self, splmt):
        url = self.api_endpoint + '?' + splmt
        req = requests.get(url)
        return req
    

    def get_dataset_json(self, dataset_name):
        splmt ='dataset={}'.format(dataset_name)
        req = self.exec_request(splmt) 
        json_file = json.loads(req.content)
        return json_file


    def get_dataset_df(self, dataset_name):
        json_file = self.get_dataset_json(dataset_name)
        return self.json_to_df(json_file)


    def json_to_df(self, json_file):
        data = [i['fields'] for i in json_file['records']]
        df = pd.DataFrame(data)
        return df


    def dict_to_splmt(self, dict_):
        splmt = ''
        for key, value in dict_.items():
            splmt += '&' if len(splmt)>0 else ''
            splmt += key + '=' + value
        return splmt


    def print_test(self):
        print('tooto')
