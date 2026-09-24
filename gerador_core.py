# gerador_core.py
# Regras de negócio do gerador de certificados, sem nenhuma dependência do Streamlit.
#
# Organização:
#   1. Fontes          -> listar e carregar arquivos de fonte
#   2. Nomes           -> obter e limpar a lista de nomes (planilha, CSV, digitação...)
#   3. Renderização    -> desenhar um nome sobre o template
#   4. Exportação      -> transformar os certificados em PDF / ZIP
#
# Para adicionar uma nova origem de nomes, basta criar uma função que devolva
# uma list[str] passando por normalizar_nomes(). O restante do fluxo não muda.

import io
import os
import zipfile
from dataclasses import dataclass
from functools import lru_cache

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------------------------
# 1. Fontes
# ---------------------------------------------------------------------------

EXTENSOES_FONTE = (".ttf", ".otf")
FONTE_PADRAO = "arial.ttf"


def listar_fontes(pasta="fonts"):
    """Lista os arquivos de fonte da pasta, sem diferenciar maiúsculas na extensão (.TTF, .ttf, .otf)."""
    if not os.path.isdir(pasta):
        return []
    return sorted(
        f for f in os.listdir(pasta)
        if f.lower().endswith(EXTENSOES_FONTE)
    )


@lru_cache(maxsize=512)
def load_font(font_path, size):
    """Guarda em cache as fontes já abertas. Tenta carregar a fonte especificada. Se falhar, tenta Arial. Se falhar novamente, usa a fonte padrão."""
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        try:
            return ImageFont.truetype(FONTE_PADRAO, size)
        except OSError:
            return ImageFont.load_default()


def fit_text_to_width(draw, text, font_path, initial_font_size, max_width):
    """Ajusta o tamanho da fonte para que o texto caiba na largura especificada."""
    font_size = initial_font_size
    while font_size > 1:
        font = load_font(font_path, font_size)
        w, h = medir_texto(draw, text, font)
        if w <= max_width:
            return font, (w, h)
        font_size -= 1
    return font, (w, h)


def medir_texto(draw, text, font):
    """Retorna (largura, altura) do texto com a fonte informada."""
    try:
        # Pillow 10+
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        # Pillow <10
        return draw.textsize(text, font=font)


# ---------------------------------------------------------------------------
# 2. Nomes
# ---------------------------------------------------------------------------

COLUNA_NOMES = "nome"
EXTENSOES_PLANILHA = ("xlsx", "csv")


def normalizar_nomes(valores):
    """Limpa uma sequência de valores e devolve uma lista de nomes válidos.

    - ignora células vazias (None / NaN) e textos em branco
    - remove espaços nas pontas e espaços repetidos no meio do nome
    """
    nomes = []
    for valor in valores:
        if valor is None or (not isinstance(valor, str) and pd.isna(valor)):
            continue
        nome = " ".join(str(valor).split())
        if nome:
            nomes.append(nome)
    return nomes


def _ler_csv(arquivo):
    """Lê um CSV detectando o separador (';' do Excel brasileiro ou ',') e a codificação."""
    conteudo = arquivo.read()
    if isinstance(conteudo, str):
        texto = conteudo
    else:
        try:
            texto = conteudo.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = conteudo.decode("latin-1")

    primeira_linha = texto.splitlines()[0] if texto.strip() else ""
    separador = ";" if ";" in primeira_linha else ","
    return pd.read_csv(io.StringIO(texto), sep=separador, dtype=str, skip_blank_lines=True)


def ler_nomes_planilha(arquivo, nome_arquivo):
    """Lê um arquivo .xlsx ou .csv e retorna (nomes, aviso).

    Usa a coluna 'nome' (sem diferenciar maiúsculas). Se ela não existir,
    usa a primeira coluna e devolve um aviso explicando isso.
    Lança ValueError com uma mensagem amigável em caso de erro.
    """
    extensao = os.path.splitext(nome_arquivo)[1].lower().lstrip(".")
    try:
        if extensao == "csv":
            df = _ler_csv(arquivo)
        elif extensao == "xlsx":
            df = pd.read_excel(arquivo)
        else:
            raise ValueError(f"Formato não suportado: .{extensao}")
    except pd.errors.EmptyDataError as e:
        raise ValueError("O arquivo está vazio.") from e
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Erro ao ler o arquivo: {e}") from e

    if df.columns.empty:
        raise ValueError("O arquivo está vazio.")

    aviso = None
    coluna = next(
        (c for c in df.columns if str(c).strip().lower() == COLUNA_NOMES),
        None,
    )
    if coluna is None:
        coluna = df.columns[0]
        aviso = f"A coluna '{COLUNA_NOMES}' não foi encontrada. Usando a primeira coluna: {coluna}"

    return normalizar_nomes(df[coluna].tolist()), aviso


# ---------------------------------------------------------------------------
# 3. Renderização
# ---------------------------------------------------------------------------

@dataclass
class ConfigTexto:
    """Configurações de como o nome é escrito sobre o template."""
    font_path: str
    font_size: int
    max_width_pct: int
    x_pct: int
    y_pct: int
    tamanho_fixo: bool
    cor: tuple = (0, 0, 0, 255)


def renderizar_certificado(template, nome, config):
    """Desenha o nome sobre uma cópia do template e devolve a nova imagem (RGBA)."""
    base = template.copy().convert("RGBA")
    draw = ImageDraw.Draw(base)
    W, H = base.size

    y = int(H * (config.y_pct / 100.0))
    max_w = int(W * (config.max_width_pct / 100.0))
    font_path = config.font_path.strip() or FONTE_PADRAO

    if config.tamanho_fixo:
        font = load_font(font_path, config.font_size)
        text_w, _ = medir_texto(draw, nome, font)
    else:
        font, (text_w, _) = fit_text_to_width(draw, nome, font_path, config.font_size, max_w)

    x = int(W * (config.x_pct / 100.0)) - (text_w // 2)
    draw.text((x, y), nome, font=font, fill=config.cor)
    return base


# ---------------------------------------------------------------------------
# 4. Exportação
# ---------------------------------------------------------------------------

def imagem_para_pdf(imagem):
    """Converte uma imagem em bytes de um PDF de uma página."""
    pdf_bytes = io.BytesIO()
    imagem.convert("RGB").save(pdf_bytes, format="PDF", resolution=300)
    return pdf_bytes.getvalue()


def gerar_pdfs(template, nomes, config):
    """Gera um PDF (em bytes) para cada nome, na mesma ordem da lista."""
    return [imagem_para_pdf(renderizar_certificado(template, nome, config)) for nome in nomes]


def nome_arquivo_seguro(nome):
    """Remove caracteres que não podem aparecer em nomes de arquivo."""
    return "".join(c for c in nome if c.isalnum() or c in (" ", "-", "_")).rstrip()


def exportar_zip(nomes, pdfs):
    """Compacta os PDFs em um .zip, com arquivos numerados ('001 - Nome.pdf')."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for idx, (nome, pdf) in enumerate(zip(nomes, pdfs), start=1):
            zipf.writestr(f"{idx:03d} - {nome_arquivo_seguro(nome)}.pdf", pdf)
    zip_buffer.seek(0)
    return zip_buffer


def exportar_pdf_unico(pdfs):
    """Junta todos os PDFs em um único arquivo."""
    from PyPDF2 import PdfMerger

    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(io.BytesIO(pdf))
    merged_pdf = io.BytesIO()
    merger.write(merged_pdf)
    merger.close()
    merged_pdf.seek(0)
    return merged_pdf
