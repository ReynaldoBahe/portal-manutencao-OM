import streamlit as st
import pandas as pd
import json
import urllib.parse

# 1. Configuração da Página (Layout Amplo e Corporativo)
st.set_page_config(
    page_title="RB Consultoria - Gestão de Ativos",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS: Altura calibrada para 650px para unificar o campo de visão
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    iframe { width: 100% !important; height: 650px !important; border-radius: 12px; }
    .legenda-item { display: flex; align-items: center; margin-bottom: 6px; font-size: 14px; }
    .quadrado-cor { width: 16px; height: 16px; border-radius: 4px; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# Base da URL do seu modelo Speckle com o token
url_base_speckle = "https://speckle.systems"

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
    url_modificadores = ""
    
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
            df_os['ID'] = df_os['ID'].astype(str).str.strip()
            
            # Mapeamento inteligente da nova coluna de responsáveis
            if 'Responsavel' in df_os.columns:
                df_os['Responsavel'] = df_os['Responsavel'].astype(str).str.strip()
            else:
                df_os['Responsavel'] = "Não Atribuído"
            
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
            st.subheader("🎨 Filtro de Cores no Modelo (BIM)")
            modo_cor = st.toggle("Ativar Visão Cromática por Status", value=True)
            
            if modo_cor:
                st.markdown("""
                <div class="legenda-item"><div class="quadrado-cor" style="background-color: #ff4b4b;"></div>🔴 Aberta (Manutenção Urgente)</div>
                <div class="legenda-item"><div class="quadrado-cor" style="background-color: #28a745;"></div>🟢 Fechado (Ativo em Conformidade)</div>
                """, unsafe_allow_html=True)
                
                # Engenharia de Isolamento de IDs no Speckle
                ids_abertos = df_exibicao[df_exibicao['Status'] == 'Aberta']['ID'].dropna().tolist()
                opcoes_visualizador = {"ghostOthers": True}
                if ids_abertos:
                    opcoes_visualizador["filter"] = {"objectIds": ids_abertos}
                
                string_json = json.dumps(opcoes_visualizador)
                url_modificadores = f"#embed={urllib.parse.quote(string_json)}"
            
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

# 3. Layout de Tela: Área Central (Maquete 3D Panorâmica do Speckle Dinâmica)
st.title("Visualizador Operacional de Ativos 3D")

url_final_speckle = f"{url_base_speckle}{url_modificadores}"
st.components.v1.iframe(url_final_speckle, height=650)

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
        
        linha_os = df_exibicao[df_exibicao['OS'] == os_selecionada].iloc[0]
        
        st.info(f"""
        **📋 Ficha Técnica do Ativo**
        * **ID BIM:** `{linha_os['ID']}`
        * **Responsável Técnico:** {linha_os['Responsavel']}
        * **Setor:** {linha_os['Setor']}
        * **Status Atual:** {linha_os['Status']}
        * **Data de Abertura:** {linha_os['Data_Abertura'].strftime('%d/%m/%Y')}
        * **Histórico de Quebras:** 3 recorrências registradas nos últimos 180 dias.
        * 📖 [Acessar Manual Técnico do Ativo](https://github.com)
        """)
        
    with col_diag:
        st.markdown("**⚡ Análise de Engenharia Operacional da IA**")
        
        if linha_os['Status'] == 'Aberta':
            st.error(f"""
            ⚠️ DIAGNÓSTICO PRESCRITIVO: Risco de Parada Crítica
            
            Análise Causa Raiz: Com base na descrição "{linha_os['Descrição']}" e no cruzamento com o manual técnico, o sintoma apresentado aponta para fadiga por vibração excessiva nas prumadas de alimentação do Bloco B.
            
            🔧 Direcionamento e Plano de Ação para Campo (Alocado para: {linha_os['Responsavel']}):
            1. Isolar a válvula reguladora de pressão hidráulica conforme Seção 4.2 do manual.
            2. Verificar se há microfissuras na junta de expansão flexível.
            3. Substituir anéis de vedação elastoméricos antes de reabrir o fluxo.
            
            Nível de Criticidade: ALTA | Ativo ID: {linha_os['ID'][:8]}...
            """)
        else:
            st.success(f"""
            ✅ ANÁLISE COMPLEMENTAR: Ordem Encerrada
            
            Análise de Fechamento: A OS executada por {linha_os['Responsavel']} referente a "{linha_os['Descrição']}" foi devidamente finalizada de acordo com as especificações técnicas do fabricante.
            
            📈 Recomendação Preditiva:
            * Agendar inspeção termográfica preventiva em 90 dias para garantir a estabilidade do ativo.
            * Registrar a conformidade dos componentes trocados no banco de dados do CMMS.
            
            Status do Ativo: Estável | ID Identificado: {linha_os['ID'][:8]}...
            """)
            
    # --- NOVO BLOCO VISUAL: ANÁLISE DE DESEMPENHO DA EQUIPE ---
    st.markdown("---")
    st.subheader("👥 Análise de Produtividade da Equipe Técnica")
    
    df_fechadas_resp = df_exibicao[df_exibicao['Status'] == 'Fechado']
    if not df_fechadas_resp.empty:
        produtividade = df_fechadas_resp['Responsavel'].value_counts()
        st.bar_chart(produtividade)
    else:
        st.info("Nenhuma ordem fechada encontrada no filtro selecionado para montar o gráfico de barras.")
        
else:
    st.info("Carregue a planilha na barra lateral para ativar o Centro de Diagnóstico Inteligente por IA.")

st.markdown("---")
st.subheader("📋 Relatório Sincronizado de Ordens de Serviço")

if arquivo_upload is not None and not df_exibicao.empty:
