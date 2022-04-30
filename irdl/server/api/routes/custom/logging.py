import datetime
from typing import Callable
import time

from fastapi import Request, Response
from fastapi.routing import APIRoute

from .....utils.logger import Logger


class LoggingRoute(APIRoute):

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            print('custom_route_handler')
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = round(time.time() - before, 4)

            record = {}
            if await request.body():
                record["request_body"] = (await request.body()).decode("utf-8")
            record["request_headers"] = {
                k.decode("utf-8"): v.decode("utf-8") for (k, v) in request.headers.raw
            }
            record["remote_addr"] = request.client.host
            record["request_uri"] = request.url.path
            record["request_method"] = request.method
            record["request_time"] = f'{duration}s'
            record["status"] = response.status_code
            # record["response_body"] = response.body.decode("utf-8")
            record["response_headers"] = {
                k.decode("utf-8"): v.decode("utf-8") for (k, v) in response.headers.raw
            }
            Logger.i('LoggingRoute', record)
            return response

        return custom_route_handler
