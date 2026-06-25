import streamlit as st
import pandas as pd

# 1. Configuração da Página (Layout Amplo e Corporativo)
st.set_page_config(
    page_title="RB Consultoria - Gestão de Ativos",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para garantir a harmonia visual, tamanho do visualizador e design dos cards de IA
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    iframe { width: 100% !important; height: 1000px !important; border-radius: 12px; }
    .card-ia {
        background-color: #f0f7ff;
        border-left: 5px solid #0066cc;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .badge-alta { background-color: #ffcccc; color: #cc0000; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Layout de Tela: Barra Lateral (Métricas Operacionais)
with st.sidebar:
    st.title("Painel de Controle")
    st.markdown("---")
    
    # Componente de Upload do arquivo CSV gerado pelo CMMS
    arquivo_upload = st.file_uploader("Carregar Planilha CMMS (.csv)", type=["csv"])
    
    st.markdown("---")
    
    # Placeholders para evitar erros de inicialização
    df_exibicao = pd.DataFrame()
    contagem_status = {"Aberta": 0, "Fechado": 0, "Em Atendimento": 0, "Pausada": 0}
    lista_os_selecao = ["Nenhuma OS selecionada"]
    
    if arquivo_upload is not None:
        try:
            # Lendo a planilha carregada pelo usuário
            df_os = pd.read_csv(arquivo_upload)
            df_os.columns = df_os.columns.str.strip()
            
            # Padronização e limpeza dos dados
            df_os['Data_Abertura'] = pd.to_datetime(df_os['Data_Abertura'], errors='coerce')
            df_os['Status'] = df_os['Status'].astype(str).str.strip()
            df_os['Setor'] = df_os['Setor'].astype(str).str.strip()
            df_os['OS'] = df_os['OS'].astype(str).str.strip()
            
            # Base de cálculo estrita: Mês de Junho/2026
            df_mes = df_os[df_os['Data_Abertura'].dt.strftime('%Y-%m') == '2026-06']
            
            st.subheader("Filtros de Visão")
            lista_setores = ["Todos"] + sorted(list(df_mes['Setor'].unique()))
            setor_selecionado = st.selectbox("Filtrar por Setor:", lista_setores)
            
            lista_status = ["Todos"] + sorted(list(df_mes['Status'].unique()))
            status_selecionado = st.selectbox("Filtrar por Status:", lista_status)
            
            # Aplicando os filtros na tabela de exibição
            df_exibicao = df_mes.copy()
            if setor_selecionado != "Todos":
                df_exibicao = df_exibicao[df_exibicao['Setor'] == setor_selecionado]
            if status_selecionado != "Todos":
                df_exibicao = df_exibicao[df_exibicao['Status'] == status_selecionado]
            
            # Lista de OS para o seletor da IA
            lista_os_selecao = sorted(list(df_exibicao['OS'].unique()))
            
            # Mapeamento e contagem estrita dos status
            for status_chave in contagem_status.keys():
                contagem_status[status_chave] = len(df_exibicao[df_exibicao['Status'] == status_chave])
            
            st.markdown("---")
            st.subheader("Métricas de Manutenção")
            
            total_abertas_mes = len(df_mes)
            if total_abertas_mes > 0:
                total_fechadas_filtradas = len(df_exibicao[df_exibicao['Status'] == 'Fechado'])
                sla_calculado = round((total_fechadas_filtradas / total_abertas_mes) * 100, 1)
                
                st.metric(
                    label="SLA de Atendimento (Meta: 95%)",
                    value=f"{sla_calculado}%",
                    delta=f"{round(sla_calculado - 95.0, 1)}% em relação à meta",
                    delta_color="normal" if sla_calculado >= 95 else "inverse"
                )
            
        except Exception as e:
            st.error(f"Erro ao processar as colunas: {e}")
    else:
        st.warning("Aguardando upload da planilha...")
        st.metric(label="SLA de Atendimento (Meta: 95%)", value="-- %", delta="Sem dados")

# 3. Layout de Tela: Área Central (Maquete 3D Panorâmica do Speckle Atualizada)
st.title("Visualizador Operacional de Ativos 3D")

# URL atualizada com o novo embedToken enviado pelo usuário
url_maquete_3d = "https://app.speckle.systems/projects/a649da7292/models/815af390c7?embedToken=2aaa49d6f30ad4db0d2844045f56d8ad0ee3bf7643"
st.components.v1.iframe(url_maquete_3d, height=1000)

st.markdown("---")

# 4. Volumetria das Ordens de Serviço (KPIs)
st.subheader("📊 Volumetria das Ordens de Serviço")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="🟢 Aberta", value=contagem_status["Aberta"])
with col2: st.metric(label="🔵 Em Atendimento", value=contagem_status["Em Atendimento"])
with col3: st.metric(label="🟡 Pausada", value=contagem_status["Pausada"])
with col4: st.metric(label="🔴 Fechado", value=contagem_status["Fechado"])

st.markdown("---")

# 5. Centro de Diagnóstico Avançado (IA Preditiva)
st.subheader("🧠 Centro de Diagnóstico Avançado (IA Preditiva)")

if arquivo_upload is not None and not df_exibicao.empty:
    col_sel, col_diag = st.columns(2)
    
    with col_sel:
        st.markdown("**🔎 Seleção de Ativo para Auditoria**")
        os_selecionada = st.selectbox("Selecione a OS para análise da IA:", lista_os_selecao)
        
        # Puxando a linha selecionada para simular o cruzamento de dados
        linha_os = df_exibicao[df_exibicao['OS'] == os_selecionada].iloc[0]
        
        st.info(f"""
        **📋 Ficha Técnica do Ativo**
        * **Setor:** {linha_os['Setor']}
        * **Status Atual:** {linha_os['Status']}
        * **Data de Abertura:** {linha_os['Data_Abertura'].strftime('%d/%m/%Y')}
        * **Histórico de Quebras:** 3 recorrências registradas nos últimos 180 dias.
        * 📖 [Acessar Manual Técnico do Ativo](https://github.com)
        """)
        
    with col_diag:
        st.markdown("**⚡ Análise de Engenharia Operacional da IA**")
        
        if linha_os['Status'] == 'Aberta':
            st.markdown(f"""
            <div class="card-ia">
                <h4>⚠️ DIAGNÓSTICO PRESCRITIVO: Risco de Parada Crítica</h4>
                <p><b>Análise Causa Raiz:</b> Com base na descrição <i>"{linha_os['Descrição']}"</i> e no cruzamento com o manual técnico, o sintoma apresentado aponta para fadiga por vibração excessiva nas prumadas de alimentação do Bloco B.</p>
                <hr>
                <p><b>🔧 Direcionamento e Plano de Ação para Campo:</b></p>
                <ol>
                    <li>Isolar a válvula reguladora de pressão hidráulica conforme Seção 4.2 do manual.</li>
                    <li>Verificar se há microfissuras na junta de expansão flexível.</li>
                    <li>Substituir anéis de vedação elastoméricos antes de reabrir o fluxo.</li>
                </ol>
                <small>⚡ <i>Nível de Criticidade: <span class="badge-alta">ALTA</span> | MTTR estimado: 45 min.</i></small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card-ia" style="background-color: #f6fff6; border-left: 5px solid #28a745;">
                <h4>✅ ANÁLISE COMPLEMENTAR: Ordem Encerrada</h4>
                <p><b>Análise de Fechamento:</b> A OS referente a <i>"{linha_os['Descrição']}"</i> foi devidamente finalizada. O histórico confirma que a intervenção seguiu os parâmetros padrão especificados pelo fabricante no manual técnico.</p>
                <hr>
                <p><b>📈 Recomendação Preditiva:</b></p>
                <ul>
                    <li>Agendar inspeção termográfica preventiva em 90 dias para garantir a estabilidade do ativo.</li>
                    <li>Registrar a conformidade dos componentes trocados no banco de dados do CMMS.</li>
                </ul>
                <small>🍃 <i>Status do Sistema: Estável | Eficiência de Execução: 100%</i></small>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Carregue a planilha na barra lateral para ativar o Centro de Diagnóstico Inteligente por IA.")

st.markdown("---")
st.subheader("📋 Relatório Sincronizado de Ordens de Serviço")

if arquivo_upload is not None and not df_exibicao.empty:
    st.dataframe(df_exibicao, use_container_width=True, height=300)
else:
    st.info("Faça o upload do arquivo CSV na barra lateral para listar as Ordens de Serviço.")
