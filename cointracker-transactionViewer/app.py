import json
import os
from flask import Flask, render_template, escape, request

from databaseLayer.crypto_address_db import setUserDetails, getUserAddresses, getTransactionsByAddress, db_session, \
    deleteUserAddress
from exchangeLayer.exchange_integ import synchronizeTransactions, bitcoinAddressValidator

app = Flask(__name__)
userID = "admin"

app.secret_key = 'cgibeifjccgib!!TEST12345' # flask needs a secret key

@app.route("/")
def index():
    return render_template("/index.html")


@app.route("/manageAddresses", methods=["GET", "POST"])
def manageAddresses():
    newAddress = str(escape(request.form.get("Address", None)))

    if request.method == 'POST':
        if request.form["submit_button"] == 'AddAddress':
            if bitcoinAddressValidator(newAddress):
                setUserDetails(userID, newAddress)
                userMsg = '\nAddress Added successfully'
                return render_template("/manageAddresses.html") + userMsg
            else:
                userMsg = "\nInvalid BTC Address !"
                return render_template("/manageAddresses.html") + userMsg
        elif request.form["submit_button"] == 'DeleteAddress':
            deleteUserAddress(userID, newAddress)
            return render_template("/manageAddresses.html") + 'Address deleted !'

    # render succ / fail here
    return render_template("/manageAddresses.html")


@app.route("/syncAndRetrieveBalances", methods=["GET", "POST"])
def syncAndRetrieveBalances():
    address = str(escape(request.form.get("Address", None)))
    addresses = getUserAddresses(userID)
    print("List Of Addresses:"+ str(addresses))

    if address not in addresses:
        userMsg = '\nPlease enter an address from the list'
        return render_template("/syncAndRetrieveBalances.html",
                               listOfAddresses = addresses,
                               userID = userID) + userMsg

    synchronizeTransactions(addresses)
    print(address)

    items = []
    finalBalance = 0.0
    if request.method == 'POST':
        if request.form["submit_button"] == 'ViewAddressTransactions' and address:
            tinfo = json.loads(getTransactionsByAddress(address))
            addressData = tinfo['data'][str(address)]
            bType = addressData['address']['type']

            if not bType:
                userMsg = '\nAddress is not valid, remove it from your account'
                return render_template("/syncAndRetrieveBalances.html",
                                       listOfAddresses = addresses,
                                       userID = userID) + userMsg

            finalBalance = addressData['address']['balance']/100000000
            txs = addressData['transactions']

            i=0
            for transactionHash in txs:
                i+=1
                items.append(dict(
                              index=str(i),
                              hash=transactionHash))

    headers = ['index', 'hash']
    return render_template("/syncAndRetrieveBalances.html",
                           headers = headers,
                           objects = items,
                           address = address,
                           finalBalance = finalBalance,
                           listOfAddresses = addresses,
                           userID = userID)

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 4444)))
