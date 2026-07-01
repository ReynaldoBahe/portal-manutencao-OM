import streamlit as st

# 1. Configuração da página (O modo Wide permite a expansão das páginas internas)
st.set_page_config(page_title="RB Consultoria", page_icon="🏢", layout="wide")

# 2. Inicializa as variáveis de controle de login globais
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "cliente_ativo" not in st.session_state:
    st.session_state.cliente_ativo = ""

# 3. Definição das Páginas do Sistema utilizando st.Page
pagina_login = st.Page("app.py", title="Acesso ao Sistema", icon="🔒", default=True)
pagina_home = st.Page("pages/01_Home.py", title="Home", icon="🏠")
pagina_engenharia = st.Page("pages/01_Modulos_de_Engenharia.py", title="Módulos de Engenharia", icon="⚙️")
pagina_manutencao = st.Page("pages/02_Gestao_da_Manutencao.py", title="Gestão da Manutenção", icon="🛠️")
pagina_indicadores = st.Page("pages/03_Indicadores_de_Tempo.py", title="Indicadores de Tempo", icon="📊")
pagina_telemetria = st.Page("pages/04_Telemetria_em_Tempo_Real.py", title="Telemetria em Tempo Real", icon="⚡")

# Gerenciador de Navegação Dinâmica (Esconde o menu lateral antes do login)
if st.session_state.logged_in:
    paginas_disponiveis = [pagina_home, pagina_engenharia, pagina_manutencao, pagina_indicadores, pagina_telemetria]
else:
    paginas_disponiveis = [pagina_login]

pg = st.navigation(paginas_disponiveis)

# =========================================================================
# LÓGICA DE RENDERIZAÇÃO DAS TELAS
# =========================================================================
if not st.session_state.logged_in:
    
    # 🔐 CSS ISOLADO COMPORTAMENTAL: Só funciona enquanto o formulário de login existir na tela
    st.markdown("""
        <style>
        /* Aplica o fundo escuro azulado premium apenas se a página contiver o formulário de login */
        .stApp:has(div[data-testid="stForm"]) {
            background-color: #111827 !important;
            background-image: radial-gradient(at 0% 0%, hsla(217,100%,16%,1) 0, transparent 50%), 
                              radial-gradient(at 50% 0%, hsla(220,95%,10%,1) 0, transparent 50%) !important;
        }
        
        /* Centraliza e restringe a largura máxima da tela a 620px apenas na tela de login */
        .stApp:has(div[data-testid="stForm"]) .block-container {
            max-width: 620px !important;
            padding-top: 5rem !important;
            margin: 0 auto !important;
        }
        
        /* Transforma a caixa padrão em um Card Blanco Flutuante com Sombra Real */
        div[data-testid="stForm"] {
            background-color: #ffffff !important;
            padding: 35px 30px !important;
            border-radius: 16px !important;
            border: 1px solid #e5e7eb !important;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Estilização das fontes e rótulos dos campos */
        label { color: #374151 !important; font-weight: 600 !important; font-size: 14px !important; }
        
        /* Inputs arredondados, limpos e com texto escuro visível */
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 1px solid #d1d5db !important;
            padding: 12px !important;
            background-color: #f9fafb !important;
            color: #111827 !important;
        }
        
        /* Botão de Login Azul Safira customizado com gradiente corporativo */
        div.stFormSubmitButton > button {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 12px 0px !important;
            font-size: 16px !important;
            margin-top: 10px !important;
            box-shadow: 0 4px 10px rgba(30, 58, 138, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Formulário de Credenciais Premium
    with st.form("menu_login_premium"):
        
        # Logotipo em código HTML puro (Imune a erros de CORS ou quedas de links de imagem)
        st.markdown("""
            <div style='text-align: center; margin-bottom: 25px;'>
                <div style='display: inline-block; background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); padding: 10px 20px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(30, 58, 138, 0.2);'>
                    <span style='color: #ffffff; font-size: 28px; font-weight: 900; letter-spacing: 2px;'>RB</span>
                    <span style='color: #93c5fd; font-size: 28px; font-weight: 300; letter-spacing: 2px;'>CONSULTORIA</span>
                </div>
                <p style='color: #4b5563; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 5px; margin-bottom: 0px;'>Gestão Estratégica de Ativos</p>
                <div style='height: 1px; background: linear-gradient(to right, transparent, #e5e7eb, transparent); margin-top: 15px;'></div>
            </div>
        """, unsafe_allow_html=True)
        
        # Inputs de dados estruturados
        usuario = st.text_input("👤 Usuário Corporativo", placeholder="Ex: admin")
        senha = st.text_input("🔑 Senha de Acesso", type="password", placeholder="Digite sua senha")
        lembrar = st.checkbox("Manter conectado neste dispositivo")
        
        botao_entrar = st.form_submit_button("Entrar no Sistema", use_container_width=True)
        
    if botao_entrar:
        usuarios_validos = {
            "admin": "admin",
            "fiat": "fiat123",
            "ambev": "ambev123"
        }
        
        if usuario in usuarios_validos and senha == usuarios_validos[usuario]:
            st.session_state.logged_in = True
            st.session_state.cliente_ativo = usuario.upper()
            st.rerun()
        else:
            st.error("❌ Credenciais inválidas. Tente novamente.")

else:
    # 🔓 ÁREA INTERNA TOTALMENTE CONFIGURADA: Executa sem nenhuma interferência de estilo
    pg.run()
    
    # Adiciona botão de Logout limpo e original na barra lateral pós-login
    with st.sidebar:
        st.markdown("---")
        if st.button("Sair da Conta", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
