from datetime import datetime
from typing import Callable, Optional, List
import requests
import pytz
import json

from coinquant.trader.datafeed import BaseDatafeed
from coinquant.trader.setting import SETTINGS
from coinquant.trader.constant import Interval
from coinquant.trader.object import BarData, HistoryRequest


INTERVAL_VT2CA = {
    Interval.MINUTE: "1MIN",
    Interval.MINUTE3: "3MIN",
    Interval.MINUTE5: "5MIN",
    Interval.MINUTE15: "15MIN",
    Interval.MINUTE30: "30MIN",
    Interval.HOUR: "1HRS",
    Interval.HOUR2: "2HRS",
    Interval.DAILY: "1DAY",
    Interval.TICK: 0
}

UTC_TZ = pytz.utc

COINAPI_HOST = "https://rest.coinapi.io"


def to_ca_symbol(symbol, exchange):
    """将交易所代码转换为CoinAPI代码"""
    return f"{exchange.value}_{symbol}".upper()


class CoinapiDatafeed(BaseDatafeed):
    """CoinAPI数据服务接口"""

    def __init__(self):
        """"""
        self.password: str = SETTINGS["datafeed.password"]

    def query_bar_history(self, req: HistoryRequest,output: Callable = print) -> Optional[List[BarData]]:
        """查询k线数据"""
        symbol = req.symbol
        exchange = req.exchange
        interval = req.interval
        start = req.start
        end = req.end

        symbol_id = to_ca_symbol(symbol, exchange)
        period_id = INTERVAL_VT2CA[interval]
        time_start = datetime.strftime(start, "%Y-%m-%dT%H:%M:%S")
        time_end = datetime.strftime(end, "%Y-%m-%dT%H:%M:%S")

        url = COINAPI_HOST + f"/v1/ohlcv/{symbol_id}/history?"
        params = {
            "period_id": period_id,
            "time_start": time_start,
            "time_end": time_end
        }
        headers = {'X-CoinAPI-Key': self.password}

        response = requests.request(
            method="GET",
            url=url,
            params=params,
            headers=headers
        )

        if response.status_code != 200:
            print(response.text)
            return None

        bars: List[BarData] = []
        
        data = json.loads(response.text)
        for d in data:
            dt = datetime.strptime(d["time_period_start"], "%Y-%m-%dT%H:%M:%S.%f0Z")
            dt = UTC_TZ.localize(dt)

            bar = BarData(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                datetime=dt,
                open_price=d["price_open"],
                high_price=d["price_high"],
                low_price=d["price_low"],
                close_price=d["price_close"],
                volume=d["volume_traded"],
                gateway_name="CA",
            )
            bars.append(bar)

        return bars
