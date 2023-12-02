from freqtrade.strategy.interface import IStrategy
import pandas as pd

class VmaStrategy(IStrategy):

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

    def populate_buy_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['vma']) &  # El precio cruza por encima de la VMA
                (dataframe['close'].shift(1) <= dataframe['vma'].shift(1)) &  # Confirmación del cruce en el período anterior
                (dataframe['rsi'] < 66)  # RSI por debajo de 66 para evitar entrar en sobrecompra
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['vma']) &  # El precio cruza por debajo de la VMA
                (dataframe['close'].shift(1) >= dataframe['vma'].shift(1)) &  # Confirmación del cruce en el período anterior
                (dataframe['rsi'] > 70)  # RSI en sobrecompra
            ),
            'sell'] = 1

        return dataframe