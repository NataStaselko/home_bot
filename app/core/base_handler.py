import aiohttp
import asyncio


class ErrorRequest(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Handler:
    def __init__(
        self,
        method="GET",
        url="",
        params=None,
        data=None,
        data_name="json",
        headers=None,
        timeout=30,
        max_retries=3,
        normal_status_codes=range(200, 205),
    ):
        self.method = method
        self.url = url
        self.params = params
        self.data = data
        self.data_name = data_name
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.headers = headers or {"Content-Type": "application/json"}
        self.max_retries = max_retries
        self.normal_status_codes = normal_status_codes

    def _prepare_request_params(self):
        request_params = {
            "method": self.method,
            "url": self.url,
            "timeout": self.timeout,
            "headers": self.headers,
        }
        if self.params:
            request_params["params"] = self.params
        if self.data:
            request_params[self.data_name] = self.data
        return request_params

    async def _process_response(self, resp, response_type):
        if resp.status in self.normal_status_codes:
            if response_type == "json":
                return await resp.json(content_type=None)
            elif response_type == "text":
                return await resp.text()
            elif response_type == "content":
                return await resp.read()
        else:
            raise ValueError(f"Unexpected status code: {resp.status}")

    async def request(self, response_type="json"):
        params = self._prepare_request_params()
        for attempt in range(1, self.max_retries + 1):
            try:
                async with aiohttp.request(**params) as resp:
                    return await self._process_response(resp, response_type)
            except Exception as e:
                print(f"Attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(attempt)