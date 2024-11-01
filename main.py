from fastapi import FastAPI
import asyncio
import aiohttp

app = FastAPI()
task_queue = asyncio.Queue()
num_consumers = 3


async def fetch(queue, session, url):
    async with session.get(url) as response:
        content = await response.text()
        await queue.put((url, content))


async def fetcher(queue, urls):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch(queue, session, url)) for url in urls]
        await asyncio.gather(*tasks)
    for _ in range(num_consumers):
        await queue.put(None)


async def consumer(queue: asyncio.Queue, results):
    while True:
        data = queue.get()
        if data is None:
            queue.task_done()
            break
        url, content = data
        results[url] = content


@app.get('/')
async def root():
    # results1 = {}
    # queue = asyncio.Queue()
    # urls = [f'https://jsonplaceholder.typicode.com/posts/{i}' for i in range(3)]
    # producer = asyncio.create_task(fetcher(queue, urls))
    # consumers = [asyncio.create_task(consumer(queue, results1)) for _ in range(num_consumers)]
    # await producer
    # await queue.join()
    # await asyncio.gather(*consumers)
    # return results1
    return {'message': 'Hello from fast api!'}


@app.get('/hello/{name}')
async def hello(name: str):
    return {'message': f'I love you, {name}'}


@app.get('/posts/{year}')
async def posts(year: str):
    posts = {}
    for i in range(10):
        posts[f'post{i}'] = f'Post {i} in year {year}'
    return posts
