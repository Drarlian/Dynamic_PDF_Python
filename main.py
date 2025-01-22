from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import requests


def download_image(url):
    """Faz o download da imagem a partir de uma URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)  # Retorna a imagem como BytesIO
    return None


def generate_pdf_product_pages(products: list, output_file: str):
    """Gera um PDF com uma página por produto, incluindo a imagem."""
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    for product in products:
        # Título do produto
        elements.append(Paragraph(f"<b>{product['name']}</b>", styles['Title']))

        # Descrição ou informações adicionais
        elements.append(Paragraph(f"Preço: R$ {product['price']}", styles['Normal']))
        elements.append(Paragraph(f"Descrição: {product['description']}", styles['Normal']))

        # Imagem do produto
        image_url = product.get('image_url')
        if image_url:
            image_data = download_image(image_url)
            if image_data:
                img = Image(image_data, width=200, height=200)  # Define tamanho fixo da imagem
                elements.append(img)

        # Adiciona uma quebra de página após cada produto
        elements.append(PageBreak())

    doc.build(elements)


def generate_pdf_table(products, output_file):
    """Gera um PDF contendo uma tabela com todos os produtos."""
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    # elements = []
    elements = [Paragraph(f"<b>Planilha Teste</b>", styles['Title'])]  # Iniciando a página com um título.

    # Adiciona um espaço entre o título e a tabela
    elements.append(Spacer(1, 20))  # Largura 1 (não importa para vertical), altura 20

    # Define o cabeçalho da tabela
    data = [["Nome", "Preço", "Descrição"]]

    # Adiciona os produtos à tabela
    for product in products:
        data.append([product['name'], f"R$ {product['price']}", product['description']])

    # O repeatRows é essencial para tabelas que se espalham por várias páginas.
    # O valor 1 é usado para repetir apenas a primeira linha(geralmente o cabeçalho) nas demais páginas.
    # Ele melhora a legibilidade e torna o documento mais profissional e organizado.

    # Cria a tabela
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fundo do cabeçalho
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto do cabeçalho
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fundo das linhas
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Linhas da tabela
    ]))

    elements.append(table)
    doc.build(elements)


# Exemplo de uso
products = [
    {
        "name": "Produto 1",
        "price": 100.0,
        "description": "Descrição do Produto 1",
        "image_url": "https://lojabagaggio.vteximg.com.br/arquivos/ids/2333095/0018587586002---MALA-QUEBEC-PEQ-185”-ROSE-PP--2-.jpg"
    },
    {
        "name": "Produto 2",
        "price": 200.0,
        "description": "Descrição do Produto 2",
        "image_url": "https://lojabagaggio.vteximg.com.br/arquivos/ids/2334274/0018587458002---MALA-QUEBEC-PEQ-185--PRETO-PP--2-.jpg"
    },
    # Adicione mais produtos conforme necessário
]

# Gerar PDFs
generate_pdf_product_pages(products, "produtos_por_pagina.pdf")
generate_pdf_table(products, "tabela_de_produtos.pdf")
