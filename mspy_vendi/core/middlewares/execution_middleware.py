import time

from fastapi import Request, Response


async def measure_execution_time(request: Request, call_next) -> Response:
    """
    Middleware to measure the execution time of a request.
    """
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = f"{process_time:.2f} s"

    return response
