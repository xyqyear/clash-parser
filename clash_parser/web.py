import asyncio
import logging
import os
from io import StringIO

from aiohttp import ClientSession, web

from .config import Config
from .parsing import process_yaml

working_dir = os.environ.get("PARSER_WORKING_DIR")
if working_dir:
    os.chdir(working_dir)

HOST = os.environ.get("PARSER_HOST")
if not HOST:
    HOST = "localhost"
PORT = os.environ.get("PARSER_PORT")
if not PORT:
    PORT = 8080
elif PORT.isdigit():
    PORT = int(PORT)
else:
    logging.error("PARSER_PORT must be an integer")
    exit(1)

config = Config("config.yaml")

logging.basicConfig(level=logging.INFO)
routes = web.RouteTableDef()


async def get(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            response_headers = response.headers
            response_text = await response.text()
            return response_headers, response_text


async def parse_with_url(profile_url, reload_config=True):
    if not (parser := config.get_parser_for_url(profile_url)):
        return web.Response(status=404)

    profile_get_task = asyncio.create_task(get(profile_url))
    tasks = [profile_get_task]
    if reload_config:
        config_load_task = asyncio.create_task(config.load())
        tasks.append(config_load_task)

    try:
        await asyncio.wait(tasks)
    except Exception as e:
        logging.warning(e)
        return web.Response(status=500)
    original_headers, profile = profile_get_task.result()

    buffer = StringIO()
    try:
        process_yaml(profile, parser, buffer)
    except Exception as e:
        logging.warning(e)
        return web.Response(status=500)

    headers = {'subscription-userinfo': original_headers.get('subscription-userinfo', '')}
    return web.Response(text=buffer.getvalue(), headers=headers)


@routes.get("/parse")
async def parse(request):
    return await parse_with_url(request.rel_url.query["url"])


@routes.get("/s/{short_url}")
async def parse_short(request):
    await config.load()
    short_url = request.match_info["short_url"]
    if (profile_url := config.get_full_url(short_url)) is None:
        return web.Response(status=404)
    return await parse_with_url(profile_url, reload_config=False)


@routes.put("/update")
async def update(request):
    profile_url = request.rel_url.query["url"]
    body = await request.text()

    if config.find_index(profile_url) == -1:
        return web.Response(status=404)

    config.update_parser_for_url(profile_url, body)

    asyncio.ensure_future(config.save())
    return web.Response(status=200)


@routes.post("/add")
async def add(request):
    query = request.rel_url.query
    if "url" in query:
        profile_url = query["url"]
        body = await request.text()
        config.add_parser(profile_url, body)
    elif "reg" in query:
        profile_reg = query["reg"]
        body = await request.text()
        config.add_parser_regex(profile_reg, body)
    else:
        return web.Response(status=400)

    asyncio.ensure_future(config.save())
    return web.Response(status=200)


@routes.delete("/remove")
async def remove(request):
    profile_url = request.rel_url.query["url"]
    config.remove_parser_for_url(profile_url)
    asyncio.ensure_future(config.save())
    return web.Response(status=200)


def run():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host=HOST, port=PORT)
