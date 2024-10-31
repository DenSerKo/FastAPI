from fastapi import FastAPI
import asyncio
import aiohttp

app = FastAPI()
task_queue = asyncio.Queue()
num_consumers = 3  # Количество потребителей

# Продюсер добавляет задачи в очередь каждые несколько секунд
async def producer():
    while True:
        # Пример задачи — запрос к JSONPlaceholder для получения данных о постах
        url = "https://jsonplaceholder.typicode.com/posts/1"
        await task_queue.put(url)
        print(f"Produced task for URL: {url}")
        await asyncio.sleep(5)  # Интервал между задачами

# Потребители получают URL и делают HTTP запросы
async def consumer(queue: asyncio.Queue, consumer_id: int):
    async with aiohttp.ClientSession() as session:
        while True:
            url = await queue.get()
            if url is None:
                print(f"Consumer {consumer_id} shutting down.")
                queue.task_done()
                break
            print(f"Consumer {consumer_id} processing URL: {url}")
            async with session.get(url) as response:
                data = await response.json()
                print(f"Consumer {consumer_id} received data: {data}")
            queue.task_done()

@app.on_event("startup")
async def startup_event():
    # Запускаем продюсера
    asyncio.create_task(producer())
    # Запускаем несколько потребителей
    for i in range(num_consumers):
        asyncio.create_task(consumer(task_queue, i + 1))

@app.on_event("shutdown")
async def shutdown_event():
    await task_queue.join()  # Ждем, пока все задачи в очереди будут выполнены
    # Отправляем сигнал завершения для каждого потребителя
    for _ in range(num_consumers):
        await task_queue.put(None)
    print("All tasks have been processed, consumers shutting down.")
