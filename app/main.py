import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(
    page_title="Dashboard Produtividade Obras",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# CARREGAR BASE
# ==================================================
@st.cache_data
def load_data():
    df = pd.read_excel("./data/df_diarios.xlsx")
    return df

df_raw = load_data()

# ==================================================
# FILTRO MÃO DE OBRA
# ==================================================
df = df_raw[df_raw["tipo_insumo"] == "MAO DE OBRA"].copy()

st.warning(
    "Os dados foram filtrados para considerar apenas **mão de obra**, "
    "pois o índice de produtividade (ip_d) mede o desempenho da equipe."
)

# ==================================================
# TRATAMENTO DOS DADOS
# ==================================================
df["ip_d"] = pd.to_numeric(df["ip_d"], errors="coerce")
df = df.dropna(subset=["ip_d"])

df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["data_curta"] = df["data"].dt.date

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("Filtros")

obras = df["nome_obra"].dropna().unique().tolist()
obra_selecionada = st.sidebar.multiselect(
    "Filtrar por obra", obras, default=obras
)

grupos = df["grupo"].dropna().unique().tolist()
grupo_selecionado = st.sidebar.multiselect(
    "Filtrar por serviço", grupos, default=grupos
)

df_filtered = df[df["nome_obra"].isin(obra_selecionada)]

if grupo_selecionado:
    df_filtered = df_filtered[df_filtered["grupo"].isin(grupo_selecionado)]

# ==================================================
# ABAS
# ==================================================
tab1, tab2, tab3 = st.tabs([
    "📊 Dashboard",
    "📚 Dicionário de Dados",
    "🎥 Análise do Vídeo"
])

# ==================================================
# ABA 1 - DASHBOARD
# ==================================================
with tab1:

    st.title("Dashboard de Produtividade em Obras Públicas")

    st.write(
        """
Este dashboard analisa o **índice de produtividade da mão de obra** nas obras presentes
na base de dados. O indicador utilizado é o **ip_d**, que representa o índice de
produtividade diário obtido a partir das medições realizadas nas obras.
"""
    )

    # --------------------------------------
    # CÁLCULO DAS MÉTRICAS
    # --------------------------------------
    media = df_filtered["ip_d"].mean()
    mediana = df_filtered["ip_d"].median()
    moda = df_filtered["ip_d"].mode()[0]

    amplitude = df_filtered["ip_d"].max() - df_filtered["ip_d"].min()
    variancia = df_filtered["ip_d"].var()
    desvio = df_filtered["ip_d"].std()
    cv = (desvio / media) * 100

    # --------------------------------------
    # TENDÊNCIA CENTRAL
    # --------------------------------------
    st.header("Medidas de Tendência Central")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Média", f"{media:.4f}")
        st.caption(
            "Representa o valor médio do índice de produtividade considerando todas as medições da base."
        )

    with col2:
        st.metric("Mediana", f"{mediana:.4f}")
        st.caption(
            "Valor central da distribuição, dividindo os dados em duas partes iguais."
        )

    with col3:
        st.metric("Moda", f"{moda:.4f}")
        st.caption(
            "Valor de produtividade que aparece com maior frequência nos dados analisados."
        )

    st.divider()

    # --------------------------------------
    # DISPERSÃO
    # --------------------------------------
    st.header("Medidas de Dispersão")

    col4, col5, col6, col7 = st.columns(4)

    with col4:
        st.metric("Amplitude", f"{amplitude:.4f}")
        st.caption(
            "Diferença entre o maior e o menor valor de produtividade observado."
        )

    with col5:
        st.metric("Variância", f"{variancia:.4f}")
        st.caption(
            "Mede o quanto os valores de produtividade estão dispersos em relação à média."
        )

    with col6:
        st.metric("Desvio padrão", f"{desvio:.4f}")
        st.caption(
            "Indica, em média, o quanto os valores de produtividade se afastam da média."
        )

    with col7:
        st.metric("Coeficiente de variação", f"{cv:.2f}%")
        st.caption(
            "Mostra o nível de variabilidade da produtividade em relação à média."
        )

    st.divider()

    # --------------------------------------
    # HISTOGRAMA
    # --------------------------------------
    st.subheader("Distribuição da Produtividade")

    fig_hist = px.histogram(
        df_filtered,
        x="ip_d",
        nbins=30
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    # --------------------------------------
    # PRODUTIVIDADE NO TEMPO
    # --------------------------------------
    st.subheader("Produtividade ao Longo do Tempo")

    df_tempo = df_filtered.groupby("data_curta")["ip_d"].mean().reset_index()

    fig_linha = px.line(
        df_tempo,
        x="data_curta",
        y="ip_d",
        markers=True
    )

    st.plotly_chart(fig_linha, use_container_width=True)

    # --------------------------------------
    # PRODUTIVIDADE POR OBRA
    # --------------------------------------
    st.subheader("Produtividade por Obra")

    fig_box = px.box(
        df_filtered,
        x="nome_obra",
        y="ip_d"
    )

    st.plotly_chart(fig_box, use_container_width=True)

    # --------------------------------------
    # PRODUTIVIDADE POR SERVIÇO
    # --------------------------------------
    st.subheader("Produtividade por Serviço")

    fig_servico = px.box(
        df_filtered,
        x="grupo",
        y="ip_d"
    )

    st.plotly_chart(fig_servico, use_container_width=True)

    # --------------------------------------
    # RESPOSTAS A B C D
    # --------------------------------------
    st.header("Análise das Perguntas Orientadoras")

    st.subheader("A) Diferença de produtividade entre obras")

    obra_stats = df_filtered.groupby("nome_obra")["ip_d"].agg(
        media="mean",
        mediana="median",
        desvio="std"
    ).reset_index()

    st.dataframe(obra_stats)

    st.subheader("B) Diferença de produtividade entre serviços")

    grupo_stats = df_filtered.groupby("grupo")["ip_d"].agg(
        media="mean",
        mediana="median",
        desvio="std"
    ).reset_index()

    st.dataframe(grupo_stats)

    st.subheader("C) Relação entre média e mediana")

    comparacao = df_filtered.groupby("nome_obra")["ip_d"].agg(
        media="mean",
        mediana="median"
    ).reset_index()

    st.dataframe(comparacao)

    st.subheader("D) Previsibilidade da produtividade")

    estabilidade = df_filtered.groupby("grupo")["ip_d"].agg(
        media="mean",
        desvio="std"
    ).reset_index()

    estabilidade["coef_var"] = (estabilidade["desvio"] / estabilidade["media"]) * 100

    st.dataframe(estabilidade)

    # --------------------------------------
    # CONCLUSÃO
    # --------------------------------------
    st.header("Conclusão da Análise")

    st.markdown("""
A análise da base de dados permitiu observar o comportamento da produtividade da mão de obra nas obras analisadas.

De modo geral, foi possível identificar que a produtividade apresenta variações entre diferentes obras e também entre diferentes tipos de serviços. Essas diferenças podem estar associadas a fatores operacionais como a complexidade das atividades executadas, o nível de organização do canteiro de obras, a experiência das equipes de trabalho e as condições específicas de cada projeto.

A comparação entre média e mediana indicou que, em alguns casos, essas medidas são bastante próximas, o que sugere uma distribuição relativamente equilibrada dos dados. Em outras situações, diferenças maiores entre esses valores podem indicar a presença de valores extremos ou variações pontuais de produtividade.

A análise do coeficiente de variação também permitiu identificar quais serviços apresentam comportamento mais previsível e quais possuem maior variabilidade. Serviços com menor coeficiente de variação indicam maior estabilidade produtiva, enquanto valores mais elevados indicam maior incerteza e maior dificuldade de previsão no planejamento da obra.

Essas informações são importantes para apoiar processos de planejamento, orçamento e controle de obras, permitindo que gestores compreendam melhor o comportamento da produtividade e tomem decisões mais embasadas.
""")

# ==================================================
# ABA 2 - DICIONÁRIO DE DADOS
# ==================================================
with tab2:

    st.title("Dicionário de Variáveis")

    dados = {
        "Variável":[
            "classe","caderno","grupo","codigo_cc","descricao",
            "unid","nova","codins","insumo","unidins",
            "tipo_insumo","nome_obra","id_ccoi_elemento",
            "id_appropriation_composition","app_inicio","app_fim",
            "qnts","qs","data","qntd_ac","qs_acum","ip_d","ip_acum","elementos"
        ],

        "Tipo":[
            "Qualitativa nominal","Qualitativa nominal","Qualitativa nominal","Qualitativa nominal",
            "Qualitativa nominal","Qualitativa nominal","Qualitativa nominal","Qualitativa nominal",
            "Qualitativa nominal","Qualitativa nominal","Qualitativa nominal","Qualitativa nominal",
            "Qualitativa nominal","Qualitativa nominal","Quantitativa contínua","Quantitativa contínua",
            "Quantitativa contínua","Quantitativa contínua","Quantitativa contínua","Quantitativa contínua",
            "Quantitativa contínua","Quantitativa contínua","Quantitativa contínua","Qualitativa nominal"
        ]
    }

    df_dic = pd.DataFrame(dados)

    st.dataframe(df_dic, use_container_width=True)

# ==================================================
# ABA 3 - VÍDEO
# ==================================================
with tab3:

    st.title("Análise do Vídeo")

    st.subheader("Objetivo do vídeo")

    st.markdown("""
O vídeo apresenta o processo de criação e atualização das composições de custos utilizadas nas tabelas de obras públicas da prefeitura. Essas tabelas servem como referência para elaboração de orçamentos, planejamento e contratação de obras públicas.
""")

    st.subheader("Principais pontos")

    st.markdown("""
- Correção de inconsistências nas tabelas SIURB  
- Inclusão de novos serviços  
- Atualização das composições unitárias  
- Análise comparativa entre tabelas  
- Validação dos dados com o mercado  
- Uso de dados reais de obras para calcular produtividade
""")

    st.subheader("Coeficiente de produtividade")

    st.markdown("""
O coeficiente de produtividade representa a quantidade de recursos necessários para produzir uma unidade de serviço.

Ele é calculado a partir de medições em obras reais, análise estatística dos dados coletados e comparação com outras tabelas de referência. A partir dessas informações é possível definir valores representativos que serão utilizados nas tabelas de composição de custos para elaboração de orçamentos públicos.
""")

    st.subheader("Possíveis perguntas")

    st.markdown("""
- Como são escolhidas as obras utilizadas para coletar dados?
- Quantas medições são necessárias para garantir confiabilidade?
- Como são definidos os pesos usados na comparação entre tabelas?
- Com que frequência essas tabelas são atualizadas?
- Como lidar com diferenças de produtividade entre equipes e condições de obra?
<<<<<<< HEAD
""")
=======
""")
>>>>>>> ced3e81bb36f9ae0e57fd66053a1e2c5309ca6d7
