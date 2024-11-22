import requests
import pandas as pd
import streamlit as st

st.set_page_config(layout='wide')
st.title('Monitoramento das Proposições Legislativas PRIORITÁRIAS da Câmara dos Deputados')

st.text("Os projetos prioritários são: PL 987/2022, PL 327/2021, PL 11247/2018, PL 624-A/2023, PL 6211/2019")
st.text("PL 868/2020, PL 2780/2024, PL 2159/2021, PL 669/2023, PL 4975/2023, PL 3149/2020, PL 3335/2024")

# Lista dos projetos de lei para acompanhar, com número e ano
projetos_lista = [
    {"numero": 987, "ano": 2022},
    {"numero": 327, "ano": 2021},
    {"numero": 11247, "ano": 2018},
    {"numero": 624, "ano": 2023},
    {"numero": 6211, "ano": 2019},
    {"numero": 868, "ano": 2020},
    {"numero": 2780, "ano": 2024},
    {"numero": 2159, "ano": 2021},
    {"numero": 669, "ano": 2023},
    {"numero": 4975, "ano": 2023},
    {"numero": 3149, "ano": 2020},
    {"numero": 3335, "ano": 2024}
]

# Inicializar lista para armazenar dados dos projetos encontrados
projetos = []

# Iterar sobre a lista de projetos e fazer requisições
for projeto in projetos_lista:
    url = "https://dadosabertos.camara.leg.br/api/v2/proposicoes"
    params = {
        "numero": projeto["numero"],
        "ano": projeto["ano"],
        "siglaTipo": "PL"
    }
    response = requests.get(url, params=params, headers={'Cache-Control': 'no-cache'})

    if response.status_code == 200:
        dados = response.json()["dados"]
        if dados:
            proposicao = dados[0]  # Seleciona o primeiro resultado, que é o projeto desejado
            id_proposicao = proposicao['id']

            # Obter situação de tramitação da proposição
            url_tramitacoes = f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id_proposicao}/tramitacoes"
            response_tramitacoes = requests.get(url_tramitacoes)

            if response_tramitacoes.status_code == 200:
                tramitacoes = response_tramitacoes.json()['dados']
                if tramitacoes:
                    ultima_tramitacao = tramitacoes[-1]
                    proposicao['situacaoTramitacao'] = ultima_tramitacao['descricaoSituacao']
                    proposicao['dataUltimaTramitacao'] = ultima_tramitacao['dataHora']  # Adiciona a data da última tramitação
                else:
                    proposicao['situacaoTramitacao'] = "Sem tramitações registradas"
                    proposicao['dataUltimaTramitacao'] = "Sem data registrada"

                # Adicionar link para página da proposição na Câmara dos Deputados
                proposicao['link'] = f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={id_proposicao}"
                projetos.append(proposicao)
            else:
                st.write(f"Erro ao obter tramitações para proposição {id_proposicao}: {response_tramitacoes.status_code}")
        else:
            st.write(f"Nenhum Projeto de Lei encontrado para o número {projeto['numero']} de {projeto['ano']}.")
    else:
        st.write(f"Erro ao fazer requisição para a API: {response.status_code}")

# Exibir resultados em um DataFrame se projetos foram encontrados
if projetos:
    colunas = ['siglaTipo', 'numero', 'ano', 'ementa', 'situacaoTramitacao', 'dataUltimaTramitacao', 'link']
    df = pd.DataFrame(projetos, columns=colunas)
    # Configurar a coluna de link como clique em Streamlit
    df['link'] = df['link'].apply(lambda x: f"{x}")
    st.dataframe(df)
