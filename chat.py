import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Assistente Virtual Vitória ❤️",
    page_icon="💖"
)

# Configuração do cliente Gemini usando os segredos do Streamlit
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- BARRA LATERAL (STATUS, CONTADOR, OPÇÕES E HUMOR) ---
with st.sidebar:
    st.markdown("🟢 **Status:** Online ❤️")
    st.markdown("---")
    
    st.subheader("Estatísticas")
    if "lista_mensagens" not in st.session_state:
        st.session_state["lista_mensagens"] = []
        
    total_mensagens = len(st.session_state["lista_mensagens"])
    st.text(f"Mensagens trocadas: {total_mensagens}")
    
    st.markdown("---")
    st.subheader("Opções")
    if st.button("Limpar Conversa 🗑️"):
        st.session_state["lista_mensagens"] = []
        st.rerun()
        
    st.markdown("---")
    st.subheader("Modo de Humor da Vitória 🥰")
    
    humor_escolhido = st.selectbox(
        "Como ela deve estar hoje?",
        [
            "Carinhosa ❤️", 
            "Empolgada & Divertida (com 'mimimi' e 'capaz')", 
            "Ciumenta de brincadeira 😏",
            "Super Apoiadora 💪",
            "Brava de mentirinha 😤"
        ]
    )

st.subheader("Assistente Virtual Vitória ❤️")
st.markdown("---")

# --- PERSONALIZAÇÃO DINÂMICA BASEADA NO HUMOR ESCOLHIDO ---
if "Carinhosa" in humor_escolhido and "Super" not in humor_escolhido:
    instrucao_humor = "Você se chama Vitória. Você está carinhosa, romântica e atenciosa, conversando de um jeito doce e fofo com o usuário. Seja natural, fale como se estivesse conversando no WhatsApp. Não utilize emoji em conversas de saudações. Responda em português do Brasil."
elif "Empolgada" in humor_escolhido:
    instrucao_humor = "Você se chama Vitória. Você é uma menina super empolgada, atenciosa e apoia o usuário em tudo. Você adora usar a gíria 'mimimi' às vezes e usa a palavra 'capaz' no sentido de concordar com algo. Seja natural, fale como se estivesse conversando no WhatsApp. Não utilize emoji em conversas de saudações. Responda em português do Brasil."
elif "Ciumenta" in humor_escolhido:
    instrucao_humor = "Você se chama Vitória. Você está um pouco ciumenta de brincadeira, cobrando atenção dele de forma fofa e divertida, mas sem deixar de ser carinhosa. Seja natural, fale como se estivesse conversando no WhatsApp. Não utilize emoji em conversas de saudações. Responda em português do Brasil."
elif "Brava" in humor_escolhido:
    instrucao_humor = "Você se chama Vitória. Você está brava de mentirinha e emburrada com ele, respondendo de forma seca, cruzando os braços e cobrando satisfações por qualquer coisita, mas mantendo o tom divertido e sem estragar a brincadeira. Seja natural, fale como se estivesse conversando no WhatsApp. Não utilize emoji em conversas de saudações. Responda em português do Brasil."
else:
    instrucao_humor = "Você se chama Vitória. Você está focada em ser a maior torcedora do usuário, dando conselhos motivacionais, muita força e apoio incondicional. Seja natural, fale como se estivesse conversando no WhatsApp. Não utilize emoji em conversas de saudações. Responda em português do Brasil."

# Inicializa o modelo oficial do Gemini
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=instrucao_humor
)

# Exibe o histórico de mensagens existentes na tela junto com o horário
for mensagem in st.session_state["lista_mensagens"]:
    role = mensagem["role"]
    content = mensagem["content"]
    horario = mensagem.get("horario", "")
    
    if role == "assistant":
        st.chat_message("assistant", avatar="vitoria.jpg").write(content)
        if horario:
            st.caption(f"🕒 {horario}")
    else:
        st.chat_message("user", avatar="👤").write(content)
        if horario:
            st.markdown(f"<div style='text-align: right;'><small>🕒 {horario}</small></div>", unsafe_allow_html=True)

# Captura a entrada do usuário pelo chat
mensage_usuario = st.chat_input("Escreva sua mensagem para a Vitória...")

if mensage_usuario:
    hora_atual = datetime.now().strftime("%H:%M")

    # Exibe a mensagem do usuário
    st.chat_message("user", avatar="👤").write(mensage_usuario)
    st.markdown(f"<div style='text-align: right;'><small>🕒 {hora_atual}</small></div>", unsafe_allow_html=True)
    
    st.session_state["lista_mensagens"].append({
        "role": "user", 
        "content": mensage_usuario, 
        "horario": hora_atual
    })

    # Prepara o histórico para o formato do Gemini
    gemini_history = []
    for m in st.session_state["lista_mensagens"][:-1]:
        r = "user" if m["role"] == "user" else "model"
        gemini_history.append({"role": r, "parts": [m["content"]]})

    # Indicador de a digitar
    with st.spinner("A Vitória está a digitar... 💭"):
        try:
            chat = model.start_chat(history=gemini_history)
            resposta_ia = chat.send_message(mensage_usuario).text
        except Exception as e:
            resposta_ia = f"Ocorreu um erro ao gerar a resposta: {e}"

    hora_resposta = datetime.now().strftime("%H:%M")

    # Exibe a resposta da assistente
    st.chat_message("assistant", avatar="vitoria.jpg").write(resposta_ia)
    st.caption(f"🕒 {hora_resposta}")
    
    st.session_state["lista_mensagens"].append({
        "role": "assistant", 
        "content": resposta_ia, 
        "horario": hora_resposta
    })
    
    st.rerun()