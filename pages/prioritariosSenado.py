import requests
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

st.set_page_config(layout='wide')
st.title('Monitoramento das Proposições Legislativas PRIORITÁRIAS no Senado')

st.text("Os projetos prioritários são: PL 987/2022, PL 327/2021, PL 11247/2018, PL 624/2023, PL 6211/2019")
st.text("PL 868/2020, PL 2780/2024, PL 2159/2021, PL 669/2023, PL 4975/2023, PL 3149/2020, PL 3335/2024")

# URL base para acessar as matérias
BASE_URL = "https://legis.senado.leg.br/dadosabertos/materia"

# Função para obter detalhes e situação de uma matéria
def obter_detalhes_e_situacao(sigla, numero, ano):
    # Detalhes da matéria
    url_detalhes = f"{BASE_URL}/{sigla}/{numero}/{ano}"
    response_detalhes = requests.get(url_detalhes)
    detalhes = {}

    if response_detalhes.status_code == 200:
        try:
            # Parse XML
            root = ET.fromstring(response_detalhes.content)
            materia = root.find("Materia")
            if materia is not None:
                # Dados básicos
                identificacao = materia.find("IdentificacaoMateria")
                dados_basicos = materia.find("DadosBasicosMateria")
                codigo_materia = identificacao.find("CodigoMateria").text if identificacao is not None else None
                
                detalhes.update({
                    "siglaTipo": identificacao.find("SiglaSubtipoMateria").text if identificacao is not None else "N/A",
                    "numero": identificacao.find("NumeroMateria").text if identificacao is not None else "N/A",
                    "ano": identificacao.find("AnoMateria").text if identificacao is not None else "N/A",
                    "ementa": dados_basicos.find("EmentaMateria").text if dados_basicos is not None else "N/A",
                    "link": f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{codigo_materia}" if codigo_materia else "N/A"
                })
        except Exception as e:
            print(f"Erro ao processar o XML de detalhes: {e}")
    else:
        print(f"Erro na requisição dos detalhes ({response_detalhes.status_code}): {url_detalhes}")
        return None

    # Situação atual
    codigo_materia = detalhes.get("link").split("/")[-1] if "link" in detalhes else None
    if codigo_materia:
        url_situacao = f"{BASE_URL}/movimentacoes/{codigo_materia}"
        response_situacao = requests.get(url_situacao)
        if response_situacao.status_code == 200:
            try:
                # Parse XML
                root = ET.fromstring(response_situacao.content)
                situacao_atual = root.find(".//SituacaoAtual")
                if situacao_atual is not None:
                    # Adicionar situação atual ao dicionário de detalhes
                    detalhes.update({
                        "DataSituacao": situacao_atual.find("DataSituacao").text if situacao_atual.find("DataSituacao") is not None else "N/A",
                        "DescricaoSituacao": situacao_atual.find("DescricaoSituacao").text if situacao_atual.find("DescricaoSituacao") is not None else "N/A"
                    })
            except Exception as e:
                print(f"Erro ao processar o XML de situação atual: {e}")
        else:
            print(f"Erro na requisição da situação atual ({response_situacao.status_code}): {url_situacao}")
    return detalhes

# Lista de projetos a serem consultados
projetos_lista = [
    {"numero": 987, "ano": 2022},
    {"numero": 327, "ano": 2021},
    {"numero": 11247, "ano": 2018},
    {"numero": 624, "ano": 2023},
    {"numero": 6211, "ano": 2019},
    {"numero": 868, "ano": 2020},
    {"numero": 2780, "ano": 2024},
    {"numero": 2159, "ano": 2021},
    {"numero": 699, "ano": 2023},
    {"numero": 4975, "ano": 2023},
    {"numero": 3149, "ano": 2020},
    {"numero": 3335, "ano": 2024},
]

# Lista para armazenar os dados obtidos
dados_projetos = []

# Iterando sobre a lista de projetos e obtendo as informações
for projeto in projetos_lista:
    resultado = obter_detalhes_e_situacao("PL", projeto['numero'], projeto['ano'])
    if resultado:
        dados_projetos.append(resultado)  # Adiciona o dicionário de resultados à lista


# Criando o DataFrame com os resultados obtidos
df_projetos = pd.DataFrame(dados_projetos)

# Exibindo o DataFrame
df_projetos = df_projetos[['siglaTipo', 'numero', 'ano', 'ementa', 'DescricaoSituacao', 'DataSituacao', 'link']]

st.dataframe(df_projetos)
