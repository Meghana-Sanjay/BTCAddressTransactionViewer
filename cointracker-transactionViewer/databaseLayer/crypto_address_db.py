import time
from flask import Flask
from sqlalchemy import MetaData, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
metadata = MetaData()
engine = create_engine('sqlite:///databaseLayer/crypto_address_db', connect_args={'check_same_thread': False},
                       echo=False)
Base = declarative_base()
db_session = sessionmaker(bind=engine)()

""" Class Wallet

- Defined the Wallet DB object
    - walletAddress : Address of the wallet being stored (PK)
    - insertTime : Time at which the address was inserted
"""
class Wallet(Base):
    __tablename__ = 'wallet'
    address = Column(String, primary_key=True)
    insertTime = Column(Integer)
    transactionInfo = Column(String)


""" Class User

- Defined the User DB object
    - userId : Address of the wallet being stored (PK)
    - addresses : Wallet addresses associated to a user
"""
class User(Base):
    __tablename__ = 'user'
    userId = Column(String, primary_key=True)
    addresses = Column(String)


""" getWallets

- DB api to get all the stored wallet addresses
"""
def getWallets():
    return db_session.query(Wallet)


""" wallets, WALLETS

- sqlalchemy constructs to work with a Wallet db session
"""
wallets = getWallets()
WALLETS = [[wallet.address, wallet.transactionInfo, wallet.insertTime] for wallet in wallets]

""" getUsers

- DB api to get all the stored users
"""
def getUsers():
    return db_session.query(User)


""" users, USERS

- sqlalchemy constructs to work with a User db session
"""
users = getUsers()
USERS = [[user.userId, user.addresses] for user in users]

""" setUserAddresses

- DB api to set the user and address in the account
"""
def setUserDetails(userId, address):
    print('Setting user details for user - ', userId)
    try:
        record = users.filter(User.userId == userId).first()
        allAddresses = record.addresses.split(",")
        if address not in allAddresses:
            record.addresses += ',' + address
    except:
        newUser = User(userId=str(userId), addresses=str(address))
        db_session.add(newUser)

    db_session.commit()


""" deleteUserAddress

- DB api to delete an address from a user's wallet
"""
def deleteUserAddress(userId, address):
    print('Deleting address for user - ', userId)
    try:
        record = users.filter(User.userId == userId).first()
        allAddresses = record.addresses.split(",")
        if address in allAddresses:
            allAddresses.remove(address)
            record.addresses = ",".join(allAddresses)
            db_session.commit()
    except:
        print("No matching record")


""" getUserAddresses

- DB api to get the addresses in the account
"""
def getUserAddresses(userId):
    print('Getting addresses for user - ', userId)
    try:
        record = users.filter(User.userId == userId).first()
        allAddresses = record.addresses.split(",")
        return allAddresses
    except:
        print('No addresses in user account')
        return []


""" synchronizeWalletAddress

- DB api to update the wallet's transactionInfo
"""
def synchronizeWalletAddress(address, transactionInfo):
    print('Updating transactionInfo for address - ', address)
    try:
        record = wallets.filter(Wallet.address == address).first()
        record.transactionInfo = str(transactionInfo)
    except:
        newAddress = Wallet(address=address, insertTime=time.time(), transactionInfo=transactionInfo)
        db_session.add(newAddress)

    db_session.commit()


""" getTransactionsByAddress

- DB api to get transactionIndo for the address
"""
def getTransactionsByAddress(address):
    print('Getting transactionInfo for address - ', address)
    try:
        record = wallets.filter(Wallet.address == address).first()
        return record.transactionInfo
    except:
        return None
