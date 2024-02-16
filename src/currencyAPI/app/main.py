from fastapi import FastAPI, HTTPException
import requests
 
app = FastAPI()
 
API_BASE_URL = "https://api.exchangerate-api.com/v4/latest/"
COINBASE_API_URL = "https://api.coinbase.com/v2/currencies/crypto"
COINBASE_RATES = "https://api.coinbase.com/v2/exchange-rates/"
 
 

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
 
@app.get("/available_currencies")
async def available_currencies() -> dict:
    try:
        response = requests.get(API_BASE_URL)
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
 
async def get_crypto_rate(crypto_currency: str, fiat_currency: str) -> float:
    response = requests.get(f"{COINBASE_RATES}{crypto_currency}-{fiat_currency}")
    if response.status_code == 200:
        data = response.json()
        return float(data["data"]["rates"]["value"])
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch crypto rate")
   
@app.get("/convert_crypto")
async def convert_crypto(from_crypto: str, to_currency: str, amount: float) -> dict:
#    """
#    Coded by: Tomasz Wisniewski
#    This endpoint allows you to get a quote for a crypto in any supported currency  
#    @from_crypto - chose a crypto currency (eg. BTC, or ETH)  
#    @to_currency - chose a currency to obtain the price in (eg. USD, or CAD)  
#    """
    crypto_rate = await get_crypto_rate(from_crypto, to_currency)
    converted_amount = amount * crypto_rate
    return {
        "crypto_currency": from_crypto.upper(),
        "fiat_currency": to_currency.upper(),
        "crypto_rate": crypto_rate,
        "amount": amount,
        "converted_amount": converted_amount,
    }