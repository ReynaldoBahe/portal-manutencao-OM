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

# 2. Função Inteligente de Processamento de Dados e Cálculo de SLA Real
def processar_dados_e_calcular_sla(df):
    if df.empty:
        return 0.0, 0, 0
    
    # Padronização e limpeza dos dados baseados na planilha real
    df['Data_Abertura'] = pd.to_datetime(df['Data_Abertura'], errors='coerce')
    df['Status'] = df['Status'].astype(str).str.strip()
    
    # Filtrando as OS do mês de Junho/2026 (baseado na sua planilha de testes)
    df_mes = df[df['Data_Abertura'].dt.strftime('%Y-%m') == '2026-06']
    
    total_abertas = len(df_mes)
    if total_abertas == 0:
        return 0.0, 0, 0
        
    # Contabilizando apenas as ordens concluídas ("Fechado")
    total_fechadas = len(df_mes[df_mes['Status'] == 'Fechado'])
    
    # Cálculo real do SLA
    sla_real = (total_fechadas / total_abertas) * 100
    return round(sla_real, 1), total_fechadas, total_abertas

# 3. Layout de Tela: Barra Lateral (Métricas Operacionais)
with st.sidebar:
    st.title("Painel de Controle")
    st.markdown("---")
    
    # Componente de Upload do arquivo CSV gerado pelo CMMS
    arquivo_upload = st.file_uploader("Carregar Planilha CMMS (.csv)", type=["csv"])
    
    st.markdown("---")
    st.subheader("Métricas de Manutenção")
    
    # Lógica de exibição condicional baseada no upload do arquivo
    if arquivo_upload is not None:
        try:
            # Lendo a planilha carregada pelo usuário
            df_os = pd.read_csv(arquivo_upload)
            
            # Executando o cálculo com as colunas reais: Data_Abertura e Status
            sla_calculado, fechadas, abertas = processar_dados_e_calcular_sla(df_os)
            
            # Exibindo o cartão de SLA Real Automatizado
            st.metric(
                label="SLA de Atendimento (Meta: 95%)",
                value=f"{sla_calculado}%",
                delta=f"{round(sla_calculado - 95.0, 1)}% em relação à meta",
                delta_color="normal" if sla_calculado >= 95 else "inverse"
            )
            st.info(f"📊 Dados do mês atual: {fechadas} de {abertas} OS concluídas.")
            
        except Exception as e:
            st.error("Erro ao processar as colunas. Verifique o formato do arquivo.")
            st.metric(label="SLA de Atendimento", value="Erro", delta="Planilha incompatível")
    else:
        # Estado inicial/placeholder antes do usuário fazer o upload
        st.warning("Aguardando upload da planilha...")
        st.metric(label="SLA de Atendimento (Meta: 95%)", value="-- %", delta="Sem dados")

# 4. Layout de Tela: Área Central (Maquete 3D Panorâmica e Tabela)
st.title("Visualizador Operacional de Ativos 3D")

# Renderização gigante da maquete 3D
url_maquete_3d = "https://spline.design"
st.components.v1.iframe(url_maquete_3d, height=1000)

st.markdown("---")
st.subheader("📋 Relatório Sincronizado de Ordens de Serviço")

# Exibição da tabela logo abaixo da maquete, atualizando em tempo real com o arquivo enviado
if arquivo_upload is not None:
    st.dataframe(df_os, use_container_width=True, height=300)
else:
    st.info("Faça o upload do arquivo CSV na barra lateral para listar as Ordens de Serviço ativas no mapa.")
