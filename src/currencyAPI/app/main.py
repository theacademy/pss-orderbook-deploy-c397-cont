from fastapi import FastAPI, HTTPException
import requests
 
app = FastAPI()
 
API_BASE_URL = "https://api.exchangerate-api.com/v4/latest/"
COINBASE_API_URL = "https://api.coinbase.com/v2/currencies/crypto"
COINBASE_RATES = "https://api.coinbase.com/v2/exchange-rates/"
COINBASE_FIAT = "https://api.coinbase.com/v2/currencies"
 

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
  

@app.get("/check_password_strength")
async def check_password_strength(password: str) -> dict:
    p_uppercase = any(char.isupper() for char in password)
    p_lowercase = any(char.islower() for char in password)
    p_digit = any(char.isdigit() for char in password)
    plength = len(password) >= 8
 
    return {
        "User_has_strong_password": p_uppercase and p_lowercase and p_digit and plength
    }
    # Coded by  Philip Hushani
 

@app.get("/available_currencies")
async def available_currencies() -> dict:
    try:
        response = requests.get(COINBASE_FIAT)
        if response.status_code == 200:
            data = response.json()
            available_currencies = [currency["id"] for currency in data["data"]]
            return {"available_currencies": available_currencies}
        else:
            raise HTTPException(status_code=400, detail="From currency not supported")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
 
#Coded by: Alexander Naskinov

@app.get("/available_crypto")
async def available_crypto() -> dict:
    
    #Coded by: Bette Beament
    #This endpoint allows you to see what crypto-currencies are available
    
    try:
        response = requests.get(COINBASE_API_URL)
        if response.status_code == 200:
            data = response.json()
            crypto_currencies = [currency["code"] for currency in data["data"]]
            return {"crypto_currencies": crypto_currencies}
        else:
            raise HTTPException(status_code=400, detail="Failed to fetch crypto currencies")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def get_usd_rate() -> dict:
    # """
    # Coded by: Tomasz Wisniewski
    # This endpoint allows you to see what crypto-currencies are available
    # """
    response = requests.get(f"{COINBASE_RATES}")
    if response.status_code == 200:
        data = response.json()
        return data["data"]
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch crypto rate")
   
@app.get("/convert_crypto")
async def convert_crypto(from_crypto: str, to_currency: str, amount: float) -> dict:
    # """
    # Coded by: Tomasz Wisniewski
    # This endpoint allows you to see what crypto-currencies are available
    # """
    crypto_rate = await get_usd_rate()
    ex_rate = await exchange_rate(to_currency, "USD")
    rate_to_USD = float(ex_rate["exchange_rate"])
    rate_from_USD = float(crypto_rate['rates'][from_crypto])
    rate_crypto = rate_to_USD * rate_from_USD
    converted_amount = (1/rate_crypto)* amount
    print(rate_to_USD)
    print(rate_from_USD)
    return {
        "crypto_currency": from_crypto.upper(),
        "fiat_currency": to_currency.upper(),
        "crypto_rate": rate_crypto,
        "amount": amount,
        "converted_amount": converted_amount,
    }
 
#@CODE : ADD ENDPOINT TO UPDATE PRICE OF ASSET IN ORDERBOOK DB
#The code below starts you off using SQLAlchemy ORM
#Dependencies should already be installed from your requirements.txt file
#Using the ORM instead of raw SQL is safer and less coupled: it is best practice!
 
@app.get("/update_orderbookdb_asset_price")
async def update_orderbookdb_asset_price(symbol: str, new_price: float) -> dict:
    # """
    # Coded by: Tomasz Wisniewski
    # This endpoint allows you to see what crypto-currencies are available
    # """
    from sqlalchemy import create_engine, Table, Column, String, DateTime, Numeric, update, MetaData
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('mysql+pymysql://wiley:wiley123@a11e83d0d11d64c75a070bf9a91b8c6c-1320554700.us-east-1.elb.amazonaws.com/orderbook')
    metadata = MetaData()
    product_table = Table('Product', metadata,
        Column('symbol', String(16), primary_key=True),
        Column('price', Numeric(precision=15, scale=2)),
        Column('productType', String(12)),
        Column('name', String(128)),
        Column('lastUpdate', DateTime)
    )
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    try:
        session = Session()
        stmt = update(product_table).where(product_table.c.symbol == symbol).values(price=new_price)
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
 
@app.get("/add_crypto_to_orderbook")
async def add_crypto_to_orderbook(crypto: str) -> dict:
    # """
    # Coded by: Tomasz Wisniewski
    # This endpoint allows you to see what crypto-currencies are available
    # """
    from sqlalchemy import create_engine, Table, Column, String, DateTime, Numeric, insert, MetaData
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime
    from decimal import Decimal
    engine = create_engine('mysql+pymysql://wiley:wiley123@a11e83d0d11d64c75a070bf9a91b8c6c-1320554700.us-east-1.elb.amazonaws.com/orderbook')
    crypto_data = await convert_crypto(crypto, "USD", 1)
    #crypto_price = float(crypto_data["crypto_rate"])
    crypto_price = Decimal(crypto_data["crypto_rate"]).quantize (Decimal ('.01'))
    try:
        metadata = MetaData()
        orderbook_table = Table('Product', metadata,
            Column('symbol', String(16), primary_key=True),
            Column('price', Numeric(precision=15, scale=2)),
            Column('productType', String(12)),
            Column('name', String(128)),
            Column('lastUpdate', DateTime)
        )
      
        metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        #stmt = orderbook_table(symbol=crypto, price=crypto_price, productType=productT, name=crypto, lastUpdate=datetime.now().replace(microsecond=0))
        stmt = insert(orderbook_table).values(symbol=crypto, price=crypto_price, productType="crypto", name=crypto, lastUpdate=datetime.now().replace(microsecond=0))
        session.execute(stmt)
        session.commit()
        session.flush()
        return {"insert_report": "success", "symbol": crypto}
    except Exception as e:
        raise HTTPException(status_code=400, detail="An error occurred while inserting into orderbook")
 