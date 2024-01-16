import multiprocessing
import sys
from time import sleep
from datetime import datetime, time
from logging import INFO

from coinquant.event import EventEngine
from coinquant.trader.setting import SETTINGS
from coinquant.trader.engine import MainEngine

from coinquant_okx import OkxGateway
from coinquant_ctastrategy import CtaStrategyApp
from coinquant_ctastrategy.base import EVENT_CTA_LOG


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True


okx_setting = {
    "API Key": "",
    "Secret Key": "",
    "Passphrase": "",
    "代理地址": "",
    "代理端口": "",
    "服务器": ""
}


# Chinese futures market trading period (day/night)
DAY_START = time(8, 45)
DAY_END = time(15, 0)

NIGHT_START = time(20, 45)
NIGHT_END = time(2, 45)


def check_trading_period():
    """"""
    # current_time = datetime.now().time()

    # trading = False
    # if (
    #     (current_time >= DAY_START and current_time <= DAY_END)
    #     or (current_time >= NIGHT_START)
    #     or (current_time <= NIGHT_END)
    # ):
    #     trading = True

    return True


def run_child():
    """
    Running in the child process.
    """
    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(OkxGateway)
    cta_engine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    main_engine.connect(okx_setting, "OKX")
    main_engine.write_log("连接OKX接口")

    sleep(10)

    cta_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    cta_engine.init_all_strategies()
    sleep(60)   # Leave enough time to complete strategy initialization
    main_engine.write_log("CTA策略全部初始化")

    cta_engine.start_all_strategies()
    main_engine.write_log("CTA策略全部启动")

    while True:
        sleep(10)

        trading = check_trading_period()
        if not trading:
            print("关闭子进程")
            main_engine.close()
            sys.exit(0)


def run_parent():
    """
    Running in the parent process.
    """
    print("启动CTA策略守护父进程")

    child_process = None

    while True:
        trading = check_trading_period()

        # Start child process in trading period
        if trading and child_process is None:
            print("启动子进程")
            child_process = multiprocessing.Process(target=run_child)
            child_process.start()
            print("子进程启动成功")

        # 非记录时间则退出子进程
        if not trading and child_process is not None:
            if not child_process.is_alive():
                child_process = None
                print("子进程关闭成功")

        sleep(5)


if __name__ == "__main__":
    run_parent()
