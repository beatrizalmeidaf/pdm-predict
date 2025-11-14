import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import os


def setup_driver():
    servico = Service(ChromeDriverManager().install())
    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    opcoes.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(service=servico, options=opcoes)
    driver.implicitly_wait(5)
    return driver


def extrair_reviews_produto(url_produto, driver):
    dados_reviews = []
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(url_produto)
        print(f"Abrindo produto: {url_produto[:50]}...")
    except Exception as e:
        print(f"Erro ao abrir URL do produto: {e}")
        return []

    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2.5);")
        time.sleep(1.5)
    except:
        pass

    pagina_review_atual = 1
    max_paginas_review = 10

    while pagina_review_atual <= max_paginas_review:
        print(f"Lendo página {pagina_review_atual} de reviews")

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#reviews_capability_v3")))
        except TimeoutException:
            print("Timeout: seção de reviews não carregou.")
            break

        reviews_na_pagina = driver.find_elements(By.CSS_SELECTOR,
            "#reviews_capability_v3 article.ui-review-capability-comments__comment"
        )

        if not reviews_na_pagina:
            reviews_na_pagina = driver.find_elements(
                By.CSS_SELECTOR, "#reviews_capability_v3 article.ui-review-capability__media"
            )

        if not reviews_na_pagina:
            reviews_na_pagina = driver.find_elements(
                By.CSS_SELECTOR, "#reviews_capability_v3 div.ui-review-capability-comments article"
            )

        if not reviews_na_pagina:
            print("Nenhum review encontrado.")
            break

        print(f"Encontrado {len(reviews_na_pagina)} reviews.")

        for i, review in enumerate(reviews_na_pagina):
            nota, texto = None, None

            try:
                nota_match = re.search(r'\d+', review.find_element(By.CSS_SELECTOR, "p.andes-visually-hidden").text)
                if nota_match:
                    nota = int(nota_match.group(0))
            except NoSuchElementException:
                continue

            seletores_texto = [
                "p.ui-review-capability-comments__comment__content",
                "p.ui-review-capability__review-description",
                "p.ui-review-capability__summary__description"
            ]

            for sel in seletores_texto:
                try:
                    texto = review.find_element(By.CSS_SELECTOR, sel).text.strip()
                    break
                except NoSuchElementException:
                    continue

            if nota and texto and len(texto) > 1:
                dados_reviews.append({"Nota": nota, "Texto": texto})

                print(f"     - Review salvo. Nota {nota} | {texto[:40]}...")

        # próxima página
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.andes-pagination__button--next a")
            driver.execute_script("arguments[0].click();", next_button)
            pagina_review_atual += 1
            time.sleep(2)
        except:
            print("Fim dos reviews.")
            break

    return dados_reviews


def pegar_links_produtos(driver):
    links = []

    seletores = [
        "li.ui-search-layout__item div.ui-search-result__content a.ui-search-link",
        "div.poly-card__content h3 a",
        "a.ui-search-link"
    ]

    for seletor in seletores:
        try:
            produtos = driver.find_elements(By.CSS_SELECTOR, seletor)
            if produtos:
                for p in produtos:
                    href = p.get_attribute("href")
                    if href and ("/p/" in href or "/MLB" in href):
                        links.append(href)
                return list(set(links))
        except:
            pass

    return links


def scrape_um_termo(termo_busca, driver, max_paginas_lista=3):
    reviews_termo = []

    for i in range(max_paginas_lista):
        offset = 1 + (i * 50)
        termo_url = termo_busca.replace(" ", "-")

        if i == 0:
            url_lista = f"https://lista.mercadolivre.com.br/{termo_url}"
        else:
            url_lista = f"https://lista.mercadolivre.com.br/{termo_url}_Desde_{offset}"

        print(f"\nAcessando lista: {url_lista}")

        try:
            driver.get(url_lista)
            WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.poly-card"))
                )
            )
        except TimeoutException:
            print("Falha ao carregar lista.")
            break

        links = pegar_links_produtos(driver)
        if not links:
            continue

        for link in links:
            reviews_produto = extrair_reviews_produto(link, driver)
            reviews_termo.extend(reviews_produto)

    return reviews_termo


LISTA_DE_TERMOS = [
    "smartwatch",
    "caixa de som bluetooth",
    "alexa echo dot",
    "carregador portátil",
    "kindle",
    "celular samsung",
    "iphone 14",
    "teclado sem fio",
    "mouse sem fio",
    "chromecast",
    "notebook dell",
    "monitor gamer",
    "cadeira gamer",
    "ssd 1tb",
    "placa de video rtx 3060",
    "air fryer",
    "cafeteira expresso",
    "liquidificador",
    "panela de pressão elétrica",
    "robô aspirador"
]

META_REVIEWS = 1500
PAGINAS_DA_LISTA_POR_TERMO = 3

print("Iniciando o driver...")
driver = setup_driver()
todos_os_reviews = []

try:
    for termo in LISTA_DE_TERMOS:
        print(f"\nBuscando por: {termo.upper()}")
        dados_termo = scrape_um_termo(termo, driver, PAGINAS_DA_LISTA_POR_TERMO)
        todos_os_reviews.extend(dados_termo)

        print(f"Total coletado até agora: {len(todos_os_reviews)}")

        if len(todos_os_reviews) >= META_REVIEWS:
            print("Meta atingida. Parando a coleta.")
            break

finally:
    print("Fechando navegador...")
    driver.quit()

if todos_os_reviews:
    print(f"\nColeta finalizada. Total de {len(todos_os_reviews)} reviews.")
    df_final = pd.DataFrame(todos_os_reviews)
    
    df_final = df_final.drop_duplicates(subset=['Texto'])
    print(f"Total de {len(df_final)} reviews únicos.")

    os.makedirs("../data", exist_ok=True)
    caminho_final = "../data/reviews_mercadolivre.csv"
    
    df_final.to_csv(caminho_final, index=False)
    
    print(f"\nDataFrame salvo com sucesso em '{caminho_final}'!")
    print(df_final.head())

else:
    print("Nenhum review foi coletado.")