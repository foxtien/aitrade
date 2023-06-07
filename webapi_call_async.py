import aiohttp
import asyncio
import json

async def fetch_stock_price(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    while True:
        async with aiohttp.ClientSession() as session:
            data = await fetch_stock_price(session, 'http://localhost:5000/api/stock_price')
            print(data)  # 打印即時股票資訊
        await asyncio.sleep(1)  # 暫停1秒，等待下一次更新

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
