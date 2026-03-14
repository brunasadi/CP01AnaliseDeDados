import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# CONFIGURAÇÃO GERAL DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Painel Executivo e Dicionário",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# FUNÇÃO PARA CARREGAR DADOS
# ==========================================
@st.cache_data
def load_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df

# ==========================================
# BARRA LATERAL (MENU E UPLOAD)
# ==========================================
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Selecione a Página:", ["📊 Visão Executiva", "📖 Dicionário de Variáveis"])

st.sidebar.markdown("---")
st.sidebar.header("Carregar Base de Dados")
uploaded_file = st.sidebar.file_uploader("Envie o ficheiro df_diarios", type=['csv', 'xlsx'])

# ==========================================
# PÁGINA 1: VISÃO EXECUTIVA (DASHBOARD)
# ==========================================
if pagina == "📊 Visão Executiva":
    st.title("📊 Visão Executiva: Produtividade da Mão de Obra")

    if uploaded_file is not None:
        df_raw = load_data(uploaded_file)

        # Filtros e Tratamentos Iniciais
        df = df_raw[df_raw['tipo_insumo'] == 'MAO DE OBRA'].copy()

        if 'ip_d' in df.columns:
            df['ip_d'] = pd.to_numeric(df['ip_d'], errors='coerce')
            df = df.dropna(subset=['ip_d'])

        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
            df['data_curta'] = df['data'].dt.date

        # Filtros Interativos na Sidebar
        st.sidebar.subheader("Filtros de Análise")
        obras = df['nome_obra'].dropna().unique().tolist() if 'nome_obra' in df.columns else []
        obra_selecionada = st.sidebar.multiselect("Filtrar por Obra:", options=obras, default=obras)

        grupos = df['grupo'].dropna().unique().tolist() if 'grupo' in df.columns else []
        grupo_selecionado = st.sidebar.multiselect("Filtrar por Serviço:", options=grupos, default=grupos)

        # Aplicando filtros
        df_filtered = df[df['nome_obra'].isin(obra_selecionada)]
        if grupo_selecionado:
            df_filtered = df_filtered[df_filtered['grupo'].isin(grupo_selecionado)]

        if not df_filtered.empty:
            # ==========================================
            # CÁLCULOS ESTATÍSTICOS (ip_d)
            # ==========================================
            # 1. Medidas de Tendência Central
            media = df_filtered['ip_d'].mean()
            mediana = df_filtered['ip_d'].median()
            moda = df_filtered['ip_d'].mode()[0] if not df_filtered['ip_d'].mode().empty else np.nan

            # 2. Medidas de Dispersão
            amplitude = df_filtered['ip_d'].max() - df_filtered['ip_d'].min()
            variancia = df_filtered['ip_d'].var()
            desvio_padrao = df_filtered['ip_d'].std()
            cv = (desvio_padrao / media) * 100 if media != 0 else 0

            total_registos = len(df_filtered)

            # ==========================================
            # BLOCO VISUAL 1: TENDÊNCIA CENTRAL (O "Normal")
            # ==========================================
            st.markdown("### 🎯 Medidas de Tendência Central")
            st.caption("Indicam para onde a produtividade da equipe tende a convergir no dia a dia.")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                with st.container(border=True):
                    st.metric("Média (ip_d)", f"{media:.4f}",
                              help="Soma de todos os índices dividida pelos dias trabalhados.")
            with col2:
                with st.container(border=True):
                    st.metric("Mediana", f"{mediana:.4f}",
                              help="Valor do meio. Metade dos dias foi melhor que isso, metade foi pior.")
            with col3:
                with st.container(border=True):
                    st.metric("Moda", f"{moda:.4f}", help="O índice de produtividade que mais se repetiu no canteiro.")
            with col4:
                with st.container(border=True):
                    st.metric("Registos Analisados", f"{total_registos}",
                              help="Quantidade de apontamentos de Mão de Obra considerados.")

            st.write("")  # Espaçamento

            # ==========================================
            # BLOCO VISUAL 2: DISPERSÃO (O "Risco")
            # ==========================================
            st.markdown("### ⚖️ Medidas de Dispersão e Variabilidade")
            st.caption("Indicam o nível de instabilidade, risco e variação do processo produtivo.")

            col5, col6, col7, col8 = st.columns(4)
            with col5:
                with st.container(border=True):
                    st.metric("Amplitude", f"{amplitude:.4f}",
                              help="A distância entre o dia mais produtivo e o menos produtivo (Máx - Mín).")
            with col6:
                with st.container(border=True):
                    st.metric("Variância", f"{variancia:.5f}",
                              help="Grau de afastamento dos dados em relação à média (ao quadrado).")
            with col7:
                with st.container(border=True):
                    st.metric("Desvio-Padrão", f"{desvio_padrao:.4f}",
                              help="Quantos pontos a produtividade costuma errar (para mais ou menos) em relação à média.")
            with col8:
                alerta = " ⚠️ Alerta" if cv > 30 else " ✅ Estável"
                with st.container(border=True):
                    st.metric(f"Coef. Variação (CV){alerta}", f"{cv:.1f}%",
                              help="Mede o risco. CV acima de 30% indica alta instabilidade na obra.")

            st.markdown("---")

            # ==========================================
            # BLOCO VISUAL 3: GRÁFICOS (Storytelling)
            # ==========================================
            col_graf1, col_graf2 = st.columns([6, 4])

            with col_graf1:
                st.subheader("📈 Evolução da Produtividade no Tempo")
                if 'data_curta' in df_filtered.columns and not df_filtered['data_curta'].isnull().all():
                    df_tempo = df_filtered.groupby('data_curta')['ip_d'].mean().reset_index()
                    fig_linha = px.line(df_tempo, x='data_curta', y='ip_d', markers=True)
                    st.plotly_chart(fig_linha, use_container_width=True, theme="streamlit")
                else:
                    st.info("A coluna de datas não está disponível nesta base.")

            with col_graf2:
                st.subheader("📦 Dispersão entre Obras (Boxplot)")
                fig_box = px.box(df_filtered, x='nome_obra', y='ip_d')
                st.plotly_chart(fig_box, use_container_width=True, theme="streamlit")

            st.markdown("---")
            st.subheader("👷 Alocação de Profissionais (Top 10)")
            top_insumos = df_filtered['insumo'].value_counts().reset_index().head(10)
            top_insumos.columns = ['Profissional', 'Registos']
            fig_bar = px.bar(top_insumos, x='Registos', y='Profissional', orientation='h', text='Registos')
            fig_bar.update_traces(textposition='outside')
            fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title="Quantidade de Apontamentos",
                                  yaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True, theme="streamlit")

        else:
            st.warning("Sem dados para os filtros selecionados.")
    else:
        st.info("Carregue o arquivo Excel ou CSV na barra lateral para visualizar o Dashboard.")

