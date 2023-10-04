from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

API_BASE_URL = "https://api.exchangerate-api.com/v4/latest/"

# This is a test, to see if a file
# within a sub-directory
# will trigger a build for
# currencyAPI.



async def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    response = requests.get(f"{API_BASE_URL}{from_currency.upper()}") 
    if response.status_code == 200:
        data = response.json()
        if to_currency.upper() in data["rates"]:
            return data["rates"][to_currency.upper()]
        else:
            raise HTTPException(status_code=400, detail="To currency not supported")
    else:
        raise HTTPException(status_code=400, detail="From currency not supported")


@app.get("/exchange_rate")
async def exchange_rate(from_currency: str, to_currency: str) -> dict:
    rate = await get_exchange_rate(from_currency, to_currency)
    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "exchange_rate": rate,
    }


@app.get("/convert_amount")
async def convert_amount(from_currency: str, to_currency: str, amount: float) -> dict:
    rate = await get_exchange_rate(from_currency, to_currency)
    converted_amount = amount * rate
    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "amount": amount,
        "converted_amount": converted_amount,
    }
  
# @CODE : AN ENDPOINT THAT TAKES A STRING AND CONFIRMS IT HAS
# AT LEAST ONE UPPERCASE LETTER, ONE LOWERCASE LETTER, ONE NUMBER, AND IS 8 OR MORE CHARACTERS
# Make sure the return type matches the function signature, FastAPI enforces that it does!
@app.get("/check_password_strength")
async def check_password_strength(password: str) -> bool:
    """
    Coded By: Ihovanna Huezo 
    This function checks whether a given password is strong enough, i.e., it contains at least one digit, 
    one lowercase letter, one uppercase letter, and is 8 characters long.
    """

    conditions = {
        "upper": False,
        "lower": False,
        "number": False,
        "len_8": False
    }
    
    if len(password) >= 8:
        conditions["len_8"] = True

    for char in password:
        if char.isupper():
            conditions["upper"] = True
        if char.islower():
            conditions["lower"] = True
        if char.isnumeric():
            conditions["number"] = True

    if False in conditions.values():
        return False
    else:
        return True

# @CODE : ADD ENDPOINT TO LIST ALL AVAILABLE CURRENCIES  
# NOTE : FastAPI enforces that the return type of the function matches the function signature!  
#        This is a common error!

@app.get("/available_currencies")
async def available_currencies(from_currency: str) -> dict:
    """
    Coded by: Thea Gregory
    This endpoint returns a list of available fiat currencies that can be paired with the @from_currency parameter.  
    @from_currency : str - you must specify a currency to see what currencies it can be compared against.
    """
    response = requests.get(f"{API_BASE_URL}{from_currency.upper()}") 
    data = response.json()
    output = []
    for k in data['rates'].keys():
        output.append(k)
    currencies = {
        from_currency : output
    }

    return currencies

# @CODE : ADD ENDPOINT TO GET LIST OF CRYPTO CURRENCIES
# You can use this API https://docs.cloud.coinbase.com/sign-in-with-coinbase/docs/api-currencies
# Search for the endpoint that returns all the crypto currencies.
@app.get("/available_crypto")
async def available_crypto() -> dict:
    """
    Coded by: Xavier Higa  
    This endpoint allows you to see what crypto-currencies are available  
    """
    response = requests.get('https://api.coinbase.com/v2/currencies/crypto')
    output = []
    if response.status_code == 200:
        fResponse = response.json()['data']
        for v in fResponse:
            output.append(v['code'])
        return {'data': output}
    
# @CODE : ADD ENDPOINT TO GET Price of crypto
# Use the coinbase API from above
@app.get("/convert_crypto")
async def convert_crypto(from_crypto: str, to_currency: str) -> dict:
    """
    Coded by: Ihovanna Huezo  
    This endpoint allows you to get a quote for a crypto in any supported currency  
    @from_crypto - chose a crypto currency (eg. BTC, or ETH)  
    @to_currency - chose a currency to obtain the price in (eg. USD, or CAD)  
    """
    currency_pair = f"{from_crypto.upper()}-{to_currency.upper()}"
    response = requests.get(f"https://api.coinbase.com/v2/prices/{currency_pair}/buy") 
    data = response.json()["data"]
    price_amount = round(float(data["amount"]), 2)

    return {
        "crypto_type": from_crypto.upper(),
        "price_currency": to_currency.upper(),
        "price_amount": price_amount
    }

