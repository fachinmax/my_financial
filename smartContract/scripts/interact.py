from brownie import Token, FinancialManagerial, accounts

def interact_financial_managerial_contract(user):
    contract = FinancialManagerial[-1]
    print(contract.totalDeployed({'from': user}))


def main():
    user_account = accounts[1]
    print(user_account)
    interact_financial_managerial_contract(user_account)