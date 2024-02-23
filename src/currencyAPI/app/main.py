from fastapi import FastAPI, HTTPException
import requests
from datetime import *
 
app = FastAPI()
 
API_BASE_URL = "https://api.exchangerate-api.com/v4/latest/"
COINBASE_API_URL = "https://api.coinbase.com/v2/currencies/crypto"
COINBASE_RATES = "https://api.coinbase.com/v2/exchange-rates/"
COINBASE_FIAT = "https://api.coinbase.com/v2/currencies"
FREECURRENCYAPI = "https://api.freecurrencyapi.com/v1/historical?apikey=fca_live_7dHeSfDiffz0YIQcp86XBN45JExNt6GHsDY9n5m0"
 

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
   
    #coded by: Philip Hushani
    specialc = '!@£$%^#&*()_-~?><'
    p_uppercase = any(char.isupper() for char in password)
    p_lowercase = any(char.islower() for char in password)
    p_digit = any(char.isdigit() for char in password)
    plength = len(password) >= 8
    special_c = any(char in specialc for char in password)
 
    return {
        "User_has_strong_password": p_uppercase and p_lowercase and p_digit and plength and special_c
    }


@app.get("/available_currencies")
async def available_currencies() -> dict:
    try:
        response = requests.get(f"{API_BASE_URL}USD")
        if response.status_code == 200:
            data = response.json()
            base_currency = data["base"]
            available_currencies = list(data["rates"].keys())
            return {"base_currency": base_currency, "available_currencies": available_currencies}
        else:
            raise HTTPException(status_code=400, detail="Failed to fetch available currencies")
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
            crypto_currencies = [{"Crypto ID :": currency["code"], "Crypto name : ": currency["name"]} for currency in data["data"]]
            return {"Crypto curriences :": crypto_currencies}
        else:
            raise HTTPException(status_code=400, detail="Failed to fetch crypto currencies")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
 
async def get_usd_rate() -> dict:
    # """
    # Coded by: Tomasz Wisniewski
    # This function downloads rates for USD currency.
    # """
    response = requests.get(f"{COINBASE_RATES}")
    if response.status_code == 200:
        data = response.json()
        return data["data"]
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch USD rates")
   
