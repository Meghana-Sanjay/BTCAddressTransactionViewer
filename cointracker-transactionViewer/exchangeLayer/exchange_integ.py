import hashlib
import base58
import binascii
import json
import urllib


from databaseLayer.crypto_address_db import db_session, synchronizeWalletAddress

""" synchronizeTransactions

- Given the addresses, sync the transactionInfo in the DB
"""
def synchronizeTransactions(addresses):
    print('Synchronizing transactions for addresses - ', addresses)
    blockchairApiEndpoint = 'https://api.blockchair.com/bitcoin/dashboards/address/'

    """ getTransactions

    - Given the address, return transactions and final balance
    """
    def getTransactionsFromExchange(address):
        print('Retrieving transactions for address - ', address)

        def retrieveTransactionsAndBalanceForAddress(address):
            transactions_url = blockchairApiEndpoint + address
            response = urllib.request.urlopen(transactions_url)
            data = json.loads(response.read())

            print('Retrieved transactions for address - ', address)
            return json.dumps(data)

        return retrieveTransactionsAndBalanceForAddress(address)

    for address in addresses:
        synchronizeWalletAddress(address, getTransactionsFromExchange(address))

    db_session.commit()
    return

""" bitcoinAddressValidator

- Validate input address to conform to a btc address 
"""
def bitcoinAddressValidator(bitcoinAddress):

    try :
        # base58.b58decode method generate Byte and we should convert it to Hex with hex() method
        base58Decoder = base58.b58decode(bitcoinAddress).hex()
        prefixAndHash = base58Decoder[:len(base58Decoder) - 8]
        checksum = base58Decoder[len(base58Decoder) - 8:]

        # to handle a valid result, we should pass our input to hashlib.sha256() method() as Byte format
        # so we use binascii.unhexlify() method to convert our input from Hex to Byte
        # finally, hexdigest() method convert value to human-readable
        hash = prefixAndHash
        for x in range(1, 3):
            hash = hashlib.sha256(binascii.unhexlify(hash)).hexdigest()
            print("Hash#", x, " : ", hash)
        if (checksum == hash[:8]):
            print("Checksum is valid!")
            return True
        else:
            print("Checksum is not valid!")
            return False

    except:
        return True
