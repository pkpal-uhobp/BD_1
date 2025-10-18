import aiohttp
import asyncio
import time

async def fetch_question(session, topic_id, semaphore):
    async with semaphore:
        url = "https://palchevsky.ru/index.php"
        params = {"rest_route": "/qa/v1/random-question", "topic_id": topic_id}
        headers = {"X-WP-Nonce": "1ac565fdb1"}
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                data = await response.json()
                print(f"Ответ: {data}")
                return data
        except Exception as e:
            error_msg = {"error": str(e)}
            print(f"Ошибка: {error_msg}")
            return error_msg

async def main():
    semaphore = asyncio.Semaphore(1000)
    async with aiohttp.ClientSession() as session:
        tasks1 = [fetch_question(session, 416, semaphore) for _ in range(1000)]
        results = await asyncio.gather(*tasks1)
        # tasks2 = [fetch_question(session, 418, semaphore) for _ in range(1000)]
        # results = await asyncio.gather(*tasks2)
        # tasks3 = [fetch_question(session, 420, semaphore) for _ in range(1000)]
        # results = await asyncio.gather(*tasks3)
        # tasks4 = [fetch_question(session, 421, semaphore) for _ in range(1000)]
        # results = await asyncio.gather(*tasks4)
    
    print(f"Выполнено {len(results)} запросов")
asyncio.run(main())
