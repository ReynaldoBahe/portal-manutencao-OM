import streamlit as st
import pandas as pd

# 1. Configuração da Página (Layout Amplo e Corporativo)
st.set_page_config(
    page_title="RB Consultoria - Gestão de Ativos",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para garantir a harmonia visual e o tamanho do visualizador
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    iframe { width: 100% !important; height: 1000px !important; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# 2. Layout de Tela: Barra Lateral (Métricas Operacionais)
with st.sidebar:
    st.title("Painel de Controle")
    st.markdown("---")
    
    # Componente de Upload do arquivo CSV gerado pelo CMMS
    arquivo_upload = st.file_uploader("Carregar Planilha CMMS (.csv)", type=["csv"])
    
    st.markdown("---")
    
    # Criamos os placeholders das variáveis para evitar erros de inicialização
    df_exibicao = pd.DataFrame()
    
    if arquivo_upload is not None:
        try:
            # Lendo a planilha carregada pelo usuário
            df_os = pd.read_csv(arquivo_upload)
            
            # Forçar os nomes das colunas para remover espaços invisíveis
            df_os.columns = df_os.columns.str.strip()
            
            # Padronização e limpeza dos dados baseados na planilha real
            df_os['Data_Abertura'] = pd.to_datetime(df_os['Data_Abertura'], errors='coerce')
            df_os['Status'] = df_os['Status'].astype(str).str.strip()
            df_os['Setor'] = df_os['Setor'].astype(str).str.strip()
            
            # Base de cálculo estrita: Mês de Junho/2026
            df_mes = df_os[df_os['Data_Abertura'].dt.strftime('%Y-%m') == '2026-06']
            
            st.subheader("Filtros de Visão")
            
            # Filtro por Setor dinâmico
            lista_setores = ["Todos"] + sorted(list(df_mes['Setor'].unique()))
            setor_selecionado = st.selectbox("Filtrar por Setor:", lista_setores)
            
            # Filtro por Status dinâmico
            lista_status = ["Todos"] + sorted(list(df_mes['Status'].unique()))
            status_selecionado = st.selectbox("Filtrar por Status:", lista_status)
            
            # Aplicando os filtros na tabela de exibição
            df_exibicao = df_mes.copy()
            if setor_selecionado != "Todos":
                df_exibicao = df_exibicao[df_exibicao['Setor'] == setor_selecionado]
            if status_selecionado != "Todos":
                df_exibicao = df_exibicao[df_exibicao['Status'] == status_selecionado]
            
            st.markdown("---")
            st.subheader("Métricas de Manutenção")
            
            # Cálculo do SLA focado no mês
            total_abertas_mes = len(df_mes)
            if total_abertas_mes > 0:
                total_fechadas_filtradas = len(df_exibicao[df_exibicao['Status'] == 'Fechado'])
                sla_calculado = round((total_fechadas_filtradas / total_abertas_mes) * 100, 1)
                total_exibidas = len(df_exibicao)
                
                st.metric(
                    label="SLA de Atendimento (Meta: 95%)",
                    value=f"{sla_calculado}%",
                    delta=f"{round(sla_calculado - 95.0, 1)}% em relação à meta",
                    delta_color="normal" if sla_calculado >= 95 else "inverse"
                )
                st.info(f"📊 {total_fechadas_filtradas} OS fechadas no filtro atual de {total_exibidas} visíveis.")
            else:
                st.warning("Nenhuma OS encontrada para Junho/2026.")
                
        except Exception as e:
            st.error(f"Erro ao processar as colunas: {e}")
    else:
        st.warning("Aguardando upload da planilha...")
        st.metric(label="SLA de Atendimento (Meta: 95%)", value="-- %", delta="Sem dados")

# 4. Layout de Tela: Área Central (Maquete 3D Panorâmica e Tabela)
st.title("Visualizador Operacional de Ativos 3D")

# Link atualizado e funcional da maquete 3D para evitar a tela cinza de erro
url_maquete_3d = "https://spline.design"
st.components.v1.iframe(url_maquete_3d, height=1000)

st.markdown("---")
st.subheader("📋 Relatório Sincronizado de Ordens de Serviço")

# Exibição da tabela filtrada dinamicamente logo abaixo da maquete
if arquivo_upload is not None and not df_exibicao.empty:
    st.dataframe(df_exibicao, use_container_width=True, height=300)
else:
    st.info("Faça o upload do arquivo CSV na barra lateral para listar as Ordens de Serviço filtradas.")
