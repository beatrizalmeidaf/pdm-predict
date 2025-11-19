import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
symbol = "AAPL"

if API_KEY is None:
    raise ValueError("ERRO: ALPHAVANTAGE_API_KEY não encontrada no .env")

url = (
    f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
    f"&symbol={symbol}&outputsize=full&apikey={API_KEY}"
)

r = requests.get(url)
data = r.json()

if "Time Series (Daily)" in data:

    df = pd.DataFrame(data["Time Series (Daily)"]).T
    
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df = df.apply(pd.to_numeric)
    df.index = pd.to_datetime(df.index)

    # ultimos 12 meses
    data_limite = datetime.now() - timedelta(days=365)
    df = df[df.index >= data_limite].sort_index()

    print(f"Dados de {df.index.min().date()} até {df.index.max().date()}")
    print(f"Total de linhas: {len(df)}")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    data_dir = os.path.join(base_dir, "../data")
    save_path = os.path.join(data_dir, "aapl_history.csv")

    os.makedirs(data_dir, exist_ok=True)  

    df.to_csv(save_path)
    print(f"CSV salvo em: {save_path}")

else:
    print("Erro na API")