# @CODE : ADD ENDPOINT TO UPDATE PRICE OF ASSET IN ORDERBOOK DB
# The code below starts you off using SQLAlchemy ORM
# Dependencies should already be installed from your requirements.txt file
# Using the ORM instead of raw SQL is safer and less coupled: it is best practice!
@app.get("/update_orderbookdb_asset_price")
async def update_orderbookdb_asset_price(symbol: str, new_price: float) -> dict:
    """
    Coded by: <name>  
    This endpoint allows us to update the price of the assets in the app  
    @symbol - pick a symbol to update the price of in the orderbook app  
    @new_price - The new price of the symbol  
    """
    
    # import sqlalchemy
    from sqlalchemy import create_engine, Table, Column, String, DateTime, Numeric, update, MetaData
    from sqlalchemy.orm import sessionmaker
    
    # create an engine for building sessions
    engine = create_engine('mysql+pymysql://wiley:wiley123@orderbookdb/orderbook')

    # create an ORM object that maps to the Product table
    metadata = MetaData()
    product_table = Table('Product', metadata,
        Column('symbol', String(16), primary_key=True),
        Column('price', Numeric(precision=15, scale=2)),
        Column('productType', String(12)),
        Column('name', String(128)),
        Column('lastUpdate', DateTime)
    )
    metadata.create_all(engine)

    # create a database session maker
    Session = sessionmaker(bind=engine)

    try:
        # Instantiate the session
        session = Session()
        # create the statement to udpate
        stmt = update(product_table).where(product_table.c.symbol == symbol).values(price=new_price)
        # execute commit and flush the statement
        session.execute(stmt)
        session.commit()
        session.flush()
        return {"update_report": "success", "symbol": symbol, "new_price": new_price}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="An error occurred, make sure symbol exists and price is numeric")
    finally:
        session.close()

    
# @CODE : ADD ENDPOINT FOR INSERTING A CRYPTO CURRENCY INTO THE ORDERBOOK APP
# HINT: Make use of the convert_crypto function from above! 
#       You will need to use the await keyword to wait for the result (otherwise it will run async and not wait for the result)
#@app.get("/add_crypto_to_orderbook")
#async def add_crypto_to_orderbook(symbol: str) -> dict:
#    """
#     Coded by: <name>  
#     This endpoint uses the `convert_crypto` function above to get the price of a crypto-currency  
#     and inserts that currency and price into the orderbook database 
#    """
# @app.get("/add_crypto_to_orderbook")
# async def add_crypto_to_orderbook(symbol: str) -> dict:
#    """
#     Coded by: <name>  
#     This endpoint uses the `convert_crypto` function above to get the price of a crypto-currency  
#     and inserts that currency and price into the orderbook database 
#    """
#    from sqlalchemy import create_engine, Table, Column, String, DateTime, Numeric, MetaData
#    from sqlalchemy.orm import sessionmaker
#    
#    # create an engine for building sessions
#    engine = create_engine('mysql+pymysql://wiley:wiley123@orderbookdb/orderbook')#
#
#    # create an ORM object that maps to the Product table
#    metadata = MetaData()
#    product_table = Table('Product', metadata,
#        Column('symbol', String(16), primary_key=True),
#        Column('price', Numeric(precision=15, scale=2)),
#        Column('productType', String(12)),
#        Column('name', String(128)),
#        Column('lastUpdate', DateTime)
#    )
#    metadata.create_all(engine)

    # create a database session maker
#    Session = sessionmaker(bind=engine)
#
#    try:
#        # Instantiate the session
#        session = Session()
#        # create the statement to udpate
#        # stmt = update(product_table).where(product_table.c.symbol == symbol).values(price=new_price)
#        price = await convert_crypto(symbol, 'USD')['amount']
#        stmt = session.insert(product_table).values(product_table.c.symbol = symbol, product_table.c.price = price, product_table.c.productType='Crypto', product_table.c.name=symbol)
#        # execute commit and flush the statement
#        session.execute(stmt)
#        session.commit()
#        session.flush()
#        return {"update_report": "success", "symbol": symbol, "new_price": new_price}
#    except Exception as e:
#        print(e)
#        raise HTTPException(status_code=400, detail="An error occurred, make sure symbol exists and price is numeric")
#    finally:
#        session.close()

