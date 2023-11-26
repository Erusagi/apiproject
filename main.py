import aiohttp
import asyncio
import argparse
from datetime import datetime, timedelta

class PrivatBankAPI:
    BASE_URL = "https://api.privatbank.ua/p24api/"

    @classmethod
    async def get_exchange_rate(cls, currency, date):
        async with aiohttp.ClientSession() as session:
            async with session.get(cls.BASE_URL + f"pubinfo?json&exchange&coursid=5&date={date}") as response:
                data = await response.json()

                for item in data:
                    if item["ccy"] == currency:
                        return {
                            'sale': float(item['sale']),
                            'purchase': float(item['buy'])
                        }

        raise ValueError(f"Exchange rate for {currency} on {date} not found.")

async def get_currency_rates(days):
    today = datetime.now()
    date_format = "%d.%m.%Y"
    currency_codes = ['USD', 'EUR']
    results = []

    async def fetch_and_append(date):
        rates = {}

        for currency_code in currency_codes:
            rate = await PrivatBankAPI.get_exchange_rate(currency_code, date.strftime(date_format))
            rates[currency_code] = rate

        results.append({date.strftime(date_format): rates})

    tasks = [fetch_and_append(today - timedelta(days=day)) for day in range(1, days + 1)]
    await asyncio.gather(*tasks)

    return results

def main():
    parser = argparse.ArgumentParser(description="Get currency rates from PrivatBank API.")
    parser.add_argument("days", type=int, help="Number of days to retrieve currency rates (max: 10)")

    args = parser.parse_args()

    if not 1 <= args.days <= 10:
        print("Error: Number of days should be between 1 and 10.")
        return

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(get_currency_rates(args.days))
    print(result)

if __name__ == "__main__":
    main()