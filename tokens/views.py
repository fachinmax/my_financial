from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .wallet import Wallet
from .forms import MetamaskLocal
from django.views.decorators.csrf import csrf_protect
from web3 import Web3
from pymongo import MongoClient
from datetime import datetime


# function used on views
def get_information_for_user(request):
    """return all the data the user needs to view"""
    global ganache
    data = dict()
    # token's symbol
    data['symbol'] = ganache.get_symbol()
    # token's name
    data['name'] = ganache.get_name()
    # amount tokens not deployed in financial managerial smart contract
    data['tokens_not_deployed'] = ganache.get_amount_tokens()
    # amount tokens deployed in financial managerial smart contract
    data['tokens_deployed'] = ganache.get_total_amount_tokens_deployed()
    # list of all user's cost centers
    data['cost_centers'] = ganache.get_cost_centers()
    # get all respective percentages and amount stored in user's cost centers
    percentage_cost_centers = list()
    amount_stored = list()
    for cost_center in data['cost_centers']:
        percentage_cost_centers.append(ganache.get_percentage_cost_centers(cost_center))
        amount_stored.append(ganache.get_amount_stored(cost_center))
    # list of all percentages
    data['percentages'] = percentage_cost_centers
    # list of all tokens stored in every user's cost centers
    data['amount_stored'] = amount_stored
    # get events data from mongodb
    events_type = request.GET.get('events')
    # if users choosed a specific type of event to see
    if events_type:
        tokens_sended = list()
        tokens_received = list()
        tokens_deployed = list()
        tokens_withdraw = list()
        events = db.events.find({'name': events_type}).sort('date', -1)
        for event in events:
            # given the type of event the user want to see, I will retrive all related events
            if events_type == 'Transfer':
                if ganache.get_address() == event.get('to'):
                    tokens_received.append({
                        'user': event.get('from'),
                        'amount': event.get('value'),
                        'date': event.get('date').strftime('%-S:%-M:%-H %-d %B %Y')
                    })
                if ganache.get_address() == event.get('from'):
                    tokens_sended.append({
                        'user': event.get('to'),
                        'amount': event.get('value'),
                        'date': event.get('date').strftime('%-S:%-M:%-H %-d %B %Y')
                    })
            if events_type == 'DeployNewTokens' and ganache.get_address() == event.get('user'):
                tokens_deployed.append({
                    'amount': event.get('amount'),
                    'date': event.get('date').strftime('%-S:%-M:%-H %-d %B %Y')
                })
            if events_type == 'WithdrawTokens' and ganache.get_address() == event.get('user'):
                tokens_withdraw.append({
                    'amount': event.get('amount'),
                    'cost_center': event.get('costCenter'),
                    'date': event.get('date').strftime('%-S:%-M:%-H %-d %B %Y')
                })
        # I'm going to save all the events the user wants to see
        data['received'] = tokens_received
        data['sended'] = tokens_sended
        data['deployed'] = tokens_deployed
        data['withdrawed'] = tokens_withdraw
    # I'm going to take all type of events
    documents = db.events.find()
    events = list()
    for document in documents:
        if document.get('name') not in events:
            events.append(document.get('name'))
    data['events_type'] = events
    # if user is admin then he's going to do more functionality. The admin can send tokens to other addresses registered on mongodb
    if request.user.is_staff:
        address = list()
        documents = db.address.find()
        for document in documents:
            address.append(document.get('_id'))
        data['addresses'] = address
    return data

def validate_percentages(percentages):
    """function to validate the percentages list syntax passed by user"""
    try:
        percentages = percentages.split(', ')
        for count in range(0, len(percentages)):
            percentages[count] = int(percentages[count])
        return {'OK': percentages}
    except Exception as error:
        return {'ERR': "Percentage must have this syntax: NN, NN, NN. For example: 50, 40, 10"}

def save_events(events):
    """function to save events on mongodb"""
    for event in events:
        document = dict(event.get('args'))
        document['name'] = event.get('event')
        document['date'] = datetime.now()
        db['events'].insert_one(document)


# Create your views here.
@csrf_protect
def login(request):
    """view for user authentication. If user didn't authenticate then return a authentication form"""
    global ganache
    # authentication form
    form = MetamaskLocal(request.POST or None)
    # if user sended address and private key for authentication
    if form.is_valid():
        ADDRESS = form.cleaned_data.get('address')
        PRIVATE_KEY = form.cleaned_data.get('private_key')
        ganache = Wallet(address=ADDRESS, private_key=PRIVATE_KEY)
        response = ganache.get_status_connection()
        if response.get('result'):
            accounts = ganache.get_accounts()
            if ADDRESS in accounts:
                # check if address is already saved on mongodb
                exist = False
                for document in db.address.find():
                    if ADDRESS == document.get('_id'):
                        exist = True
                # if address not saved on mongodb then I'm going to save
                if not exist:
                    db.address.insert_one({'_id': ADDRESS})
                # when I start project I'm going to mint some tokens to site administrator to see how the site function
                if request.user.is_staff and ganache.get_total_amount_tokens_deployed() == 0 and ganache.get_amount_tokens() == 0:
                    ganache.mint_new_tokens(99999)
                return render(request, 'account.html', get_information_for_user(request))
            else:
                messages.add_message(request, messages.ERROR, "Address doesn't exist in ganache network.")
        else:
            messages.add_message(request, messages.ERROR, response.get('response'))
    # whether the user need to authenticate or connection failed
    return render(request, 'login.html', {'form': form})

