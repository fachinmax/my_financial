from brownie import FinancialManagerial, Token, accounts, exceptions
import pytest

def test_deploy_financial_mangerial():
    # arrange
    user_account = accounts[1]
    contract = FinancialManagerial[-1]
    # act
    contract.createDefaultDistribution({'from': user_account})
    cost_centers = list(contract.getUserCostCenter({'from': user_account}))
    # assert
    assert cost_centers == ['home', 'study', 'investment', 'sport', 'other']

def test_set_distribution():
    # arrange
    user_account = accounts[1]
    contract = FinancialManagerial[-1]
    # act
    contract.setDistribution(['home', 'travel', 'sport'], [60, 10, 30], {'from': user_account})
    percentage_home = contract.usersPercentageCostCenters(user_account, 'home')
    percentage_travel = contract.usersPercentageCostCenters(user_account, 'travel')
    percentage_sport = contract.usersPercentageCostCenters(user_account, 'sport')
    cost_centers = contract.getUserCostCenter({'from': user_account})
    # assert
    assert percentage_home == 60
    assert percentage_travel == 10
    assert percentage_sport == 30
    assert cost_centers == ['home', 'travel', 'sport']

def test_deploy_tokens():
    # arrange
    user_account = accounts[1]
    amount_to_mint = 4000
    amount_to_deploy = 1000
    financial_managerial_contract = FinancialManagerial[-1]
    token_contract = Token[-1]
    initial_amount_deployed = financial_managerial_contract.totalDeployed({'from': user_account})
    initial_tokens_user = token_contract.balanceOf(user_account)
    initial_tokens_contract = token_contract.balanceOf(financial_managerial_contract.address)
    # act
    token_contract.mint(amount_to_mint, {'from': user_account})
    token_contract.transfer(financial_managerial_contract.address, amount_to_deploy, {'from': user_account})
    financial_managerial_contract.deploy(amount_to_deploy, {'from': user_account})
    amount_deployed = financial_managerial_contract.totalDeployed({'from': user_account})
    user_owned_tokens = token_contract.balanceOf(user_account)
    contract_owned_tokens = token_contract.balanceOf(financial_managerial_contract.address)
    # assert
    assert amount_deployed == amount_to_deploy + initial_amount_deployed
    assert user_owned_tokens == initial_tokens_user + amount_to_mint - amount_to_deploy
    assert contract_owned_tokens == initial_tokens_contract + amount_to_deploy


def test_withdraw():
    # arrange
    user_account = accounts[1]
    tokens_to_mint = 4000
    tokens_to_deploy = 1000
    tokens_to_withdraw = 100
    financial_managerial_contract = FinancialManagerial[-1]
    token_contract = Token[-1]
    initial_amount_tokens_user = token_contract.balanceOf(user_account)
    initial_amount_tokens_contract = token_contract.balanceOf(financial_managerial_contract.address)
    # act
    token_contract.mint(tokens_to_mint, {'from': user_account})
    token_contract.transfer(financial_managerial_contract.address, tokens_to_deploy, {'from': user_account})
    financial_managerial_contract.deploy(tokens_to_deploy, {'from': user_account})
    financial_managerial_contract.withdraw('home', tokens_to_withdraw, {'from': user_account})
    user_balance = token_contract.balanceOf(user_account)
    contract_balance = token_contract.balanceOf(financial_managerial_contract.address)
    # assert
    assert user_balance == initial_amount_tokens_user + tokens_to_mint - tokens_to_deploy + tokens_to_withdraw
    assert contract_balance == initial_amount_tokens_contract + tokens_to_deploy - tokens_to_withdraw

