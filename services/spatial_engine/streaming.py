"""Request-local SSE transport for the existing synchronous layout harness."""

import asyncio
import logging
import threading
from collections.abc import AsyncIterator, Awaitable, Callable

from anyio.to_thread import run_sync
from pydantic import BaseModel

from contracts.schema import (
    AuditReport,
    LayoutProgress,
    LayoutStreamError,
    OptimiseRequest,
)
from services.spatial_engine.agent import (
    LayoutCancelled,
    LayoutModel,
    ProgressCallback,
    propose_layout,
)
from services.spatial_engine.chat import ChatRequest, chat
from services.spatial_engine.layout_tools import LayoutToolbox

logger = logging.getLogger(__name__)


def solve_events(
    request: OptimiseRequest,
    model: LayoutModel | None,
    interpreter: LayoutModel | None,
    prepared: LayoutToolbox,
    *,
    disconnected: Callable[[], Awaitable[bool]] | None = None,
    heartbeat_s: float = 10.0,
) -> AsyncIterator[str]:
    return execution_events(
        lambda progress, cancelled: propose_layout(
            request,
            model,
            interpreter=interpreter,
            prepared=prepared,
            progress=progress,
            cancelled=cancelled,
        ),
        disconnected=disconnected,
        heartbeat_s=heartbeat_s,
    )


def chat_events(
    request: ChatRequest,
    model: LayoutModel | None,
    prepared: AuditReport,
    *,
    disconnected: Callable[[], Awaitable[bool]] | None = None,
) -> AsyncIterator[str]:
    return execution_events(
        lambda progress, cancelled: chat(
            request,
            model,
            prepared=prepared,
            progress=progress,
            cancelled=cancelled,
        ),
        disconnected=disconnected,
    )


async def execution_events(
    execute: Callable[[ProgressCallback, Callable[[], bool]], BaseModel],
    *,
    disconnected: Callable[[], Awaitable[bool]] | None = None,
    heartbeat_s: float = 10.0,
) -> AsyncIterator[str]:
    """Stop future work on disconnect; an active SDK call retains its existing timeout."""
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[tuple[str, BaseModel]] = asyncio.Queue()
    stop = threading.Event()

    def publish(event: str, data: BaseModel) -> None:
        if stop.is_set():
            raise LayoutCancelled()
        loop.call_soon_threadsafe(queue.put_nowait, (event, data))

    def progress(update: LayoutProgress) -> None:
        publish("progress", update)

    def work() -> None:
        try:
            result = execute(progress, stop.is_set)
            publish("result", result)
        except LayoutCancelled:
            return
        except Exception as exc:
            # Never send raw exceptions, provider content or request data to the client.
            logger.error("Unexpected layout stream failure (%s)", type(exc).__name__)
            if not stop.is_set():
                publish(
                    "error",
                    LayoutStreamError(
                        message=("The layout request failed. Your room has not changed. Try again.")
                    ),
                )

    worker = asyncio.create_task(run_sync(work, abandon_on_cancel=True))
    try:
        while True:
            if disconnected is not None and await disconnected():
                return
            try:
                event, data = await asyncio.wait_for(queue.get(), timeout=heartbeat_s)
            except TimeoutError:
                yield ": keep-alive\n\n"
                continue
            yield f"event: {event}\ndata: {data.model_dump_json()}\n\n"
            if event != "progress":
                return
    finally:
        stop.set()
        worker.cancel()
        await asyncio.gather(worker, return_exceptions=True)
