# app_certificados.py
# Streamlit app to generate certificates in PDF from a template image and a list of names.
# The names can come from a spreadsheet (.xlsx or .csv) with a column named 'nome',
# or be typed one by one in the app.
#
# Requirements (put in requirements.txt):
# streamlit
# pillow
# pandas
# openpyxl
# PyPDF2
#
# How to run:
# 1. Create a virtualenv and install requirements:
#    python -m venv .venv
#    source .venv/bin/activate   (on Windows: .venv\Scripts\activate)
#    pip install -r requirements.txt
# 2. Run the app:
#    streamlit run app_certificados.py
#
# Structure:
# - app_certificados.py -> interface (Streamlit)
# - gerador_core.py     -> regras de negócio (nomes, renderização e exportação)
#
# Notes about fonts:
# The app lists the .ttf/.otf files inside the 'fonts/' folder. If none is found it tries Arial (arial.ttf)
# and, as a last resort, Pillow's default font.

import os
from datetime import datetime

import streamlit as st
from PIL import Image

from gerador_core import (
    ConfigTexto,
    EXTENSOES_PLANILHA,
    FONTE_PADRAO,
    exportar_pdf_unico,
    exportar_zip,
    gerar_pdfs,
    ler_nomes_planilha,
    listar_fontes,
    normalizar_nomes,
    renderizar_certificado,
)

st.set_page_config(page_title="Gerador de Certificados", layout="wide")

st.title("Gerador de Certificados")
st.write(
    "Faça upload do template (PNG/JPG) e escolha como informar os nomes: "
    "por uma planilha (.xlsx ou .csv) com a coluna 'nome', ou digitando um por um."
)

ORIGEM_PLANILHA = "Planilha (.xlsx / .csv)"
ORIGEM_MANUAL = "Digitar manualmente"
NOME_EXEMPLO = "Nome Inserido"

# Estado da lista de nomes digitados (persiste entre as execuções do Streamlit)
if "nomes_manuais" not in st.session_state:
    st.session_state.nomes_manuais = []

# Sidebar configs
st.sidebar.header("Configurações")
# Fontes disponíveis
font_names = listar_fontes("fonts")
if not font_names:
    st.sidebar.warning("Nenhuma fonte encontrada na pasta 'fonts/'.")
    FONT_PATH = FONTE_PADRAO
else:
    FONT_PATH = os.path.join("fonts", st.sidebar.selectbox("Selecione a fonte", font_names))

default_font_size = st.sidebar.slider("Tamanho de fonte (inicial)", min_value=20, max_value=180, value=48)
max_width_pct = st.sidebar.slider("Largura máxima do nome (% da largura da imagem)", min_value=40, max_value=95, value=80)

# Y position como prct em slider
y_pos_pct = st.sidebar.slider("Posição vertical do nome", min_value=0, max_value=100, value=43)

# X como slides tbm
x_pos_pct = st.sidebar.slider("Posição horizontal do nome", 0, 100, 50)


fix_size = st.sidebar.checkbox("Usar tamanho fixo para todos os nomes", value=True)
gerar_pdf_unico = st.sidebar.checkbox("Gerar um único PDF com todos os certificados", value=False)

# Define nome do arquivo
if "output_zip_name" not in st.session_state:
    st.session_state.output_zip_name = f"certificados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

output_zip_name = st.sidebar.text_input(
    "Nome do arquivo de saída",
    value=st.session_state.output_zip_name,
    key="zip_name_input"
)
st.session_state.output_zip_name = output_zip_name  # salva edição

config = ConfigTexto(
    font_path=FONT_PATH,
    font_size=default_font_size,
    max_width_pct=max_width_pct,
    x_pct=x_pos_pct,
    y_pct=y_pos_pct,
    tamanho_fixo=fix_size,
)


# Callbacks da lista manual

def adicionar_nome():
    """Adiciona o nome digitado à lista e limpa o campo (chamado ao apertar Enter ou 'Adicionar')."""
    novos = normalizar_nomes([st.session_state.campo_nome])
    if novos:
        nome = novos[0]
        if nome in st.session_state.nomes_manuais:
            st.session_state.aviso_nome = f"'{nome}' já estava na lista e foi adicionado novamente."
        st.session_state.nomes_manuais.append(nome)


def remover_nome(indice):
    st.session_state.nomes_manuais.pop(indice)


def limpar_nomes():
    st.session_state.nomes_manuais = []