# ==========================================
# PÁGINA 2: DICIONÁRIO DE VARIÁVEIS
# ==========================================
elif pagina == "📖 Dicionário de Variáveis":
    st.title("📖 Dicionário e Tipos de Variáveis")
    st.markdown("Classificação estatística de cada coluna presente na base de dados `df_diarios`.")

    dados_variaveis = {
        "Variável na Base": [
            "classe", "caderno", "grupo", "código cc", "descrição",
            "unid", "nova", "codins", "insumo", "unidins",
            "tipo insumo", "Nome_obra", "id_ccoi_elemento",
            "id_appropriation_composition", "app_inicio",
            "app_fim", "qnts", "qs", "data", "qntd_ac",
            "qs_acum", "ip_d", "ip_acum", "elementos"
        ],
        "Classificação Estatística": [
            "Qualitativa Nominal", "Qualitativa Nominal", "Qualitativa Nominal", "Qualitativa Nominal",
            "Qualitativa Nominal",
            "Qualitativa Nominal", "Qualitativa Nominal", "Qualitativa Nominal", "Qualitativa Nominal",
            "Qualitativa Nominal",
            "Qualitativa Nominal", "Qualitativa Nominal", "Qualitativa Nominal",
            "Qualitativa Nominal", "Quantitativa Contínua",
            "Quantitativa Contínua", "Quantitativa Contínua", "Quantitativa Contínua", "Quantitativa Contínua",
            "Quantitativa Contínua",
            "Quantitativa Contínua", "Quantitativa Contínua", "Quantitativa Contínua", "Qualitativa Nominal"
        ]
    }

    df_dicionario = pd.DataFrame(dados_variaveis)
    st.dataframe(df_dicionario, use_container_width=True, hide_index=True)

    st.info("""
    **Notas de Interpretação Estatística:**
    * **Qualitativa Nominal:** Categorias, nomes ou rótulos sem uma ordem matemática natural (ex: nome da obra, insumo).
    * **Quantitativa Contínua:** Variáveis numéricas que podem assumir valores fracionados, geralmente provenientes de medições (ex: horas, índices de produtividade).
    """)