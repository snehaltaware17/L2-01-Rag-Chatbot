import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM, OllamaEmbeddings

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="DocMind AI",
    page_icon="🧠",
    layout="wide"
)

# -------------------- CUSTOM CSS --------------------
# Design direction: "the reading room" — a document sits on a scanner bed while
# a beam of light passes over it. Warm paper + deep archive-ink navy + a single
# amber accent (the beam / the stamp), folios instead of generic numbering,
# dog-eared cards instead of glassmorphism, and a librarian's ink stamp as the
# signature moment when an answer is verified against the source document.
# v2: tightened rhythm so the whole flow sits on one screen, and every surface
# now has a small living detail — drifting motes in the hero, a shimmer sweep
# on cards, a breathing stamp, a hand-drawn underline on focus.
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    :root{
        --paper:      #F7F2E7;
        --paper-line: #E4DAC4;
        --ink:        #1C1B1F;
        --navy:       #16273D;
        --navy-2:     #1F3A5C;
        --amber:      #C97A2B;
        --amber-soft: #E8B978;
        --sage:       #3F6E52;
        --muted:      #6E6656;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--ink); }

    .stApp {
        background:
            repeating-linear-gradient(0deg, rgba(28,27,31,0.015) 0px, rgba(28,27,31,0.015) 1px, transparent 1px, transparent 3px),
            var(--paper);
        background-attachment: fixed;
    }

    .block-container { padding-top: 1.4rem !important; padding-bottom: 1rem !important; max-width: 1180px; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation: none !important; transition: none !important; }
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes riseIn {
        from { opacity: 0; transform: translateY(10px) scale(0.99); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes scanSweep {
        0%   { top: -6%; opacity: 0; }
        8%   { opacity: 0.9; }
        50%  { opacity: 0.9; }
        92%  { opacity: 0; }
        100% { top: 106%; opacity: 0; }
    }
    @keyframes stampIn {
        0%   { transform: rotate(-8deg) scale(2.4); opacity: 0; }
        60%  { transform: rotate(-8deg) scale(0.92); opacity: 0.9; }
        100% { transform: rotate(-8deg) scale(1); opacity: 0.9; }
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.15; }
    }
    @keyframes drift {
        0%   { transform: translate(0,0); opacity: 0.35; }
        50%  { transform: translate(6px,-10px); opacity: 0.8; }
        100% { transform: translate(0,0); opacity: 0.35; }
    }
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(63,110,82,0.35); }
        50%      { box-shadow: 0 0 0 6px rgba(63,110,82,0); }
    }
    @keyframes shimmer {
        0%   { transform: translateX(-120%) skewX(-15deg); }
        100% { transform: translateX(220%) skewX(-15deg); }
    }
    @keyframes underlineGrow {
        from { width: 0%; }
        to   { width: 100%; }
    }
    @keyframes tiltIn {
        from { transform: rotate(-1.5deg) scale(0.8); opacity: 0; }
        to   { transform: rotate(-1.5deg) scale(1); opacity: 1; }
    }
    @keyframes bounceDot {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
        40% { transform: translateY(-4px); opacity: 1; }
    }

    /* ---------- HERO ---------- */
    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(155deg, var(--navy) 0%, var(--navy-2) 60%, #24456B 100%);
        padding: 1.7rem 2.2rem 1.5rem 2.2rem;
        border-radius: 4px;
        margin-bottom: 1.3rem;
        animation: fadeInUp 0.6s ease both;
        border: 1px solid #0E1B2C;
        box-shadow: 0 22px 40px rgba(15, 20, 35, 0.28);
    }
    /* scanning beam — the signature element */
    .hero::before {
        content: "";
        position: absolute;
        left: 0; right: 0;
        height: 46px;
        top: -6%;
        background: linear-gradient(180deg, transparent, rgba(233,185,120,0.28) 45%, rgba(233,185,120,0.55) 50%, rgba(233,185,120,0.28) 55%, transparent);
        animation: scanSweep 5.5s cubic-bezier(.45,.05,.55,.95) infinite;
        pointer-events: none;
    }
    .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        background-image: repeating-linear-gradient(90deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 64px);
        pointer-events: none;
    }
    /* drifting dust motes over the scanner bed */
    .motes span{
        position: absolute;
        width: 3px; height: 3px;
        border-radius: 50%;
        background: var(--amber-soft);
        animation: drift 4.5s ease-in-out infinite;
        pointer-events: none;
    }
    .motes span:nth-child(1){ top: 20%; left: 12%; animation-delay: 0s; }
    .motes span:nth-child(2){ top: 55%; left: 34%; animation-delay: 0.7s; }
    .motes span:nth-child(3){ top: 30%; left: 58%; animation-delay: 1.4s; }
    .motes span:nth-child(4){ top: 68%; left: 78%; animation-delay: 0.4s; }
    .motes span:nth-child(5){ top: 15%; left: 88%; animation-delay: 2s; }
    .motes span:nth-child(6){ top: 78%; left: 22%; animation-delay: 1.1s; }

    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: var(--amber-soft);
        border: 1px solid rgba(233,185,120,0.4);
        padding: 0.3rem 0.7rem;
        border-radius: 3px;
        margin-bottom: 0.8rem;
        position: relative;
        z-index: 1;
    }
    .hero-eyebrow .dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--amber-soft);
        animation: blink 1.8s ease-in-out infinite;
    }
    .hero h1 {
        font-family: 'Fraunces', serif;
        font-optical-sizing: auto;
        font-weight: 600;
        color: #FBF7EE;
        font-size: 2.15rem;
        margin: 0 0 0.35rem 0;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    .hero p {
        color: #C9D3DF;
        font-size: 0.98rem;
        margin: 0;
        max-width: 560px;
        position: relative;
        z-index: 1;
        line-height: 1.5;
    }

    /* ---------- FOLIO TAGS (replaces pill row) ---------- */
    .folio-row {
        display: flex;
        gap: 0.5rem;
        margin: 0 0 0.9rem 0;
        flex-wrap: wrap;
        animation: fadeInUp 0.7s ease 0.1s both;
    }
    .folio {
        background: var(--paper);
        border: 1px dashed var(--paper-line);
        border-radius: 3px;
        padding: 0.4rem 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.73rem;
        font-weight: 500;
        letter-spacing: 0.4px;
        color: var(--muted);
        transition: transform 0.18s ease, border-color 0.18s ease, color 0.18s ease;
    }
    .folio:hover {
        transform: translateY(-3px) rotate(-1deg);
        border-color: var(--amber);
        border-style: solid;
        color: var(--navy);
    }
    .folio b { color: var(--navy); }

    /* ---------- CARDS (dog-eared paper) ---------- */
    .card {
        position: relative;
        overflow: hidden;
        background: #FFFDF7;
        border-radius: 3px;
        padding: 1.2rem 1.5rem 1.35rem 1.5rem;
        border: 1px solid var(--paper-line);
        margin-bottom: 0.9rem;
        box-shadow: 0 1px 0 rgba(28,27,31,0.02), 0 10px 24px rgba(60, 46, 20, 0.05);
        transition: box-shadow 0.25s ease, transform 0.2s ease;
        height: 100%;
    }
    .card.reveal-1 { animation: riseIn 0.55s ease 0.05s both; }
    .card.reveal-2 { animation: riseIn 0.55s ease 0.18s both; }
    .card.reveal-3 { animation: riseIn 0.45s ease both; }
    .card:hover { box-shadow: 0 16px 30px rgba(60, 46, 20, 0.1); transform: translateY(-2px); }
    .card::after {
        content: "";
        position: absolute;
        top: 0; right: 0;
        width: 22px; height: 22px;
        background: linear-gradient(135deg, transparent 50%, var(--paper) 50.5%, #EDE4CC 51%, #EDE4CC 100%);
        border-bottom-left-radius: 3px;
        box-shadow: -2px 2px 4px rgba(60,46,20,0.06);
    }
    /* a light sweep that passes through every card once it appears */
    .card::before {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 40%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(233,185,120,0.16), transparent);
        animation: shimmer 1.6s ease-out 0.3s 1;
        pointer-events: none;
    }

    .step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 42px; height: 24px;
        padding: 0 8px;
        background: var(--navy);
        color: var(--amber-soft);
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.72rem;
        letter-spacing: 0.5px;
        margin-right: 0.6rem;
        border-radius: 2px;
        transform: rotate(-1.5deg);
        animation: tiltIn 0.4s ease both;
        transition: transform 0.2s ease, background 0.2s ease;
    }
    .card:hover .step-num { transform: rotate(2deg) scale(1.06); background: var(--navy-2); }

    .section-title {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 1.18rem;
        color: var(--navy);
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
    }
    .section-sub {
        color: var(--muted);
        font-size: 0.85rem;
        margin: 0 0 0.7rem 3.05rem;
        font-style: italic;
    }

    /* ---------- BUTTONS ---------- */
    .stButton > button {
        position: relative;
        overflow: hidden;
        background: var(--navy);
        color: #FBF7EE;
        border: 1px solid #0E1B2C;
        border-radius: 3px;
        padding: 0.55rem 1.4rem;
        font-weight: 600;
        font-size: 0.94rem;
        letter-spacing: 0.2px;
        transition: transform 0.12s ease, box-shadow 0.2s ease, background 0.2s ease;
        box-shadow: 0 6px 14px rgba(22, 39, 61, 0.25);
    }
    .stButton > button::before {
        content: "";
        position: absolute;
        top: 0; left: -60%;
        width: 40%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(233,185,120,0.35), transparent);
        transform: skewX(-20deg);
        transition: left 0.5s ease;
    }
    .stButton > button:hover::before { left: 130%; }
    .stButton > button:hover {
        background: var(--navy-2);
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(22, 39, 61, 0.3);
    }
    .stButton > button:active {
        transform: scale(0.96) rotate(-0.5deg);
        box-shadow: 0 3px 8px rgba(22, 39, 61, 0.35);
    }

    /* ---------- TEXT INPUT ---------- */
    .stTextInput > div > div > input {
        border-radius: 2px;
        border: none;
        border-bottom: 2px dashed var(--paper-line);
        padding: 0.6rem 0.2rem;
        font-size: 0.98rem;
        font-family: 'JetBrains Mono', monospace;
        background: transparent;
        transition: border-color 0.2s ease;
    }
    .stTextInput > div > div > input:focus {
        border-bottom: 2px solid var(--amber);
        box-shadow: none;
    }

    /* ---------- ANSWER ---------- */
    .answer-wrap { position: relative; }
    .stamp {
        position: absolute;
        top: -14px;
        right: 14px;
        border: 2.5px solid var(--sage);
        color: var(--sage);
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.65rem;
        letter-spacing: 2.5px;
        padding: 3px 10px;
        border-radius: 3px;
        transform: rotate(-8deg);
        opacity: 0.9;
        animation: stampIn 0.5s cubic-bezier(.34,1.56,.64,1) 0.15s both, glowPulse 2.4s ease-in-out 0.7s infinite;
        background: rgba(63,110,82,0.04);
        z-index: 2;
    }
    .answer-box {
        background: #FBFAF3;
        border-left: 3px solid var(--sage);
        border-radius: 2px;
        padding: 1.1rem 1.4rem;
        font-size: 1rem;
        color: #1F3327;
        line-height: 1.65;
        animation: riseIn 0.4s ease both;
    }

    /* thinking dots while the model works */
    .thinking-dots{ display:flex; gap:5px; align-items:center; padding: 0.4rem 0; }
    .thinking-dots span{
        width:7px; height:7px; border-radius:50%;
        background: var(--amber);
        animation: bounceDot 1.2s ease-in-out infinite;
    }
    .thinking-dots span:nth-child(2){ animation-delay: 0.15s; }
    .thinking-dots span:nth-child(3){ animation-delay: 0.3s; }

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(190deg, var(--navy) 0%, #10202F 100%);
        border-right: 1px solid #0B1620;
    }
    section[data-testid="stSidebar"] * { color: #DCE4EC !important; }
    section[data-testid="stSidebar"] h2 {
        color: #FBF7EE !important;
        font-family: 'Fraunces', serif !important;
        font-weight: 600 !important;
    }
    .sidebar-logo {
        font-size: 1.7rem;
        margin-bottom: 0.1rem;
        letter-spacing: 3px;
        font-family: 'JetBrains Mono', monospace;
        color: var(--amber-soft) !important;
        animation: fadeInUp 0.5s ease both;
    }
    .sidebar-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(233,185,120,0.18);
        border-left: 2px solid var(--amber-soft);
        border-radius: 2px;
        padding: 0.75rem 0.9rem;
        margin: 0.55rem 0;
        transition: border-color 0.2s ease, background 0.2s ease;
    }
    .sidebar-card:hover { border-color: var(--amber-soft); background: rgba(255,255,255,0.07); }
    .sidebar-card b { color: var(--amber-soft) !important; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.4px; }

    hr { border-color: var(--paper-line); margin: 0.6rem 0; }

    .footer-text {
        text-align: center;
        color: var(--muted);
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 0.88rem;
        margin-top: 1rem;
        letter-spacing: 0.2px;
        opacity: 0.8;
    }

    /* tighten Streamlit's own vertical gaps between elements */
    div[data-testid="stVerticalBlock"] > div { margin-bottom: 0 !important; }
    div[data-testid="stMarkdownContainer"] p { margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

# -------------------- HERO HEADER --------------------
st.markdown("""
<div class="hero">
    <div class="motes"><span></span><span></span><span></span><span></span><span></span><span></span></div>
    <div class="hero-eyebrow"><span class="dot"></span>DOCUMENT INTELLIGENCE, ON THE BENCH</div>
    <h1>🧠 DocMind AI</h1>
    <p>Lay a PDF on the scanner bed. Ask it anything. Every answer is checked against the page it came from before it reaches you.</p>
</div>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR (no tech stack shown) --------------------
with st.sidebar:
    st.markdown('<div class="sidebar-logo">✦ ARCHIVE</div>', unsafe_allow_html=True)
    st.markdown("## DocMind AI")
    st.write("Turn any PDF into a conversation. Ask questions and get instant, accurate answers grounded in your document.")
    st.markdown("""
    <div class="sidebar-card">
        <b>HOW IT WORKS</b><br><br>
        01 · Click <b>Process Document</b><br>
        02 · Wait for it to finish indexing<br>
        03 · Ask any question about the content
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-card">
        <b>TIP</b><br><br>
        Keep questions specific and grounded in the document for the most accurate answers.
    </div>
    """, unsafe_allow_html=True)

pdf_path = "data/sample.pdf"

# -------------------- PROCESS + ASK, SIDE BY SIDE TO SAVE VERTICAL SPACE --------------------
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown('<div class="card reveal-1">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="step-num">NO.01</span>Process Document</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Index your PDF so DocMind AI can search and reason over it.</div>', unsafe_allow_html=True)

    if st.button("🚀 Process Document"):
        with st.spinner("Reading and indexing your document... ⏳"):
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=400,
                chunk_overlap=50
            )
            chunks = splitter.split_documents(documents)
            embeddings = OllamaEmbeddings(
                model="nomic-embed-text"
            )
            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory="chroma_db"
            )
        st.success("✅ Document processed successfully! You can now ask questions.")
        st.balloons()

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card reveal-2">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="step-num">NO.02</span>Ask a Question</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Type a question and get an answer grounded in your document.</div>', unsafe_allow_html=True)

    question = st.text_input(
        "Enter your question",
        placeholder="e.g. What is Business Intelligence?",
        label_visibility="collapsed"
    )

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- ANSWER --------------------
if question:
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown(
        '<div class="thinking-dots"><span></span><span></span><span></span></div>',
        unsafe_allow_html=True
    )

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )
    vector_db = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )
    retriever = vector_db.as_retriever(
        search_kwargs={"k": 1}
    )
    relevant_docs = retriever.invoke(question)
    context = "\n\n".join(
        [doc.page_content for doc in relevant_docs]
    )
    llm = OllamaLLM(
        model="qwen2.5:0.5b",
        temperature=0.2
    )
    prompt = f"""
You are a PDF Question Answering Assistant.
Answer ONLY using the information provided in the context.
If the answer is not present in the context, reply:
"I couldn't find this information in the PDF."
Do NOT use your own knowledge.
Do NOT add extra information.
Keep the answer faithful to the PDF.
Context:
{context}
Question:
{question}
Answer:
"""
    response = llm.invoke(prompt)
    thinking_placeholder.empty()

    st.markdown('<div class="card reveal-3">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="step-num">✓</span>Answer</div>', unsafe_allow_html=True)
    st.markdown(f'''
    <div class="answer-wrap">
        <div class="stamp">VERIFIED</div>
        <div class="answer-box">{response}</div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- FOOTER --------------------
st.markdown('<div class="footer-text">Made with care for smarter document understanding 💜</div>', unsafe_allow_html=True)