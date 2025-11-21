import pandas as pd
import numpy as np
import os

def process_data():
    print("Iniciando Processamento de Dados")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "../data/aapl_history.csv")
    output_path = os.path.join(base_dir, "../data/aapl_processed.csv")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    df = pd.read_csv(input_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date').sort_index()

    # Feature Engineering 
    
    # target com retorno logarítmico (melhor pra ML do que preço bruto)
    # log return estabiliza a variância
    df['Log_Ret'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # médias móveis (tendência)
    df['SMA_7'] = df['Close'].rolling(window=7).mean()
    df['SMA_21'] = df['Close'].rolling(window=21).mean()
    
    # volatilidade (risco recente)
    df['Volatility_7'] = df['Log_Ret'].rolling(window=7).std()

    # lags 
    for lag in [1, 2, 3, 5]:
        df[f'Lag_{lag}'] = df['Log_Ret'].shift(lag)

    # variáveis de data (sazonalidade semanal/mensal)
    df['Day_of_Week'] = df.index.dayofweek
    df['Month'] = df.index.month

    # definição do target
    # prever o retorno do dia seguinte (t+1)
    # se target > 0 o preço subiu, se < 0 caiu
    df['Target'] = df['Log_Ret'].shift(-1)

    df_clean = df.dropna()
    df_clean = df_clean.drop(columns=['Unnamed: 0'])

    print(f"Features criadas: {list(df_clean.columns)}")
    print(f"Linhas originais: {len(df)} -> Linhas processadas: {len(df_clean)}")

    df_clean.to_csv(output_path)
    print(f"CSV Processado salvo em: {output_path}")

if __name__ == "__main__":
    process_data()