# Estrategia VMA con RSI para Freqtrade

## Descripción
La estrategia `VmaStrategy` utiliza la Variable Moving Average (VMA) combinada con el Relative Strength Index (RSI) para identificar oportunidades de trading en criptomonedas. Esta estrategia está diseñada para operar en marcos temporales variados y busca capturar tendencias basándose en el cruce del precio con la VMA y las condiciones de sobrecompra/sobreventa indicadas por el RSI.

## Características
- **Variable Moving Average (VMA):** Utiliza el precio y el volumen para calcular un promedio móvil más representativo de la tendencia del mercado.
- **Relative Strength Index (RSI):** Mide la magnitud de los movimientos recientes para evaluar condiciones de sobrecompra o sobreventa.
- **Señales de Compra:** Generadas cuando el precio cruza la VMA de abajo hacia arriba y el RSI está por debajo de 66, indicando un potencial inicio de tendencia alcista sin estar en sobrecompra.
- **Señales de Venta:** Se emiten cuando el precio cruza la VMA de arriba hacia abajo y el RSI está por encima de 70, sugiriendo el final de una tendencia alcista o una condición de sobrecompra.

## Uso
La estrategia está diseñada para ser utilizada con el bot de trading Freqtrade. Se recomienda realizar backtesting exhaustivos y ajustar los parámetros según las necesidades y características del mercado antes de su uso en trading en vivo.

## Pruebas y Optimización
Es vital realizar pruebas de backtesting para entender el rendimiento de la estrategia en diferentes condiciones de mercado. Además, la optimización de parámetros como la longitud del RSI y los umbrales de sobrecompra/sobreventa puede ayudar a mejorar los resultados.

## Riesgos
Como en cualquier estrategia de trading, existe el riesgo de pérdidas. Se recomienda una comprensión completa de los riesgos y la utilización de medidas de gestión de riesgos como stop loss y trailing stops.

---

*Esta estrategia es proporcionada con fines educativos y no debe considerarse como asesoramiento financiero.*
