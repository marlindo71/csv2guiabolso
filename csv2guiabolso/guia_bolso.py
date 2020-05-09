import uuid
import hashlib
import requests
import json
import csv

class GuiaBolso(object):
    def __init__(self, email, password):
        self.token=""
        self.email = email
        self.password = password
        hardware_address = str(uuid.getnode()).encode('utf-8')
        self.device_token = hashlib.md5(hardware_address).hexdigest()
        self.session = requests.Session()
        self.token = self.login()
        self.basic_info = self.get_basic_info()

    def login(self):

        url = "https://www.guiabolso.com.br/comparador/v2/events/others"

        payload = """
        {
             "name":"web:users:login",
             "version":"1",
             "payload":{"email":%s,
                        "pwd":%s,
                        "userPlatform":"GUIABOLSO",
                        "deviceToken":"%s",
                        "os":"Windows",
                        "appToken":"1.1.0",
                        "deviceName":"%s"},
             "flowId":"","id":"",
             "auth":{"token":"","x-sid":"","x-tid":""},
             "metadata":{"origin":"web",
                         "appVersion":"1.0.0",
                         "createdAt":"2020-04-24T23:20:05.552Z"},
             "identity":{}
        }""" % (json.dumps(self.email),
                json.dumps(self.password),
                self.device_token,
                self.device_token)

        headers = {
            'content-type': "application/json"
        }

        response = self.session.get(url, headers=headers)
        response = self.session.post(url, headers=headers, data=payload).json()
        if response['name'] != "web:users:login:response":
            print(response['name'])
            raise Exception(response['payload']['code'])
        
        return response['auth']['token']

    def get_basic_info(self):
        url = "https://www.guiabolso.com.br/comparador/v2/events/"

        headers = {
            'content-type': "application/json"
        }

        payload = """
        {
            "name":"rawData:info",
            "version":"6",
            "payload":{"userPlatform":"GUIABOLSO",
                       "appToken":"1.1.0",
                       "os":"Win32"},
            "flowId":"",
            "id":"",
            "auth":{"token":"Bearer %s",
                    "sessionToken":"%s",
                    "x-sid":"",
                    "x-tid":""},
            "metadata":{"origin":"web",
                        "appVersion":"1.0.0",
                        "createdAt":""},
            "identity":{}
        }""" % (self.token,
                self.token)

        response = self.session.post(url, headers=headers, data=payload).json()

        d = {}
        d['categoryTypes'] = response['payload']['categoryTypes']
        d['accounts'] = response['payload']['accounts']

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=4)
    
        return dict(d)
    
    def get_manual_accounts(self):
        print("##########  Contas Manuais  ###########")
        for account in self.basic_info['accounts']:
            if account['name'] == "Conta manual":
                for item in account['statements']:
                    acc_id = item['id']
                    acc_name = item['name']
                    print(f'ID: {acc_id} | Conta: {acc_name}')
    
    def get_categories(self):
        # categories = []
        linha = {}
        print("##########    Categorias    ###########")
        for categoryType in self.basic_info['categoryTypes']:
            for category in categoryType['categories']:
                # linha['id'] = category['id']
                # linha['name'] = category['name']
                # linha['tipo'] = categoryType['name']
                print(f"Categoria: {category['name']} | ID: {category['id']} | Tipo: {categoryType['name']}")
                # categories.append(linha.copy())

    def load_csv(self,file_location):
        csv_file = []

        with open(file_location, mode='r') as f:
            csv_reader = csv.DictReader(f,delimiter=';')
            for row in csv_reader:
                linha = dict(row)
                linha['label'] = linha['name']
                csv_file.append(linha.copy())
        return csv_file
    
    def upload_csv(self,file_location):
        headers = {
            'content-type': "application/json"
        }
        url = "https://www.guiabolso.com.br/comparador/v2/events/"
        csv_file = self.load_csv(file_location)
        payload = {
            "name":"save:manual:transaction",
            "version":"1",
            "payload":{"arguments":{"payload":{}}},
            "flowId":"",
            "id":"",
            "auth":{"token":"Bearer " + self.token,
                    "sessionToken": self.token,
                    "x-sid":"",
                    "x-tid":""},
            "metadata":{"origin":"web",
                        "appVersion":"1.0.0",
                        "createdAt":""},
            "identity":{}
        }
        for linha in csv_file:

            payload['payload']['arguments']['payload'] = linha
            response = self.session.post(url, headers=headers, json=payload).json()

            if response['name'] != "save:manual:transaction:response":
                print(response.content)
                raise Exception("Erro ao Salvar")
                