def deploy_tokens(request):
    """view for deploy user's token on financial managerial smart contract"""
    global ganache
    amount_tokens = int(request.GET.get('amountTokens'))
    if amount_tokens != 0:
        response = ganache.deploy_new_tokens(amount_tokens)
        if response.get('ERR'):
            messages.add_message(request, messages.ERROR, response.get('ERR'))
        # when tokens deployed I'm going to save the events on mongodb
        else:
            save_events(response.get('events'))
    return render(request, 'account.html', get_information_for_user(request))

def withdraw_tokens(request):
    """view for withdraw user's token from a specific cost center"""
    global ganache
    if request.GET.get('costCenters'):
        cost_center = request.GET.get('costCenters')
        amount_tokens = int(request.GET.get('amountTokens'))
        if amount_tokens > ganache.get_amount_stored(cost_center):
            messages.add_message(request, messages.ERROR, "You can't withdraw more tokens about than you have.")
        else:
            response = ganache.withdraw_tokens(cost_center, amount_tokens)
            if response.get('ERR'):
                messages.add_message(request, messages.ERROR, response.get('ERR'))
            # when tokens withdrawed I'm going to save the events on mongodb
            else:
                save_events(response.get('events'))
    else:
        messages.add_message(request, messages.ERROR, "Create your tokens distribution.")
    return render(request, 'account.html', get_information_for_user(request))

def remove_cost_center(request):
    """view for remove a specific cost center. Firstly I withdraw all users token and then I'm going to remove the cost center"""
    global ganache
    if request.GET:
        cost_center = request.GET.get('costCenters')
        response = ganache.remove_cost_center(cost_center)
        if response.get('ERR'):
            messages.add_message(request, messages.ERROR, response.get('ERR'))
        # when the cost center was remove I'm going to save the events on mongodb
        else:
            save_events(response.get('events'))
    else:
        messages.add_message(request, messages.ERROR, "Create your tokens distribution.")
    return render(request, 'account.html', get_information_for_user(request))

def update_cost_centers(request):
    """view for update all cost centers and its percentage"""
    global ganache
    # I take all cost center and then I'm going to create a cost center list to send at financial managerial smart contract
    cost_centers = request.GET.get('costCenters')
    cost_centers = cost_centers.split(', ')
    # I take all cost centers' percentages and then I'm going to create a percentages list to send at financial managerial smart contract
    percentages = request.GET.get('percentages')
    response = validate_percentages(percentages)
    if response.get('OK'):
        response = ganache.set_distribution(cost_centers, response.get('OK'))
        if response.get('ERR'):
            messages.add_message(request, messages.ERROR, response.get('ERR'))
    # when the cost center was update I'm going to save the events on mongodb
    else:
        messages.add_message(request, messages.ERROR, response.get('ERR'))
    return render(request, 'account.html', get_information_for_user(request))

def create_default_distribution(request):
    """view for create a default distribution. This default distribution changes based on the type of user: administrator or normal user"""
    global ganache
    # if user is admin then the default allocation is different: every cost center match with every address saved on mongodb
    if(request.user.is_staff):
        # I'm going to create a list with all address saved on mongodb
        cost_centers = list()
        documents = db.address.find()
        number_of_address = 0
        for document in documents:
            cost_centers.append(document.get('_id'))
            number_of_address += 1
        # I'm going to calculate and create a percentages cost centers list
        percentages = list()
        amount_calculated = 0
        for i in range(0, number_of_address):
            percentage = int(100/number_of_address)
            percentages.append(percentage)
            amount_calculated += percentage
        if amount_calculated != 100:
            percentages[0] += 100 - amount_calculated
        response = ganache.set_distribution(cost_centers, percentages)
        if response.get('ERR'):
            messages.add_message(request, messages.ERROR, response.get('ERR'))
    else:
        response = ganache.create_default_distribution()
        if response.get('ERR'):
            messages.add_message(request, messages.ERROR, response.get('ERR'))
    return render(request, 'account.html', get_information_for_user(request))

def send_token_to(request):
    """view for send specific amount of tokens from a user to other address"""
    global ganache
    address = request.GET.get('addresses')
    amount_tokens = int(request.GET.get('amountTokens'))
    response = ganache.transfer(address, amount_tokens)
    if response.get('ERR'):
        messages.add_message(request, messages.ERROR, response.get('ERR'))
    # I'm going to save the events on mongodb when the cost center was update
    else:
        save_events(response.get('events'))
    return render(request, 'account.html', get_information_for_user(request))

def events(request):
    """view to show the user the requested events"""
    return render(request, 'account.html', get_information_for_user(request))


# create global variables
# object for comunicated with ganache
ganache = ''
# object for comunicated with MongoDB
client = MongoClient('localhost', 27017)
db = client['financial_managerial']