uploaded_image = st.file_uploader("Upload do template do certificado (PNG/JPG)", type=["png", "jpg", "jpeg"])

origem = st.radio("Origem dos nomes", [ORIGEM_PLANILHA, ORIGEM_MANUAL], horizontal=True)

# Cada origem só precisa produzir uma lista de nomes; o restante do fluxo é o mesmo.
nomes = []
erro_nomes = None

if origem == ORIGEM_PLANILHA:
    uploaded_sheet = st.file_uploader(
        "Upload da planilha (.xlsx ou .csv) com coluna 'nome'", type=list(EXTENSOES_PLANILHA)
    )
    if uploaded_sheet is not None:
        try:
            nomes, aviso = ler_nomes_planilha(uploaded_sheet, uploaded_sheet.name)
            if aviso:
                st.warning(aviso)
            st.caption(f"{len(nomes)} nome(s) encontrado(s) na planilha.")
        except ValueError as e:
            erro_nomes = str(e)
            st.error(erro_nomes)
else:
    with st.form("form_nome", clear_on_submit=True, border=False):
        col_campo, col_botao = st.columns([5, 1], vertical_alignment="bottom")
        with col_campo:
            st.text_input(
                "Digite um nome e aperte Enter",
                key="campo_nome",
                placeholder="Ex.: Maria da Silva",
            )
        with col_botao:
            st.form_submit_button("Adicionar", on_click=adicionar_nome, use_container_width=True)

    if "aviso_nome" in st.session_state:
        st.warning(st.session_state.pop("aviso_nome"))

    nomes = list(st.session_state.nomes_manuais)
    if nomes:
        col_total, col_limpar = st.columns([5, 1], vertical_alignment="center")
        col_total.caption(f"{len(nomes)} nome(s) na lista.")
        col_limpar.button("Limpar lista", on_click=limpar_nomes, use_container_width=True)

        with st.container(height=min(60 + 45 * len(nomes), 320)):
            for i, nome in enumerate(nomes):
                col_nome, col_remover = st.columns([12, 1], vertical_alignment="center")
                col_nome.write(f"{i + 1}. {nome}")
                col_remover.button("❌", key=f"remover_{i}", on_click=remover_nome, args=(i,), help="Remover")
    else:
        st.caption("Nenhum nome adicionado ainda.")

# Duas colunas principais com as demais informações
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Pré-visualização do template**")
    preview_placeholder = st.empty()
with col2:

    generate_btn = st.button("Gerar certificados")


image = None
if uploaded_image is not None:
    image = Image.open(uploaded_image).convert("RGBA")
    # Mostra o primeiro nome real da lista, quando houver
    nome_preview = nomes[0] if nomes else NOME_EXEMPLO
    preview_placeholder.image(renderizar_certificado(image, nome_preview, config), use_container_width=True)


if generate_btn:
    if image is None:
        st.warning("Por favor envie o template antes de gerar.")
    elif erro_nomes:
        st.error(erro_nomes)
    elif not nomes:
        if origem == ORIGEM_PLANILHA:
            st.warning("Envie uma planilha com pelo menos um nome válido antes de gerar.")
        else:
            st.warning("Adicione pelo menos um nome à lista antes de gerar.")
    else:
        # Geração dos certificados
        with st.spinner(f"Gerando {len(nomes)} certificado(s)..."):
            pdf_list = gerar_pdfs(image, nomes, config)

        # --- Unir ou compactar ---
        if gerar_pdf_unico:
            merged_pdf = exportar_pdf_unico(pdf_list)
            st.success(f"Gerado um único PDF com {len(nomes)} certificados.")
            st.download_button("Baixar PDF único", data=merged_pdf, file_name="certificados_unificados.pdf", mime="application/pdf")

        else:
            zip_buffer = exportar_zip(nomes, pdf_list)
            st.success(f"Gerados {len(nomes)} certificados — download pronto.")
            st.download_button("Baixar todos os PDFs (.zip)", data=zip_buffer, file_name=output_zip_name, mime='application/zip')


st.markdown("---")
st.markdown(
    """
    Desenvolvido por **Arthur de Morais**  usando Pillow + Streamlit  
    [GitHub](https://github.com/ArthurTiso) / [LinkedIn](https://www.linkedin.com/in/arthur-de-morais-marques-222308306/)
    """,
    unsafe_allow_html=True
)
