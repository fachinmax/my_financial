from web3 import Web3
import json
from eth_account import Account


class Wallet:
    def __init__(self, address, private_key):
        """inizialize user's address and private key, connection with ganache, fetch address and abi of smart contracts and create
        smart contracts"""
        # parameter for indicate whether the credentials (address and private key) are correct
        self.__credential_correct = True
        # check user's address and user's private key
        response = self.__validate_authentication(address, private_key)
        if response.get('result'):
            self.__valid_object = True
            self.__ADDRESS = address
            # user's private key
            self.__PRIVATE_KEY = private_key
            self.__inizialize_connection()
            # create object for connect with financial managerial smart contract
            address = self.__get_financial_managerial_smart_contract_address()
            abi = self.__get_financial_managerial_smart_contract_abi()
            self.__financial_managerial_smart_contract = self.__ganache.eth.contract(abi=abi, address=address)
            # create object for connect with token smart contract
            address = self.__get_token_smart_contract_address()
            abi = self.__get_token_smart_contract_abi()
            self.__token_smart_contract = self.__ganache.eth.contract(abi=abi, address=address)
        else:
            # set false this variabile if the address and the private key were wrongs 
            self.__credential_correct = False
    
    def __validate_authentication(self, address, private_key):
        """check the match of user's private key and users's address and check the address"""
        # check address
        try:
            destination_address = Web3.to_checksum_address(address)
        except ValueError as error:
            return {'result': False, 'response': str(error.args)[2: -3]}
        except TypeError as error:
            return {'result': False, 'response': str(error.args)[2: -3]}
        # check the match of user's address and user's private key
        try:
            account = Account.from_key(private_key)
        except ValueError as error:
            return {'result': False, 'response': str(error.args)[2: -3]}
        if address == account.address and private_key == Web3.to_hex(account.key):
            return {'result': True}
        else:
            return {'result': False, 'response': "Private key and address don't match"}

    def __inizialize_connection(self):
        """inizialize connection with ganache blockchain"""
        self.__ganache = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

    def __get_financial_managerial_smart_contract_address(self):
        """fetch and return address of financial managerial smart contract"""
        with open('./smartContract/build/deployments/map.json') as file:
            smart_contract_text = file.read()
        smart_contract_json = json.loads(smart_contract_text)
        return smart_contract_json['5777']['FinancialManagerial'][-1]

    def __get_financial_managerial_smart_contract_abi(self):
        """fetch and return abi of financial managerial smart contract"""
        with open('./smartContract/build/contracts/FinancialManagerial.json') as file:
            smart_contract_file = file.read()
        smart_contract_json = json.loads(smart_contract_file)
        return smart_contract_json['abi']
    
    def __get_token_smart_contract_address(self):
        """fetch and return address of agency's new token smart contract"""
        with open('./smartContract/build/deployments/map.json') as file:
            smart_contract_text = file.read()
        smart_contract_json = json.loads(smart_contract_text)
        return smart_contract_json['5777']['Token'][-1]

    def __get_token_smart_contract_abi(self):
        """fetch and return abi of agency's new token smart contract"""
        with open('./smartContract/build/contracts/Token.json') as file:
            smart_contract_file = file.read()
        smart_contract_json = json.loads(smart_contract_file)
        return smart_contract_json['abi']

    def __get_transaction_parameters(self):
        """return paramenter for build a new function"""
        return {
            'nonce': self.__ganache.eth.get_transaction_count(self.__ADDRESS),
            'chainId': self.__ganache.eth.chain_id,
            'from': self.__ADDRESS,
            'gasPrice': self.__ganache.eth.gas_price
        }
    
    def get_address(self):
        """return user address"""
        return self.__ADDRESS

    def get_status_connection(self):
        """if connection was successful return true otherwise whether the address and the private key were wrong return false"""
        if self.__credential_correct:
            if self.__ganache.is_connected():
                return {'result': True}
            else:
                return {'result': False, 'response': 'Connection failed'}
        else:
            return {'result': False, 'response': 'address and/or private key are wrongs'}

    def __send_transaction(self, transaction):
        """sign, send and return receipt transaction"""
        sign_transaction = self.__ganache.eth.account.sign_transaction(transaction, self.__PRIVATE_KEY)
        hash_transaction = self.__ganache.eth.send_raw_transaction(sign_transaction.rawTransaction)
        return self.__ganache.eth.wait_for_transaction_receipt(hash_transaction)

    def create_default_distribution(self):
        """create a default distribution"""
        try:
            transaction = self.__financial_managerial_smart_contract.functions.createDefaultDistribution().build_transaction(self.__get_transaction_parameters())
            self.__send_transaction(transaction)
            return dict({'OK': 'distribution created'})
        except Exception as error:
            return dict({'ERR': str(error.args)[72: -3]})
    
    def set_distribution(self, cost_centers, cost_centers_percentage):
        """change the the cost centers and its percentages"""
        if(str(type(cost_centers))[8:12] == 'list' and str(type(cost_centers_percentage))[8:12] == 'list'):
            try:   
                transaction = self.__financial_managerial_smart_contract.functions.setDistribution(cost_centers, cost_centers_percentage).build_transaction(self.__get_transaction_parameters())
                self.__send_transaction(transaction)
                return dict({'OK': 'distribution setted'})
            except Exception as error:
                return dict({'ERR': str(error.args)[72: -3]})
        else:
            return 'You must send two list of values. The first one must be a strings list and second one must be a int list'
    
    def get_total_amount_tokens_deployed(self):
        """return the amount of tokens deployed on financial managerial smart contract"""
        return self.__financial_managerial_smart_contract.functions.totalDeployed().call({'from': self.__ADDRESS})

    def remove_cost_center(self, cost_center):
        """remove a specific cost center and return all events generated by the token smart contract and financial managerial smart contract"""
        if(str(type(cost_center))[8:11] == 'str'):
            try:
                events = list()
                transaction = self.__financial_managerial_smart_contract.functions.removeCostCenter(cost_center).build_transaction(self.__get_transaction_parameters())
                transaction_receipt = self.__send_transaction(transaction)
                # create events for send to user
                log_to_process_of_token_smart_contract = transaction_receipt['logs'][0]
                log_to_process_of_financial_managerial_smart_contract = transaction_receipt['logs'][1]
                events.append(self.__token_smart_contract.events.Transfer().process_log(log_to_process_of_token_smart_contract))
                events.append(self.__financial_managerial_smart_contract.events.WithdrawTokens().process_log(log_to_process_of_financial_managerial_smart_contract))
                return dict({'OK': 'cost center removed', 'events': events})
            except Exception as error:
                return dict({'ERR': str(error.args)[72: -3]})
        else:
            return 'You must send an string of one cost center to delete.'

    def withdraw_tokens(self, cost_center, amount):
        """withdraw a specific amoount of tokens of a cost center and return all events generated by the token smart contract and financial managerial smart contract"""
        if(str(type(cost_center))[8:11] == 'str' and str(type(amount))[8:11] == 'int'):
            try:
                events = list()
                transaction = self.__financial_managerial_smart_contract.functions.withdraw(cost_center, amount).build_transaction(self.__get_transaction_parameters())
                transaction_receipt = self.__send_transaction(transaction)
                # create events for send to user
                log_to_process_of_token_smart_contract = transaction_receipt['logs'][0]
                log_to_process_of_financial_managerial_smart_contract = transaction_receipt['logs'][1]
                events.append(self.__token_smart_contract.events.Transfer().process_log(log_to_process_of_token_smart_contract))
                events.append(self.__financial_managerial_smart_contract.events.WithdrawTokens().process_log(log_to_process_of_financial_managerial_smart_contract))
                return dict({'OK': 'tokens withdrawed', 'events': events})
            except Exception as error:
                return dict({'ERR': str(error.args)[72: -3]})
        else:
            return 'You must send an string of cost center and the amount to with draw.'

    def deploy_new_tokens(self, amount):
        """deploy new tokens and return all events generated by the token smart contract and financial managerial smart contract"""
        if(str(type(amount))[8:11] == 'int'):
            try:
                events = list()
                transaction = self.__financial_managerial_smart_contract.functions.deploy(amount).build_transaction(self.__get_transaction_parameters())
                transaction_receipt_of_financial_managerial_smart_contract = self.__send_transaction(transaction)
                transaction = self.__token_smart_contract.functions.transfer(self.__financial_managerial_smart_contract.address, amount).build_transaction(self.__get_transaction_parameters())
                transaction_receipt_of_token_smart_contract = self.__send_transaction(transaction)
                # create events for send to user
                log_to_process_of_financial_managerial_smart_contract = transaction_receipt_of_financial_managerial_smart_contract['logs'][0]
                log_to_process_of_token_smart_contract = transaction_receipt_of_token_smart_contract['logs'][0]
                events.append(self.__financial_managerial_smart_contract.events.DeployNewTokens().process_log(log_to_process_of_financial_managerial_smart_contract))
                events.append(self.__token_smart_contract.events.Transfer().process_log(log_to_process_of_token_smart_contract))
                return dict({'OK': 'tokens deployed', 'events': events})
            except Exception as error:
                return dict({'ERR': str(error.args)[72: -3]})
        else:
            return 'You must send an integer of tokens to deploy.'

    def get_cost_centers(self):
        """return all users's cost centers"""
        return self.__financial_managerial_smart_contract.functions.getUserCostCenter().call({'from': self.__ADDRESS})

    def get_percentage_cost_centers(self, cost_center):
        """return all users's percentage cost centers"""
        return self.__financial_managerial_smart_contract.functions.usersPercentageCostCenters(self.__ADDRESS, cost_center).call()

    def get_amount_stored(self, cost_center):
        """return total amount of tokens deployed on a specific user's cost center"""
        return self.__financial_managerial_smart_contract.functions.usersStorageArea(self.__ADDRESS, cost_center).call()

    def mint_new_tokens(self, amount):
        """mint new tokens. This function must be used when was buy a agency's product"""
        transaction = self.__token_smart_contract.functions.mint(amount).build_transaction(self.__get_transaction_parameters())
        self.__send_transaction(transaction)

    def get_amount_tokens(self):
        """return total amount of tokens deployed on financial managerial smart contract"""
        return self.__token_smart_contract.functions.balanceOf(self.__ADDRESS).call()

    def get_accounts(self):
        """return all ganache's accounts"""
        return self.__ganache.eth.accounts
    
    def transfer(self, to, amount):
        """transfer a specif amount of tokens to specific user. Return the event of token smart contract"""
        if(str(type(amount))[8:11] == 'int'):
            try:
                event = list()
                to = Web3.to_checksum_address(to)
                transaction = self.__token_smart_contract.functions.transfer(to, amount).build_transaction(self.__get_transaction_parameters())
                transaction_receipt = self.__send_transaction(transaction)
                # create event for send to user
                log_to_process = transaction_receipt['logs'][0]
                event.append(self.__token_smart_contract.events.Transfer().process_log(log_to_process))
                return dict({'OK': 'tokens deployed', 'events': event})
            except ValueError as error:
                return dict({'ERR': str(error.args)[2: -3]})
            except TypeError as error:
                return dict({'ERR': str(error.args)[2: -3]})
            except Exception as error:
                return dict({'ERR': str(error.args)[72: -3]})
        else:
            return 'You must send an integer of tokens to deploy.'

    def get_symbol(self):
        """return the agency's token symbol"""
        return self.__token_smart_contract.functions.symbol().call()
    
    def get_name(self):
        """return the agency's token name"""
        return self.__token_smart_contract.functions.name().call()
