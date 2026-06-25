# 🏢 Portal de Operação & Manutenção - RB Consultoria

Painel analítico para gestão de ativos tridimensionais integrado com monitoramento de SLA de ordens de serviço.

## 📋 Instruções de Operação do Sistema
1. Exporte a planilha de Ordens de Serviço do sistema CMMS no formato `.csv`.
2. Certifique-se de que as colunas `Data_Abertura` e `Status` estão preenchidas corretamente.
3. Faça o upload do arquivo na barra lateral do painel para recalcular o SLA em tempo real.

## 📖 Manuais Técnicos de Ativos (Links Compartilhados)
*   **Sistema de Climatização (Chillers/Ar-Condicionado Central)**: [Clique aqui para acessar o manual](INSIRA_O_LINK_DO_SEU_GOOGLE_DRIVE_OU_SHAREPOINT_AQUI)
*   **Geradores de Energia Elétrica**: [Clique aqui para acessar o manual](INSIRA_O_LINK_DO_SEU_GOOGLE_DRIVE_OU_SHAREPOINT_AQUI)
*   **Quadro Elétrico e Bombas Hidráulicas**: [Clique aqui para acessar o manual](INSIRA_O_LINK_DO_SEU_GOOGLE_DRIVE_OU_SHAREPOINT_AQUI)

## 📊 Dicionário de Dados da Planilha
*   `Data_Abertura`: Data e hora em que a manutenção foi solicitada.
*   `Status`: Estado atual da OS. O sistema contabiliza o SLA buscando o termo **"Fechado"**.
# portal-manutencao-OM


---

## 🧠 Memorial Descritivo de Arquitetura Técnica

O sistema foi concebido sob uma arquitetura leve, moderna e orientada a dados, focada no tripé: **Geometria Tridimensional (BIM)**, **Indicadores Operacionais de Desempenho (SLA/PCM)** e **Lógica Prescritiva (IA)**.

### 1. Pilares da Estrutura de Arquivos
*   **`app.py` (O Cérebro)**: Script mestre em Python utilizando o framework *Streamlit*. Gerencia o estado da aplicação, processa a matemática do SLA em milissegundos, renderiza o layout responsivo e realiza a injeção dinâmica de parâmetros.
*   **`requirements.txt` (A Infraestrutura)**: Arquivo de dependências lido automaticamente pelo servidor de nuvem para provisionar os pacotes essenciais (`streamlit` e `pandas`).
*   **`README.md` (A Base de Conhecimento)**: Este manual técnico, configurado para centralizar links compartilhados de manuais de ativos e a documentação técnica da operação.

### 2. Engenharia de Dados & Fluxo de Informações (Backend)
O aplicativo opera sob um modelo de **memória volátil e segura**, ideal para auditoria local sem exposição de banco de dados fixo:
1.  **Ingestão de Dados**: Arquivo `.csv` exportado do CMMS é carregado via interface gráfica por upload local.
2.  **Saneamento de Strings**: O pacote *Pandas* realiza o *strip* automático de colunas, convertendo campos de data (`Data_Abertura`) para objetos nativos e limpando espaços invisíveis.
3.  **Lógica Estrita do SLA**: O sistema isola o mês corrente de análise (Junho/2026) e processa dinamicamente a equação corporativa:
    $$\text{SLA Real} = \left( \frac{\text{OS Fechadas}}{\text{Total de OS Abertas no Mês}} \right) \times 100$$

### 3. Integrações de Interface & Recursos Visuais (Frontend)
*   **Visualizador BIM (Speckle API)**: Modelo 3D autêntico do resort renderizado nativamente por meio de contêineres `iframe` em HTML5, otimizado com *embed tokens* privados. 
*   **Controle Cromático & Isolação Preditiva**: O código converte a coluna de identificadores únicos de 32 caracteres (`ID`) da planilha e injeta parâmetros de filtro criptografados diretamente na URL (`#embed=...`). Isso ativa o *Modo Fantasma (Ghosting)* no Speckle, isolando instantaneamente na maquete apenas os elementos com manutenção pendente.
*   **Matriz de Volumetria (KPIs)**: Disposição em 4 colunas responsivas mapeando o estado tático das equipes em tempo real (*Aberta, Em Atendimento, Pausada, Fechado*).
*   **Centro de Diagnóstico Inteligente**: Arquitetura lógica utilizando os componentes de notificação nativos e seguros do Streamlit, cruzando o `Status` e a `Descrição` da falha para fornecer à equipe de campo um diagnóstico de causa raiz e plano de ação integrado ao responsável técnico alocado.
*   **Gráfico de Produtividade**: Componente de visualização nativo que contabiliza e plota em barras horizontais o volume acumulado de entregas com sucesso por colaborador.