def test_division():
    # arrange
    user_account = accounts[1]
    tokens_to_mint = 4000
    tokens_to_deploy = 1000
    financial_managerial_contract = FinancialManagerial[-1]
    token_contract = Token[-1]
    initial_amount_storage_home = financial_managerial_contract.usersStorageArea(user_account, 'home')
    initial_amount_storage_investment = financial_managerial_contract.usersStorageArea(user_account, 'investment')
    initial_amount_storage_study = financial_managerial_contract.usersStorageArea(user_account, 'study')
    initial_amount_storage_sport = financial_managerial_contract.usersStorageArea(user_account, 'sport')
    initial_amount_storage_other = financial_managerial_contract.usersStorageArea(user_account, 'other')
    # act
    token_contract.mint(tokens_to_mint, {'from': user_account})
    token_contract.transfer(financial_managerial_contract.address, tokens_to_deploy, {'from': user_account})
    financial_managerial_contract.deploy(tokens_to_deploy, {'from': user_account})
    amount_storage_home = financial_managerial_contract.usersStorageArea(user_account, 'home')
    amount_storage_investment = financial_managerial_contract.usersStorageArea(user_account, 'investment')
    amount_storage_study = financial_managerial_contract.usersStorageArea(user_account, 'study')
    amount_storage_sport = financial_managerial_contract.usersStorageArea(user_account, 'sport')
    amount_storage_other = financial_managerial_contract.usersStorageArea(user_account, 'other')
    percentage_home = financial_managerial_contract.usersPercentageCostCenters(user_account, 'home')
    percentage_investment = financial_managerial_contract.usersPercentageCostCenters(user_account, 'investment')
    percentage_study = financial_managerial_contract.usersPercentageCostCenters(user_account, 'study')
    percentage_sport = financial_managerial_contract.usersPercentageCostCenters(user_account, 'sport')
    percentage_other = financial_managerial_contract.usersPercentageCostCenters(user_account, 'other')
    # assert
    assert amount_storage_home == initial_amount_storage_home + tokens_to_deploy * percentage_home/100
    assert amount_storage_study == initial_amount_storage_investment + tokens_to_deploy * percentage_investment/100
    assert amount_storage_investment == initial_amount_storage_study + tokens_to_deploy * percentage_study/100
    assert amount_storage_sport == initial_amount_storage_sport + tokens_to_deploy * percentage_sport/100
    assert amount_storage_other == initial_amount_storage_other + tokens_to_deploy * percentage_other/100

def test_error():
    # arrange
    user_account = accounts[1]
    contract_creator_account = accounts[0]
    # act
    financial_managerial_contract = FinancialManagerial[-1]
    # assert
    with pytest.raises(ValueError):
        financial_managerial_contract.setDistribution(['home'], [100], {'from': user_account})
    with pytest.raises(ValueError):
        financial_managerial_contract.withdraw('home', 999999999999, {'from': user_account})
    with pytest.raises(ValueError):
        financial_managerial_contract.withdraw('dd', 45, {'from': user_account})

def test_remove():
    # arrange
    user_account = accounts[1]
    token_smart_contract = Token[-1]
    financial_managerial_contract = FinancialManagerial[-1]
    amount_to_mint = 1000
    cost_center = 'travel'
    percentage = financial_managerial_contract.usersPercentageCostCenters(user_account, cost_center)
    initial_amount_tokens_financial_managerial = token_smart_contract.balanceOf(financial_managerial_contract.address)
    # act
    token_smart_contract.mint(amount_to_mint, {'from': user_account})
    token_smart_contract.transfer(financial_managerial_contract.address, amount_to_mint, {'from': user_account})
    financial_managerial_contract.deploy(amount_to_mint, {'from': user_account})
    initial_amount_user_tokens = financial_managerial_contract.usersStorageArea(user_account, cost_center)
    financial_managerial_contract.removeCostCenter(cost_center, {'from': user_account})
    final_amount_tokens = financial_managerial_contract.usersStorageArea(user_account, cost_center)
    final_amount_tokens_financial_managerial = token_smart_contract.balanceOf(financial_managerial_contract.address)
    # assert
    assert final_amount_tokens == 0
    assert initial_amount_tokens_financial_managerial + amount_to_mint - initial_amount_user_tokens == final_amount_tokens_financial_managerial