## Coleta de Dados da Apple (AAPL) via API — Alpha Vantage

A Alpha Vantage é uma API pública que fornece dados do mercado financeiro, incluindo preços históricos de ações.
Nesse notebook coletamos o histórico diário da Apple (AAPL) dos últimos 12 meses.

--- 
### Significado de cada coluna

| Coluna           | Descrição                                                                                                                                     |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Index (Data)** | A data de negociação (YYYY-MM-DD).                                                                                                            |
| **Open**         | Preço de abertura: valor da ação quando o mercado abriu (09:30 NY).                                                                      |
| **High**         | Preço máximo: maior valor pago pela ação durante o dia.                                                                                  |
| **Low**          | Preço mínimo: menor valor atingido pelo ativo naquele dia.                                                                               |
| **Close**        | Preço de fechamento: quanto valia a ação no final do pregão. <br>*Target do modelo de Machine Learning para previsão.* |
| **Volume**       | Quantidade total de ações negociadas no dia. <br>Volumes altos indicam forte interesse ou notícias relevantes.                                |
