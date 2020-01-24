from typing import Any
from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager
)
from vnpy.trader.object import(
    BarData,
    TickData
)

class DemoStrategy(CtaTemplate):
    """"""

    author = "用Python的交易员"

    fast_windows = 10
    slow_windows = 20

    fa_ma0 = 0
    sl_ma0 = 0
    fa_ma1 = 0
    sl_ma1 = 0

    parameters = [
        "fast_windows",
        "slow_windows"
    ]
    variables = [
        "fa_ma0",
        "sl_ma0",
        "fa_ma1",
        "sl_ma1"
    ]
    def __init__(
        self, 
        cta_engine: Any,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,
    ):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar)#把tick合称为K线
        self.am = ArrayManager()#生成出来的一根根的K线放到一个容器当中

    def on_init(self):
        """初始化"""
        self.write_log("策略初始化开始")
        self.load_bar(10)

    def on_start(self):
        """启动"""
        self.write_log("启动")

    def on_stop(self, parameter_list):
        """停止"""
        self.write_log("停止")

    def on_tick(self, tick: TickData):
        """tick更新"""
        self.bg.update_tick(tick)

    def on_bar(self, bar:BarData):
        """K线更新"""
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return #检测am是否满足初始化要求，比如数量够不够啊之类的

        #计算技术指标
        fast_ma = am.sma(self.fast_windows, array=True)
        #sma计算窗口均值,array=True是返回一个数组结果--不仅仅是最新的那个点
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]

        slow_ma = am.sma(self.slow_windows, array=True)
        #sma计算窗口均值,array=True是返回一个数组结果--不仅仅是最新的那个点
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]

        #判断均线交叉
        cross_over = (self.fast_ma0 >= self.slow_ma0 and 
                      self.fast_ma1 < self.slow_ma1)
        
        cross_below = (self.fast_ma0 <= self.slow_ma0 and 
                      self.fast_ma1 > self.slow_ma1)

        if cross_over:
            price = bar.close_price + 5#加5块是随便写的
            if not self.pos:
                self.buy(price, 1)
            elif self.pos < 0:
                self.cover(price, 1)
                self.buy(price, 1)
        elif cross_below:
            price = bar.close_price - 5
            if not self.pos:
                self.short(price, 1)
            elif self.pos > 0:
                self.sell(price, 1)
                self.short(price, 1)

        #更新图形界面
        self.put_event()



        
        