@app.get("/convert_crypto")
async def convert_crypto(from_crypto: str, to_currency: str, amount: float) -> dict:
    # """
    # Coded by: Bette Beaument
    # This endpoint allows you to convert crypto into any currency.
    # """
    try:
        check_result = await check_crypto(from_crypto)
        if "error_message" in check_result:
            raise HTTPException(status_code=404, detail=check_result["error_message"])
 
        crypto_rate = await get_usd_rate()
        ex_rate = await exchange_rate(to_currency, "USD")
        rate_to_USD = float(ex_rate["exchange_rate"])
        rate_from_USD = float(crypto_rate['rates'][from_crypto])
        rate_crypto = rate_to_USD * rate_from_USD
        converted_amount = (1 / rate_crypto) * amount
        return {
            "crypto_currency": from_crypto.upper(),
            "fiat_currency": to_currency.upper(),
            "crypto_rate": rate_crypto,
            "amount": amount,
            "converted_amount": converted_amount,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

 
#@CODE : ADD ENDPOINT TO UPDATE PRICE OF ASSET IN ORDERBOOK DB
#The code below starts you off using SQLAlchemy ORM
#Dependencies should already be installed from your requirements.txt file
#Using the ORM instead of raw SQL is safer and less coupled: it is best practice!
 
@app.get("/update_orderbookdb_asset_price")
async def update_orderbookdb_asset_price(symbol: str, new_price: float) -> dict:
    # """
    # Coded by: Tomasz Wisniewski
    # This endpoint allows you to update price of asset in orderbook database.
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
 
 
async def get_crypto_name(crypto_n: str) -> str:
    # """
    # Coded by: Tomasz Wisniewski
    # This function downloads all crypto names and extract required name.
    # """
    get_crypto_names = await available_crypto()
    if get_crypto_names.status_code == 200:
        crypto_names = get_crypto_names["Crypto curriences :"]
        for crypto_name in crypto_names:
            if crypto_name["Crypto ID :"] == crypto_n:
                c_name = crypto_name["Crypto name : "]
                return c_name
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch crypto name")
       
# @CODE : ADD ENDPOINT FOR INSERTING A CRYPTO CURRENCY INTO THE ORDERBOOK APP
# HINT: Make use of the convert_crypto function from above!
#       You will need to use the await keyword to wait for the result (otherwise it will run async and not wait for the result)
@app.get("/add_crypto_to_orderbook")
    # """
    # Coded by: Tomasz Wisniewski
    # This endpoint will insert a crypto currency into the orderbook app.
    # """
async def add_crypto_to_orderbook(crypto: str) -> dict:
    from sqlalchemy import create_engine, Table, Column, String, DateTime, Numeric, insert, MetaData
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime
    from decimal import Decimal
    engine = create_engine('mysql+pymysql://wiley:wiley123@a11e83d0d11d64c75a070bf9a91b8c6c-1320554700.us-east-1.elb.amazonaws.com/orderbook')
    crypto_data = await convert_crypto(crypto, "USD", 1)
    c_name = await get_crypto_name(crypto)
    crypto_price = Decimal(1/crypto_data["crypto_rate"]).quantize (Decimal ('.01'))
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
        stmt = insert(orderbook_table).values(symbol=crypto, price=crypto_price, productType=c_name, name=crypto, lastUpdate=datetime.now().replace(microsecond=0))
        session.execute(stmt)
        session.commit()
        session.flush()
        return {"insert_report": "success", "symbol": crypto}
    except Exception as e:
        raise HTTPException(status_code=400, detail="An error occurred while inserting into orderbook")
    finally:
        session.close()

@app.get("/check_crypto")
async def check_crypto(crypto_param: str) -> dict:
   
    # Coded by: Alex Naskinov
    # This endpoint checks if a given crypto currency is available for trade
    # Supports querying by either crypto ID or crypto name
   
    try:
        response = requests.get(COINBASE_API_URL)
        if response.status_code == 200:
            data = response.json()
            crypto_codes = [currency["code"] for currency in data["data"]]
            crypto_names = [currency["name"] for currency in data["data"]]
            
            if crypto_param in crypto_codes or crypto_param in crypto_names:
                return {"message": "This crypto currency is tradable"}
            else:
                return {"error_message": "This crypto currency is not tradable"}
        else:
            raise HTTPException(status_code=400, detail="Failed to fetch crypto currencies")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/compare_currencies")
async def compare_currencies(currency_1: str, currency_2: str) -> dict:
    try:
        currency_1 = currency_1.upper()  # Convert to uppercase
        currency_2 = currency_2.upper()  # Convert to uppercase

        response = requests.get(f"{API_BASE_URL}/{currency_1}")
        if response.status_code == 200:
            data = response.json()
            base_currency = data["base"]
            conversion_rates = data["rates"]

            if currency_2 not in conversion_rates:
                return {"error": f"{currency_2} not found in exchange rates."}

            currency_1_value = conversion_rates.get(currency_1, None)
            currency_2_value = conversion_rates[currency_2]

            if currency_1_value is None:
                return {"error": f"{currency_1} not found in exchange rates."}

            if currency_2_value < 1:
                message = f"{currency_2} is more valuable than {currency_1} compared to {base_currency}."
            elif currency_2_value > 1:
                message = f"{currency_1} is more valuable than {currency_2} compared to {base_currency}."
            else:
                message = f"{currency_1} and {currency_2} have the same value compared to {base_currency}."

            return {"result": "success", "message": message}
        else:
            raise HTTPException(status_code=400, detail="Failed to fetch exchange rates.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_historical_data(currency: str) -> dict:
    # """
    # Coded by: Tomasz Wisniewski
    # This function downloads historical rate against USD for required currency.
    # """
    response = requests.get(f"{FREECURRENCYAPI}&base_currency=USD&currencies={currency}")
    if response.status_code == 200:
        data = response.json()
        return data["data"]
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch USD the historical data")
 
@app.get("/check_yesterdays_price")
async def check_yesterdays_price(currency: str) -> dict:
    # """
    # Coded by: Tomasz Wisniewski and Bette Beament
    # This endpoint will compare current price with the price from previous day against USD
    # """
    y_day = []
    today_d = date.today()
    y_day.append(today_d - timedelta(days = 1))
    yesterday = y_day[0]
    try:
        old_data = await get_historical_data(currency)
        old_price = old_data[str(yesterday)][currency.upper()]
        #print(old_data)
        new_data = await exchange_rate("USD", currency)
        new_price = new_data['exchange_rate']
 
        if old_price > new_price:
            return {"message": f"{currency} is worth more than yesterday (in USD)."}
        if old_price < new_price:
            return {"message": f"{currency} is worth less than yesterday (in USD)."}
        else:
            return {"message": f"{currency} price hasn't change since yesterday (in USD)."}
       
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="An error occurred while receiving data")


@app.post("/track-portfolio")
async def track_portfolio(holdings: dict):
    if "holdings" not in holdings:
        raise HTTPException(status_code=400, detail="Invalid request")
 
    total_portfolio_value = calculate_portfolio_value(holdings["holdings"])
 
    return {"total_portfolio_value in GBP": total_portfolio_value}
 
def calculate_portfolio_value(holdings: dict) -> float:
    total_value = 0.0
    exchange_rates = {
        'USD': 0.79,
        'EUR': 0.85,
        'GBP': 1,
        'JPY': 0.0052,
        'AUD': 0.52,
        'CAD': 0.59  
    }
 
    for currency, amount in holdings.items():
        if currency not in exchange_rates:
            raise HTTPException(status_code=400, detail=f"Invalid currency: {currency}")
 
        exchange_rate = exchange_rates[currency]
        total_value += amount * exchange_rate
    return total_value