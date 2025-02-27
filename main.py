from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import requests
from teste import informations
from datetime import datetime


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


def generate_pdf(products: list, output_file: str):
    """Gera um PDF com até 3 produtos por página, incluindo imagens e barras personalizadas."""
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    product_count = 0  # Contador de produtos na página

    for product in products:
        if product['product']['quantidadeCalibrada'] >= 200 or product['product']['quantidadeGeral'] >= 200:
            # Carregar a imagem do produto
            image_url = product['images'][0].get('url')
            img = None
            if image_url:
                image_data = download_image(image_url)
                if image_data:
                    img = Image(image_data, width=200, height=200)

            # Criar os textos do produto
            product_name = Paragraph(f"<b>{product['product']['name'].upper()}</b>", styles['Heading2'])  # Nome maior e mais visível
            product_color = Paragraph(f"<b>Cor:</b> {product['product']['color'].upper()}", styles['Normal'])
            product_size = Paragraph(f"<b>Tamanho:</b> {product['product']['height'].upper()}", styles['Normal'])
            product_group = Paragraph(f"<b>Grupo:</b> {product['product']['groupProduct'].upper()}", styles['Normal'])
            product_price = Paragraph(f"<b>Preço:</b> R$ {product['product']['custo']:.2f}", styles['Normal'])

            # Criar tabela com imagem (esquerda) e informações (direita)
            data = [[img, [product_name, Spacer(1, 10), product_color,
                           Spacer(1, 10), product_size, Spacer(1, 10),
                           product_group, Spacer(1, 10), product_price]]]

            table = Table(data, colWidths=[170, 350])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Mantém alinhado verticalmente
                ('LEFTPADDING', (1, 0), (1, 0), 40),  # Espaço entre imagem e texto
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # **Texto à esquerda**
            ]))

            # Adiciona tabela ao PDF
            elements.append(table)

            # Adiciona um espaço entre os produtos
            elements.append(Spacer(1, 20))

            # Incrementa o contador de produtos
            product_count += 1

            # A cada 3 produtos, adiciona uma quebra de página
            if product_count == 3:
                elements.append(PageBreak())
                product_count = 0  # Reinicia o contador para a nova página

    # onFirstPage -> Define que a função draw_page_frame(canvas, doc) será chamada na primeira página do PDF para
    # desenhar algo (neste caso, as barras superior e inferior).

    # onLaterPages -> Define que a mesma função draw_page_frame(canvas, doc) será chamada em todas as
    # páginas subsequentes.

    # Gera o PDF chamando a função `draw_page_frame`
    doc.build(elements, onFirstPage=draw_page_frame, onLaterPages=draw_page_frame)


def draw_page_frame(canvas, doc):
    """Desenha as barras verdes no topo e na base de cada página."""
    width, height = A4  # Obtém tamanho da página

    # Configura a cor verde
    canvas.setFillColorRGB(0.0, 0.47, 0.35)  # Verde escuro (RGB)

    # Desenha a barra superior
    canvas.rect(0,
                height - 68,
                width,
                68,
                fill=1,
                stroke=0)

    # Desenha a barra inferior
    canvas.rect(0,
                -2,
                width,
                68,
                fill=1,
                stroke=0)

    # Configura o texto dentro das barras
    canvas.setFillColorRGB(1, 1, 1)  # Cor branca para o texto
    canvas.setFont("Helvetica-Bold", 20)

    # Texto superior
    canvas.drawCentredString(width / 2, height - 42, "BAGAGGIO")

    # # Texto inferior
    # canvas.drawCentredString(width / 2, 20, "")


# Exemplo de uso
products = [
    {
        "name": "Produto 1",
        "price": 100.0,
        "description": "Descrição do Produto 1",
        "image_url": "imagem"
    },
    {
        "name": "Produto 2",
        "price": 200.0,
        "description": "Descrição do Produto 2",
        "image_url": "imagem"
    },
    # Adicione mais produtos conforme necessário
]

# Gerar PDFs
# generate_pdf_product_pages(products, "produtos_por_pagina.pdf")
# generate_pdf_table(products, "tabela_de_produtos.pdf")

tempo_inicial = datetime.now()

generate_pdf(informations, 'tabela_de_produtos_real.pdf')

tempo_final = datetime.now()

print(f'Tempo percorrido: {tempo_final - tempo_inicial}')
