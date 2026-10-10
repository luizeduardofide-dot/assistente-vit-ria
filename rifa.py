import streamlit as st
import urllib.parse
import json
import os
import time
import requests
from PIL import Image, ImageOps

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Rifa Equipe Zeus - Fórmula SAE",
    page_icon="🏎️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CHAVES DO JSONBIN (CONFIGURADAS) ---
JSONBIN_BIN_ID = st.secrets.get("JSONBIN_BIN_ID", "6ac9e66eac6210605a24aca3")
JSONBIN_API_KEY = st.secrets.get("JSONBIN_API_KEY", "$2a$10$JDZzWPNr4Ih2SxcZmtLkIOJjdLf068P7pNndXwwyTV9ooHEvd6PgK")

# --- DESIGN CUSTOMIZADO (RESPONSIVO E ESCURO) ---
st.markdown("""
    <style>
    /* Força o fundo escuro geral */
    .stApp { 
        background-color: #0b0c10; 
        color: #ffffff; 
    }
    
    /* BLOQUEIO DE ROLAGEM HORIZONTAL E ESPAÇO PARA O HEADER DO STREAMLIT CLOUD */
    html, body, [data-testid="stAppViewContainer"], .main {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    
    [data-testid="stMainBlockContainer"], .block-container {
        padding-left: 10px !important;
        padding-right: 10px !important;
        padding-top: 3.5rem !important; /* Espaço para o cabeçalho não cortar na nuvem */
        padding-bottom: 6rem !important; /* Espaço extra para a faixa flutuante não cobrir o final */
        max-width: 100% !important;
    }

    img { border-radius: 15px; }
    
    /* --- CORREÇÃO ESPECÍFICA APENAS DA LOGO NO MOBILE --- */
    @media (max-width: 768px) {
        .logo-container img {
            max-width: 80px !important;
            margin: 0 auto;
            display: block;
        }
    }
    
    /* --- FAIXA FLUTUANTE FIXA NA TELA --- */
    .banner-flutuante {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #ffcc00, #ff9900);
        color: #000000;
        padding: 14px 20px;
        border-radius: 20px;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.85);
        z-index: 999999;
        text-align: center;
        width: 92%;
        max-width: 520px;
        border: 2px solid #ffffff;
        font-weight: bold;
    }
    
    /* --- PROMOÇÕES --- */
    .promo-container { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; justify-content: center; }
    .promo-card { background: linear-gradient(145deg, #1f2833, #0b0c10); border: 1px solid #3b42f5; border-radius: 10px; padding: 12px; text-align: center; flex: 1 1 100px; box-shadow: 0 4px 8px rgba(59, 66, 245, 0.15); }
    .promo-card.destaque { border: 2px solid #ffcc00; box-shadow: 0 0 12px rgba(255, 204, 0, 0.4); transform: scale(1.03); }
    .promo-qtd { font-size: 1em; font-weight: bold; color: #ffffff; margin-bottom: 4px;}
    .promo-valor { font-size: 1.25em; font-weight: 900; color: #28a745; }
    .promo-tag { font-size: 0.65em; color: #0b0c10; background-color:#ffcc00; padding: 2px 6px; border-radius: 12px; font-weight: bold; margin-top: 6px; display: inline-block;}
    
    /* --- ESTILO DOS BOTÕES DA GRADE (DARK) --- */
    button[kind="secondary"] {
        background-color: #1f2833 !important;
        border: 1px solid #45a29e !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        height: 42px !important;
        width: 100% !important;
        font-size: 15px !important;
        font-weight: bold !important;
        padding: 0 !important;
    }
    button[kind="secondary"]:hover { background-color: #45a29e !important; color: #ffffff !important; }

    button[kind="primary"] {
        background-color: #28a745 !important;
        border: 2px solid #ffffff !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        height: 42px !important;
        width: 100% !important;
        font-weight: 900 !important;
        font-size: 15px !important;
        padding: 0 !important;
    }

    .caixa-status {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 42px; border-radius: 6px; font-weight: bold; font-size: 0.8em; line-height: 1.1; width: 100%;
    }
    .box-res { background-color: #ffc107; color: #000000; border: 1px solid #d39e00; }
    .box-pago { background-color: #dc3545; color: #ffffff; border: 1px solid #bd2130; }

    /* --- FORÇAR 5 COLUNAS APENAS NA GRADE DE NÚMEROS NO MOBILE --- */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"]:nth-child(5)) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 3px !important;
            margin-bottom: 3px !important;
            width: 100% !important;
        }

        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"]:nth-child(5)) > div[data-testid="stColumn"] {
            width: 0 !important;
            min-width: 0 !important;
            flex: 1 1 0% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        button[kind="secondary"], button[kind="primary"], .caixa-status {
            height: 38px !important;
            font-size: 13px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- DADOS E CONFIGURAÇÕES DA RIFA ---
TOTAL_NUMEROS = 350
CHAVE_PIX = "rifaequipezeus@gmail.com"  
NOME_PIX = "Equipe Zeus"
WHATSAPP_CONTATO = "5535997699577"  

# --- FUNÇÃO DE PADRONIZAÇÃO DE IMAGENS EM TAMANHO QUADRADO (1:1) ---
def carregar_imagem_padronizada(caminho, tamanho=(600, 600)):
    if os.path.exists(caminho):
        img = Image.open(caminho)
        return ImageOps.fit(img, tamanho, method=Image.Resampling.LANCZOS)
    return None

# --- SISTEMA DE INTEGRAÇÃO COM O JSONBIN (OTIMIZADO COM CACHE DE 60 SEGUNDOS) ---
@st.cache_data(ttl=60)
def carregar_dados():
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
    headers = {"X-Master-Key": JSONBIN_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            record = response.json().get("record", {})
            numeros = {int(k): v for k, v in record.get("numeros_status", {}).items()}
            compradores = {int(k): v for k, v in record.get("compradores", {}).items()}
            
            for i in range(1, TOTAL_NUMEROS + 1):
                if i not in numeros:
                    numeros[i] = "Disponível"
            return numeros, compradores
    except Exception as e:
        st.error(f"Erro ao carregar dados do banco na nuvem: {e}")

    return {i: "Disponível" for i in range(1, TOTAL_NUMEROS + 1)}, {}

def salvar_dados(numeros_status, compradores):
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": JSONBIN_API_KEY
    }
    payload = {
        "numeros_status": {str(k): v for k, v in numeros_status.items()},
        "compradores": {str(k): v for k, v in compradores.items()}
    }
    try:
        requests.put(url, headers=headers, json=payload, timeout=5)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Erro ao salvar dados na nuvem: {e}")

# --- INICIALIZAÇÃO DE VARIÁVEIS ---
numeros_salvos, compradores_salvos = carregar_dados()

if "numeros_status" not in st.session_state:
    st.session_state.numeros_status = numeros_salvos
if "compradores" not in st.session_state:
    st.session_state.compradores = compradores_salvos
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "reserva_concluida" not in st.session_state:
    st.session_state.reserva_concluida = False
if "dados_reserva" not in st.session_state:
    st.session_state.dados_reserva = {}

# --- FUNÇÃO DE CLIQUE SEGURO ---
def toggle_numero(num):
    if num in st.session_state.carrinho:
        st.session_state.carrinho.remove(num)
    else:
        st.session_state.carrinho.append(num)

def calcular_total(qtd):
    total = 0
    while qtd >= 10:
        total += 25.0
        qtd -= 10
    while qtd >= 8:
        total += 22.0
        qtd -= 8
    while qtd >= 4:
        total += 10.0
        qtd -= 4
    total += qtd * 3.0
    return total

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 3], vertical_alignment="center")

with col_logo:
    if os.path.exists("fotologo.jpeg"):
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image("fotologo.jpeg", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with col_titulo:
    st.markdown("<h2 style='margin: 0; padding: 0; font-size: 1.8rem; font-weight: 800;'>Rifa - Equipe Zeus</h2>", unsafe_allow_html=True)
    st.markdown("<p style='margin: 0; padding-top: 4px; color: #a0a0a0; font-size: 0.95rem;'>Acelerando sonhos com o Fórmula SAE UFLA!</p>", unsafe_allow_html=True)

st.markdown("---")

# --- BANNER DO CARRO ---
if os.path.exists("fotocarro.jpeg"):
    img_original = Image.open("fotocarro.jpeg")
    w, h = img_original.size
    nova_altura = int(w * 0.45)
    topo = (h - nova_altura) // 2
    fundo = topo + nova_altura
    img_cortada = img_original.crop((0, topo, w, fundo))
    st.image(img_cortada, use_container_width=True)

# --- BARRA DE PROGRESSO ---
numeros_indisponiveis = sum(1 for status in st.session_state.numeros_status.values() if status != "Disponível")
porcentagem_vendida = numeros_indisponiveis / TOTAL_NUMEROS

st.write("")
st.markdown(f"### 🔥 Já vendemos **{numeros_indisponiveis}** de **{TOTAL_NUMEROS}** números!")
st.progress(porcentagem_vendida)
st.markdown("---")

# --- PROJETO E PRÊMIOS (RESUMO) ---
col_proj, col_premio = st.columns(2)

with col_proj:
    st.subheader("🏁 O Projeto")
    st.write("Nós projetamos e construímos um carro de corrida do zero para competir! Sua contribuição é o combustível para cobrir os custos de manufatura e colocar o nosso projeto na pista.")

with col_premio:
    st.subheader("🏆 Sorteio: 18/12")
    st.write("Confira as fotos detalhadas dos prêmios na aba **'Ver Prêmios'** logo abaixo!")
    st.markdown("📸 **Siga no Instagram:** [@zeusufla](https://instagram.com/zeusufla)")

st.write("") 

# --- SISTEMA DE ABAS (TABS) ---
aba_comprar, aba_premios = st.tabs(["🎟️ Comprar Números", "🏆 Ver Prêmios"])

# --- CONTEÚDO DA ABA 1: COMPRAR NÚMEROS ---
with aba_comprar:
    st.header("💰 Combos Promocionais")
    st.write("Escolha seus números clicando na grade. O sistema calcula o **desconto automaticamente**!")

    st.markdown("""
    <div class="promo-container">
        <div class="promo-card">
            <div class="promo-qtd">🎟️ 1 Número</div>
            <div class="promo-valor">R$ 3,00</div>
        </div>
        <div class="promo-card">
            <div class="promo-qtd">🎟️ 3 Números</div>
            <div class="promo-valor">R$ 9,00</div>
        </div>
        <div class="promo-card destaque">
            <div class="promo-qtd">🔥 4 Números</div>
            <div class="promo-valor">R$ 10,00</div>
            <div class="promo-tag">MAIS VENDIDO</div>
        </div>
        <div class="promo-card">
            <div class="promo-qtd">⚡ 8 Números</div>
            <div class="promo-valor">R$ 22,00</div>
        </div>
        <div class="promo-card destaque">
            <div class="promo-qtd">🚀 10 Números</div>
            <div class="promo-valor">R$ 25,00</div>
            <div class="promo-tag">PACOTÃO ZEUS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- SELEÇÃO DE NÚMEROS ---
    st.subheader("👇 Clique nos quadradinhos para selecionar:")
    st.markdown("* 🟦 **Disponíveis** | 🟩 **Selecionados** | 🟡 **Reservados** | 🔴 **Pagos**")

    # BARRA FLUTUANTE FIXA NA TELA ENQUANTO HOUVER NÚMEROS SELECIONADOS
    if len(st.session_state.carrinho) > 0:
        qtd_c = len(st.session_state.carrinho)
        st.markdown(f"""
            <div class="banner-flutuante">
                <div style="font-size: 1.15em; margin-bottom: 2px;">🛒 <b>{qtd_c} número(s) selecionado(s)!</b></div>
                <div style="font-size: 0.95em; font-weight: 600;">👇 Role até o final da página para informar seu Nome e pagar.</div>
            </div>
        """, unsafe_allow_html=True)

    cols_por_linha = 5
    for i in range(0, TOTAL_NUMEROS, cols_por_linha):
        cols = st.columns(cols_por_linha)
        for j in range(cols_por_linha):
            num = i + j + 1
            if num <= TOTAL_NUMEROS:
                status = st.session_state.numeros_status[num]
                
                if num in st.session_state.carrinho:
                    cols[j].button(f"{num}", key=f"btn_{num}", type="primary", use_container_width=True, on_click=toggle_numero, args=(num,))
                elif status == "Disponível":
                    cols[j].button(f"{num}", key=f"btn_{num}", type="secondary", use_container_width=True, on_click=toggle_numero, args=(num,))
                elif status == "Reservado":
                    cols[j].markdown(f"<div class='caixa-status box-res'>{num}<br>Res.</div>", unsafe_allow_html=True)
                else:
                    cols[j].markdown(f"<div class='caixa-status box-pago'>{num}<br>Pago</div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- CHECKOUT E PAGAMENTO ---
    if st.session_state.reserva_concluida:
        dados = st.session_state.dados_reserva
        st.success(f"🎉 Reserva confirmada para {dados['nome']}!")
        st.subheader("💳 Falta pouco! Faça o PIX para garantir os números.")
        st.info(f"**Total a pagar: R$ {dados['valor_total']:.2f}** pelos números: {dados['numeros_str']}")
        
        st.write(f"**Favorecido:** {NOME_PIX}")
        st.write("**Copie a Chave PIX abaixo:**")
        st.code(CHAVE_PIX, language="text")
        
        msg = f"Olá! Me chamo {dados['nome']}. Reservei os números [{dados['numeros_str']}] na Rifa da Equipe Zeus. Segue o comprovante do PIX no valor de R$ {dados['valor_total']:.2f}:"
        msg_encoded = urllib.parse.quote(msg)
        link_wpp = f"https://wa.me/{WHATSAPP_CONTATO}?text={msg_encoded}"
        
        st.markdown(f"### 👉 **[CLIQUE AQUI PARA ENVIAR O COMPROVANTE NO WHATSAPP]({link_wpp})**", unsafe_allow_html=True)
        if st.button("Fazer nova compra"):
            st.session_state.reserva_concluida = False
            st.session_state.dados_reserva = {}
            st.rerun()

    elif len(st.session_state.carrinho) > 0:
        qtd_selecionada = len(st.session_state.carrinho)
        valor_final = calcular_total(qtd_selecionada)
        
        st.header("🛒 Fechar Pedido / Finalizar Compra")
        st.write(f"Você selecionou **{qtd_selecionada}** número(s): **{sorted(st.session_state.carrinho)}**")
        st.info(f"💰 **Valor Total com Desconto: R$ {valor_final:.2f}**")
        
        col_nome, col_tel = st.columns(2)
        nome_comprador = col_nome.text_input("Nome Completo:")
        tel_comprador = col_tel.text_input("Seu WhatsApp (com DDD):")
        
        if st.button("Confirmar Reserva e Gerar PIX", type="primary", use_container_width=True):
            if not nome_comprador or not tel_comprador:
                st.error("Por favor, preencha seu nome completo e WhatsApp para continuar.")
            else:
                numeros_atualizados, compradores_atualizados = carregar_dados()
                conflito = [n for n in st.session_state.carrinho if numeros_atualizados.get(n) != "Disponível"]
                
                if conflito:
                    st.error(f"⚠️ Eita! Alguém foi mais rápido e acabou de reservar os números: {conflito}. Por favor, desmarque eles e escolha outros!")
                    st.session_state.numeros_status = numeros_atualizados
                    st.session_state.compradores = compradores_atualizados
                else:
                    for n in st.session_state.carrinho:
                        numeros_atualizados[n] = "Reservado"
                        compradores_atualizados[n] = f"{nome_comprador} ({tel_comprador})"
                    
                    salvar_dados(numeros_atualizados, compradores_atualizados)
                    
                    st.session_state.numeros_status = numeros_atualizados
                    st.session_state.compradores = compradores_atualizados
                    
                    st.session_state.dados_reserva = {
                        "nome": nome_comprador, "telefone": tel_comprador,
                        "valor_total": valor_final, "numeros_str": ", ".join(map(str, sorted(st.session_state.carrinho)))
                    }
                    st.session_state.carrinho = []
                    st.session_state.reserva_concluida = True
                    st.rerun()

# --- CONTEÚDO DA ABA 2: VER PRÊMIOS ---
with aba_premios:
    st.header("🎁 Conheça os nossos Prêmios!")
    st.write("Ao participar na nossa rifa, além de ajudar o projeto, você concorre a estes super prêmios:")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.subheader("🥇 1º LUGAR")
        st.markdown("**Televisão 43\"**")
        img1 = carregar_imagem_padronizada("premio1.jpeg")
        if img1:
            st.image(img1, use_container_width=True)
        else:
            st.info("Imagem da TV em breve!")
            
    with col_p2:
        st.subheader("🥈 2º LUGAR")
        st.markdown("**Airfryer + Kit Parafusadeira**")
        img2 = carregar_imagem_padronizada("premio2.jpeg")
        if img2:
            st.image(img2, use_container_width=True)
        else:
            st.info("Imagem da Airfryer em breve!")
            
    with col_p3:
        st.subheader("🥉 3º LUGAR")
        st.markdown("**Cesta de Queijos**")
        img3 = carregar_imagem_padronizada("premio3.jpeg")
        if img3:
            st.image(img3, use_container_width=True)
        else:
            st.info("Imagem da Cesta em breve!")

# --- PAINEL DO ADMINISTRADOR ---
st.markdown("---")
with st.expander("🔐 Área do Administrador"):
    senha_admin = st.text_input("Senha Admin", type="password")
    if senha_admin == "zeus0709":
        num_admin = st.number_input("Digite o Número que deseja gerenciar:", min_value=1, max_value=TOTAL_NUMEROS, step=1)
        
        col_pago, col_cancela = st.columns(2)
        with col_pago:
            if st.button("✅ Marcar como Pago", type="primary", use_container_width=True):
                numeros_atualizados, compradores_atualizados = carregar_dados()
                numeros_atualizados[num_admin] = "Pago"
                salvar_dados(numeros_atualizados, compradores_atualizados)
                
                st.session_state.numeros_status = numeros_atualizados
                st.session_state.compradores = compradores_atualizados
                st.success(f"Sucesso! Número {num_admin} confirmado como PAGO.")
                time.sleep(1)
                st.rerun()
                
        with col_cancela:
            if st.button("❌ Cancelar Reserva", use_container_width=True):
                numeros_atualizados, compradores_atualizados = carregar_dados()
                numeros_atualizados[num_admin] = "Disponível"
                if num_admin in compradores_atualizados:
                    del compradores_atualizados[num_admin]
                
                salvar_dados(numeros_atualizados, compradores_atualizados)
                
                st.session_state.numeros_status = numeros_atualizados
                st.session_state.compradores = compradores_atualizados
                st.success(f"Reserva cancelada! Número {num_admin} liberado.")
                time.sleep(1)
                st.rerun()