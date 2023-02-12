from brownie import accounts, FinancialManagerial, Token

def deploy_token_contract(contract_creator_account):
    Token.deploy('MyAgency', 'MA', {'from': contract_creator_account})

def deploy_financial_managerial_contract(contract_creator_account):
    token_contract = Token[-1]
    financial_managerial_contract = FinancialManagerial.deploy(token_contract.address, {'from': contract_creator_account})

def main():
    contract_creator_account = accounts[0]
    deploy_token_contract(contract_creator_account)
    deploy_financial_managerial_contract(contract_creator_account)