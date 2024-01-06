from coinquant.event import EventEngine
from coinquant.trader.engine import MainEngine
from coinquant.trader.ui import MainWindow, create_qapp

from coinquant_ctastrategy import CtaStrategyApp
from coinquant_ctabacktester import CtaBacktesterApp

from coinquant_okx import OkxGateway

from coinquant_datamanager import DataManagerApp
#from coinquant_datarecorder import DataRecorderApp

def main():
    """主入口函数"""
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(DataManagerApp)
    #main_engine.add_app(DataRecorderApp)
    main_engine.add_gateway(OkxGateway)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()