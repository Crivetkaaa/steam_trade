import requests
import time
import hashlib


class GLO:
    key = 'C8F9C72EA0B3490D871809F46E7B0F2C'
    seller = 1193548


def price_to_rub(game_price:float, language:str):
    valute = requests.get("https://www.cbr-xml-daily.ru/daily_json.js").json()
    if language == 'us' or language == 'md':
        value = float(valute['Valute']['USD']['Value'])/(valute['Valute']['USD']['Nominal'])
    elif language == 'kz':
        value = valute['Valute']['KZT']['Value']/(valute['Valute']['KZT']['Nominal'])
    elif language == 'ua':
        value = valute['Valute']['UAH']['Value']/(valute['Valute']['UAH']['Nominal'])
    price = float(game_price)*float(value)
    return price


def get_price_ru(game_id:int, i:int, language:str):
    info = requests.get(f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc={language}")
    data = info.json()
    game_price = data[game_id[0:-1]]['data']['package_groups'][0]['subs'][i]['price_in_cents_with_discount']
    if language != 'ru':
        game_price = price_to_rub(game_price, language)
    return game_price


def new_prices(price):
    str_prices = str(price)
    if str_prices[-1] == "0":
        return price-1
    else:
        return int(str_prices[0:-1]+'9')    

def post_price(product_id:int, new_price:float, percent:int):
    prices = int(new_price*((100+percent)/10000))
    data = {
    "price": {
        "price": new_prices(prices),
        "currency": "RUB"
        }
    }
    requests.post(url=f'https://api.digiseller.ru/api/product/edit/uniquefixed/{product_id}?token={token}', json=data)
    print(new_prices(prices))
    
def product_cycle(product_info:list, game_id:int):
    i = 0
    while i < len(product_info):
        if '_' == product_info[i] :
            i += 1
        else:
            product_id, product_language, percent = product_info[i].split(':')
            game_price = get_price_ru(game_id, i, product_language)
            post_price(product_id, game_price, int(percent))
            i += 1


def encode_sha256(input_string):
    encoded_string = input_string.encode('utf-8')
    sha256_hash = hashlib.sha256(encoded_string).hexdigest()
    return sha256_hash


def generate_token():
    times = time.time()
    input_string = GLO.key + f"{int(times)}"
    sign = encode_sha256(input_string)

    data = {
        "seller_id": GLO.seller,
        "timestamp": times,
        "sign": sign
    }

    responce = requests.post('https://api.digiseller.ru/api/apilogin', json=data)
    print(responce.json())
    token = responce.json()['token']
    print(token)
    return token


def get_from_file():
    with open('id_list.txt', 'r', encoding='utf-8') as file:
        data = file.readlines()
    return data


if __name__ == "__main__":
    token = generate_token()
    data = get_from_file()

    for line in data:
        products_info, game_id = line.split('-')
        try:
            products_info = products_info.split(',')
        except:
            products_info = products_info
        product_cycle(products_info, game_id)