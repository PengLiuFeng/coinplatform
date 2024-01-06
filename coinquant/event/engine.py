"""
myleap 的事件驱动框架
"""

from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from time import sleep
from typing import Any, Callable, List

EVENT_TIMER = "eTimer"


class Event:
    """
    事件对象由事件引擎用于分发事件的类型字符串和包含实际数据的数据对象组成。
    """

    def __init__(self, type: str, data: Any = None) -> None:
        """"""
        self.type: str = type
        self.data: Any = data


# Defines handler function to be used in event engine.
HandlerType: callable = Callable[[Event], None]


class EventEngine:
    """
    事件引擎根据事件对象的类型将事件对象分发给已注册的处理程序。

    它还以每间隔秒为单位生成计时器事件,可用于计时目的。
    """

    def __init__(self, interval: int = 1) -> None:
        """
        如果没有指定interval,定时器事件默认每1秒产生一次。
        """
        self._interval: int = interval
        self._queue: Queue = Queue()
        self._active: bool = False
        self._thread: Thread = Thread(target=self._run)
        self._timer: Thread = Thread(target=self._run_timer)
        self._handlers: defaultdict = defaultdict(list)
        self._general_handlers: List = []

    def _run(self) -> None:
        """
        从队列中获取事件，然后处理它。
        """
        while self._active:
            try:
                event: Event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event: Event) -> None:
        """
        首先将事件分发给那些注册侦听此类型的处理程序。

        然后将事件分发给侦听所有类型的通用处理程序。
        """
        if event.type in self._handlers:
            [handler(event) for handler in self._handlers[event.type]]

        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def _run_timer(self) -> None:
        """
        按间隔秒(s)休眠，然后生成计时器事件。
        """
        while self._active:
            sleep(self._interval)
            event: Event = Event(EVENT_TIMER)
            self.put(event)

    def start(self) -> None:
        """
        启动事件引擎来处理事件并生成定时器事件。
        """
        self._active = True
        self._thread.start()
        self._timer.start()

    def stop(self) -> None:
        """
        停止事件引擎。
        """
        self._active = False
        self._timer.join()
        self._thread.join()

    def put(self, event: Event) -> None:
        """
        将一个事件对象放入事件队列。
        """
        self._queue.put(event)

    def register(self, type: str, handler: HandlerType) -> None:
        """
        为特定的事件类型注册新的处理程序函数。每个函数对于每种事件类型只能注册一次。
        """
        handler_list: list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type: str, handler: HandlerType) -> None:
        """
        从事件引擎注销现有的处理程序函数。
        """
        handler_list: list = self._handlers[type]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            self._handlers.pop(type)

    def register_general(self, handler: HandlerType) -> None:
        """
        为所有事件类型注册一个新的处理程序函数。每个函数对于每种事件类型只能注册一次。
        """
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler: HandlerType) -> None:
        """
        取消注册现有的通用处理程序函数。
        """
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)
