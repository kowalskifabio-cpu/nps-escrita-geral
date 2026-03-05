import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. Configurações da Página
st.set_page_config(page_title="NPS Escrita Geral", page_icon="📊")

# --- BLOCO DE SEGURANÇA VISUAL (LIMPEZA DE INTERFACE) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Remove a barra de ferramentas (pixels e coroa) */
            [data-testid="stToolbar"] {display: none !important;}
            [data-testid="stStatusWidget"] {display: none !important;}
            .stAppDeployButton {display: none !important;}
            
            /* Remove o selo "Made with Streamlit" e o avatar no mobile */
            div[data-testid="stDecoration"] {display: none !important;}
            .viewerBadge_container__1QSob {display: none !important;}
            
            /* Esconde os botões específicos de gerenciamento para o cliente */
            button[title="View app status"], 
            button[title="Manage app"],
            div[class*="StatusWidget"] {
                display: none !important;
            }

            /* Ajuste para mobile: remove o cabeçalho fixo branco */
            .stApp > header {display: none !important;}
            [data-testid="stHeader"] {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# ------------------------------------------------------------

# 2. CSS Personalizado - BLINDAGEM TOTAL PARA IPHONE (CONTRA ESCRARECIMENTO)
st.markdown("""
<style>
    /* Força o navegador a entender que a página é Light Mode */
    :root { color-scheme: light !important; }

    /* Fundo geral da página */
    .stApp { background-color: #F4F6F8 !important; }
    
    /* Força cor azul escuro em todos os textos da página */
    label, p, span, .stMarkdown, .stTextInput label, .stSelectbox label, .stTextArea label, h1, h2, h3, .stHeader {
        color: #0E3A5D !important;
        -webkit-text-fill-color: #0E3A5D !important;
    }
    
    /* Inputs de texto e áreas de texto: Fundo branco e Letra Azul Escuro */
    input, textarea, [data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        color: #0E3A5D !important;
        -webkit-text-fill-color: #0E3A5D !important;
        opacity: 1 !important;
        border: 1px solid #0E3A5D !important;
    }

    /* Selectbox (Dropdown): Fundo branco e Letra Azul Escuro */
    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #0E3A5D !important;
        -webkit-text-fill-color: #0E3A5D !important;
    }

    /* Botões: Força Fundo Azul e Texto Branco (evita o botão preto no iPhone) */
    div.stButton > button {
        background-color: #0E3A5D !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 2px solid #B79A5B !important;
        font-weight: bold !important;
        width: 100%;
        opacity: 1 !important;
    }

    /* Cabeçalho */
    .header-container { background-color: #0E3A5D; padding: 1.5rem; border-radius: 10px; text-align: center; margin-bottom: 2rem; }
    .header-title { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; font-weight: bold; margin-top: 10px; }
    
    /* Seções e Legendas */
    .section-title { color: #0E3A5D !important; -webkit-text-fill-color: #0E3A5D !important; font-weight: bold; border-bottom: 2px solid #B79A5B; margin-bottom: 20px; padding-top: 10px; }
    .stCaption { color: #555555 !important; -webkit-text-fill-color: #555555 !important; }

    /* Slider: Força visibilidade das marcas */
    .stSlider label { color: #0E3A5D !important; }
</style>
""", unsafe_allow_html=True)

# 3. Conexão Google com Limpeza de Chave
def get_gsheet_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"].to_dict()
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(credentials)

# 4. Cabeçalho
with st.container():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    try:
        st.image("Logo Escrita.png", width=200)
    except:
        st.write("---")
    st.markdown('<h1 class="header-title">Pesquisa de Satisfação</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. Navegação
if 'passo' not in st.session_state:
    st.session_state.passo = 1
    st.session_state.respostas = {}

# PASSO 1: IDENTIFICAÇÃO
if st.session_state.passo == 1:
    with st.form("f1"):
        nome_contato = st.text_input("Seu nome:", placeholder="Ex: João Silva")
        nome_empresa = st.text_input("Nome da sua empresa:", placeholder="Ex: Empresa ABC")
        st.markdown("### De 0 a 10, o quanto você recomendaria a Escrita Contabilidade para um amigo?")
        n_geral = st.select_slider("Nota:", options=list(range(11)), value=10)
        
        motivo_nota = st.text_area("O que mais motivou a sua nota?", placeholder="Conte-nos brevemente o motivo da sua avaliação...")
        
        if st.form_submit_button("Próxima Etapa"):
            if not nome_contato or not nome_empresa: 
                st.error("Por favor, preencha seu nome e o nome da empresa.")
            elif n_geral < 7 and not motivo_nota.strip():
                st.error("Para notas abaixo de 7, por favor, descreva o que motivou sua avaliação para que possamos melhorar.")
            else:
                st.session_state.respostas.update({
                    'cliente': nome_contato, 
                    'empresa': nome_empresa, 
                    'nota_geral': n_geral,
                    'motivo_nota': motivo_nota
                })
                st.session_state.passo = 2
                st.rerun()

# PASSO 2: ATRIBUTOS ESTRATÉGICOS
elif st.session_state.passo == 2:
    st.markdown('<p class="section-title">Avaliação Geral de Serviços</p>', unsafe_allow_html=True)
    with st.form("f2"):
        c1, c2 = st.columns(2)
        with c1:
            clareza = st.select_slider("Clareza nas informações:", options=list(range(11)), value=10)
            comunicacao = st.select_slider("Qualidade da Comunicação:", options=list(range(11)), value=10)
            custo = st.select_slider("Custo-benefício:", options=list(range(11)), value=10)
        with c2:
            prazos = st.select_slider("Cumprimento de Prazos:", options=list(range(11)), value=10)
            atendimento = st.select_slider("Cordialidade no Atendimento:", options=list(range(11)), value=10)
            
        if st.form_submit_button("Avaliar Departamentos"):
            st.session_state.respostas.update({
                'clareza': clareza, 'prazos': prazos, 'comunicacao': comunicacao,
                'atendimento': atendimento, 'custo': custo
            })
            st.session_state.passo = 3
            st.rerun()

# PASSO 3: DEPARTAMENTOS E FINALIZAÇÃO
elif st.session_state.passo == 3:
    st.markdown('<p class="section-title">Avaliação por Setor</p>', unsafe_allow_html=True)
    with st.form("f3"):
        def campo_setor(label, descricao, key_n, key_t):
            st.write(f"**{label}**")
            st.caption(descricao)
            col_n, col_t = st.columns([1, 4])
            opcoes_nota = ["Não se aplica"] + list(range(11))
            n = col_n.selectbox("Nota", opcoes_nota, index=11, key=key_n) 
            t = col_t.text_input("O que podemos melhorar? (obrigatório para notas abaixo de 7)", key=key_t)
            st.divider()
            return n, t

        n_con, t_con = campo_setor("Setor Contábil", "Responsável por lançamentos, conciliações, balancetes e demonstrações contábeis.", "n_con", "t_con")
        n_fis, t_fis = campo_setor("Setor Fiscal", "Responsável pela apuração de impostos, escrituração fiscal e obrigações acessórias tributárias.", "n_fis", "t_fis")
        n_pes, t_pes = campo_setor("Pessoal (Folha)", "Responsável por folha de pagamento, encargos sociais e rotinas trabalhistas.", "n_pes", "t_pes")
        n_leg, t_leg = campo_setor("Setor Legal / Societário", "Responsável por aberturas, alterações contratuais, certidões e regularizações de empresas.", "n_leg", "t_leg")
        n_fin, t_fin = campo_setor("Setor Financeiro", "Responsável pela gestão interna e faturamento da Escrita Contabilidade.", "n_fin", "t_fin")
        n_bpo, t_bpo = campo_setor("Setor BPO Financeiro", "Responsável pela gestão terceirizada das contas a pagar/receber e fluxo de caixa de nossos clientes.", "n_bpo", "t_bpo")
        n_recep, t_recep = campo_setor("Recepção", "Primeiro contato, atendimento telefônico e recebimento/entrega de documentos físicos.", "n_recep", "t_recep")
        n_est, t_est = campo_setor("Estrutura Física", "Avaliação de nossas instalações, conforto e ambiente para reuniões presenciais.", "n_est", "t_est")
        n_csc, t_csc = campo_setor("Sucesso do Cliente (CS)", "Responsável por garantir que suas necessidades sejam atendidas e sua experiência seja excelente.", "n_csc", "t_csc")

        st.write("**Podemos entrar em contato para falar sobre sua avaliação?**")
        contato_autorizado = st.radio("Selecione uma opção:", ["Sim", "Não"], index=0, horizontal=True)

        if st.form_submit_button("Finalizar e Enviar"):
            setores_erro = []
            lista_setores = [
                (n_con, t_con, "Contábil"), (n_fis, t_fis, "Fiscal"), (n_pes, t_pes, "Pessoal"),
                (n_leg, t_leg, "Legal"), (n_fin, t_fin, "Financeiro"), (n_bpo, t_bpo, "BPO"), 
                (n_recep, t_recep, "Recepção"), (n_est, t_est, "Estrutura"), (n_csc, t_csc, "CS")
            ]
            
            for nota, texto, nome in lista_setores:
                if isinstance(nota, int) and nota < 7 and not texto.strip():
                    setores_erro.append(nome)
            
            if setores_erro:
                st.error(f"Por favor, justifique as notas baixas nos setores: {', '.join(setores_erro)}")
            else:
                try:
                    client = get_gsheet_client()
                    sh = client.open_by_key(st.secrets["SHEET_ID"])
                    wks = sh.worksheet("respostas")
                    resp = st.session_state.respostas
                    linha = [
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        resp['cliente'], resp['empresa'], resp['nota_geral'], resp['motivo_nota'],
                        resp['clareza'], resp['prazos'], resp['comunicacao'], resp['atendimento'], resp['custo'],
                        n_con, t_con, n_fis, t_fis, n_pes, t_pes,
                        n_leg, t_leg, n_fin, t_fin, n_bpo, t_bpo,
                        n_recep, t_recep, n_est, t_est, n_csc, t_csc,
                        contato_autorizado
                    ]
                    wks.append_row(linha)
                    st.session_state.passo = 4
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

# PASSO 4: SUCESSO
elif st.session_state.passo == 4:
    st.balloons()
    st.success("Sua avaliação foi enviada com sucesso! A Escrita Contabilidade agradece.")
    if st.button("Enviar outra resposta"):
        st.session_state.passo = 1
        st.session_state.respostas = {}
        st.rerun()
