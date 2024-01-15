from freqtrade.strategy.interface import IStrategy
import pandas as pd

class VmaStrategy(IStrategy):
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy.
    timeframe = '15m'

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    minimal_roi = {
        "120": 0.01,
        "60": 0.02,
        "0": 0.04
    }

    # Optimal stoploss designed for the strategy.
    stoploss = -0.05

    # Trailing stoploss
    trailing_stop = True
    trailing_only_offset_is_reached = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Strategy parameters
    buy_rsi = IntParameter(20, 50, default=30, space="buy")
    sell_rsi = IntParameter(50, 80, default=70, space="sell")

    # Optional order type mapping.
    order_types = {
        'entry': 'market',
        'exit': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'GTC',
        'exit': 'GTC'
    }
    
    # Al usar ordenes de mercado para la entrada especificamos "other"
    entry_pricing = {
        'price_side' : 'other'
    }
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        l = 21  # Longitud de la VMA ajustada a 21
        k = 1.0 / l  # Factor de suavizado

        # Cálculo de Positive Difference Maxima (PDM) y Negative Difference Maxima (MDM)
        dataframe['pdm'] = (dataframe['close'] - dataframe['close'].shift(1)).clip(lower=0)
        dataframe['mdm'] = (dataframe['close'].shift(1) - dataframe['close']).clip(lower=0)

        # Suavización de PDM y MDM
        dataframe['pdm_smooth'] = dataframe['pdm'].ewm(alpha=k, adjust=False).mean()
        dataframe['mdm_smooth'] = dataframe['mdm'].ewm(alpha=k, adjust=False).mean()

        # Suma de PDM y MDM suavizados
        s = dataframe['pdm_smooth'] + dataframe['mdm_smooth']

        # Índices de movimiento (PDI y MDI)
        dataframe['pdi'] = dataframe['pdm_smooth'] / s
        dataframe['mdi'] = dataframe['mdm_smooth'] / s

        # Suavización de PDI y MDI
        dataframe['pdi_smooth'] = dataframe['pdi'].ewm(alpha=k, adjust=False).mean()
        dataframe['mdi_smooth'] = dataframe['mdi'].ewm(alpha=k, adjust=False).mean()

        # Diferencia y suma de PDI y MDI suavizados
        d = abs(dataframe['pdi_smooth'] - dataframe['mdi_smooth'])
        s1 = dataframe['pdi_smooth'] + dataframe['mdi_smooth']

        # Cálculo de IS
        dataframe['is'] = (d / s1).ewm(alpha=k, adjust=False).mean()

        # Determinar el máximo y mínimo de IS en la ventana l
        hhv = dataframe['is'].rolling(window=l).max()
        llv = dataframe['is'].rolling(window=l).min()

        # Cálculo de VI
        d1 = hhv - llv
        dataframe['vi'] = (dataframe['is'] - llv) / d1

        # Cálculo final de VMA
        dataframe['vma'] = ((1 - k * dataframe['vi']) * dataframe['vma'].shift(1)) + (k * dataframe['vi'] * dataframe['close'])

        # Añadiendo el RSI personalizado
        length = 14
        delta = dataframe['close'].diff()
        up = delta.clip(lower=0).ewm(span=length, adjust=False).mean()
        down = -delta.clip(upper=0).ewm(span=length, adjust=False).mean()
        dataframe['rsi'] = 100 - (100 / (1 + up / down))

        return dataframe

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['vma']) &  # El precio cruza por encima de la VMA
                (dataframe['close'].shift(1) <= dataframe['vma'].shift(1)) &  # Confirmación del cruce en el período anterior
                (dataframe['rsi'] < 66)  # RSI por debajo de 66 para evitar entrar en sobrecompra
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['vma']) &  # El precio cruza por debajo de la VMA
                (dataframe['close'].shift(1) >= dataframe['vma'].shift(1)) &  # Confirmación del cruce en el período anterior
                (dataframe['rsi'] > 70)  # RSI en sobrecompra
            ),
            'exit_long'] = 1

        return dataframe