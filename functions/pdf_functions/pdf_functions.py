from reportlab.lib.pagesizes import A4, A2
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import requests


# Lista com as URLs das imagens pré-determinadas para as 4 primeiras páginas
default_images = [
    "default_images/IMAGEM1.png",
    "default_images/IMAGEM2.png",
    "default_images/IMAGEM3.png",
    "default_images/IMAGEM4.png"
]

CUSTOM_SIZE = (4000, 2250)  # Definindo um tamanho personalizado


def download_image(url):
    """Faz o download da imagem a partir de uma URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)  # Retorna a imagem como BytesIO
    return None


def generate_pdf_product_pages_test(products: list, output_file: str):
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


def generate_pdf_table_legacy_test(products, output_file):
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


def generate_pdf_a4(products: list, output_file: str):
    """
        Gera um PDF com até 3 produtos por página, incluindo imagens e barras personalizadas.
        O PDF gerado é uma folha A4.
    """
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    product_count = 0  # Contador de produtos na página

    for _ in default_images:
        elements.append(PageBreak())

    for product in products:
        if product['product']['quantidadeCalibrada'] >= 200 or product['product']['quantidadeGeral'] >= 200:
            # Carregar a imagem do produto
            image_url = product['images'][0].get('url')
            if image_url:
                image_data = download_image(image_url)
                if image_data:
                    img = Image(image_data, width=200, height=200)
                else:
                    continue
            else:
                continue

            # Criar os textos do produto
            product_name = Paragraph(f"<b>{product['product']['name'].upper()}</b>",
                                     styles['Heading2'])  # Nome maior e mais visível
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


def generate_pdf_personalized(products: list, output_file: str):
    """
        Gera um PDF com até 3 produtos por página, incluindo imagens e barras personalizadas.
        O PDF gerado é uma folha A2.
    """

    doc = SimpleDocTemplate(
        output_file,
        pagesize=CUSTOM_SIZE,
        leftMargin=0,
        rightMargin=50,
        topMargin=310,    # Espaço para a barra
        bottomMargin=50
    )
    styles = getSampleStyleSheet()
    elements = []
    product_count = 0  # Contador de produtos na página
    product_rows = []  # Lista para armazenar linhas de produtos
    row = []  # Linha atual de produtos

    # Exemplo de estilos maiores para os textos
    big_name_style = ParagraphStyle(
        'BigName',
        parent=styles['Heading2'],
        fontSize=60,
        leading=75,  # -> Controla o espaçamento entre linhas do parágrafo.
        spaceAfter=15,
    )
    normal_style = ParagraphStyle(
        'MyNormal',
        parent=styles['Normal'],
        fontSize=50,
        leading=14
    )

    for _ in default_images:
        elements.append(PageBreak())

    for product in products:
        if product['product']['quantidadeCalibrada'] >= 200 or product['product']['quantidadeGeral'] >= 200:
            # Carregar a imagem do produto
            image_url = product['images'][0].get('url')
            if image_url:
                image_data = download_image(image_url)
                if image_data:
                    img = Image(image_data, width=800, height=800)
                else:
                    continue
            else:
                continue

            # Criar os textos do produto
            product_name = Paragraph(f"<b>{product['product']['name'].upper()}</b>", big_name_style)

            product_color = Paragraph(f"<b>Cor:</b> {product['product']['color'].upper()}", normal_style)
            product_size = Paragraph(f"<b>Tamanho:</b> {product['product']['height'].upper()}", normal_style)
            product_group = Paragraph(f"<b>Grupo:</b> {product['product']['groupProduct'].upper()}", normal_style)
            product_price = Paragraph(f"<b>Preço:</b> R$ {product['product']['custo']:.2f}", normal_style)
            product_material = Paragraph(f"<b>Material:</b> {product['product']['material'].upper()}", normal_style)
            product_polegadas = Paragraph(f"<b>Polegadas:</b> {product['product']['polegadas'].upper()}", normal_style)

            # Criar tabela com imagem (esquerda) e informações (direita)
            data = [[img, [product_name, Spacer(1, 80), product_color,
                           Spacer(1, 60), product_size, Spacer(1, 60),
                           product_group, Spacer(1, 60), product_price,
                           Spacer(1, 60), product_material,
                           Spacer(1, 60), product_polegadas]]]

            table = Table(data, colWidths=[750, 1500])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Mantém alinhado verticalmente
                ('LEFTPADDING', (1, 0), (1, 0), 20),  # Espaço entre imagem e texto
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Texto alinhado à esquerda
                # ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                # ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            row.append(table)  # Adiciona o produto à linha atual
            product_count += 1

            # Se a linha tiver 2 produtos, adiciona à lista de linhas
            if len(row) == 2:
                product_rows.append(row)
                row = []  # Reinicia a linha

            # A cada 4 produtos (2 linhas de 2 colunas), adiciona ao PDF e faz a quebra de página
            if product_count == 4:
                # [(CUSTOM_SIZE[0] / 2) - 50] * 2 = [950, 950] -> 2 elementos no array = 2 colunas na tabela
                # Dessa forma, a tabela é formatada para que cada célula ocupe aproximadamente a metade da página,
                # com um espaço de 50 pontos a menos para margem ou espaçamento interno.
                complete_table = Table(product_rows, colWidths=[(CUSTOM_SIZE[0] / 2) - 50] * 2)

                complete_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Mantém alinhado verticalmente
                    ('LEFTPADDING', (1, 0), (1, 0), 20),  # Espaço entre imagem e texto
                    ('TOPPADDING', (0, 0), (-1, -1), 20),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Texto alinhado à esquerda
                ]))

                elements.append(complete_table)
                elements.append(PageBreak())
                product_rows = []  # Reinicia as linhas de produtos
                product_count = 0  # Reinicia o contador

    # Adiciona qualquer produto restante que não completou um bloco de 4
    if row:
        product_rows.append(row)

    if product_rows:
        table = Table(product_rows, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Mantém alinhado verticalmente
            ('LEFTPADDING', (1, 0), (1, 0), 20),  # Espaço entre imagem e texto
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Texto alinhado à esquerda
        ]))
        elements.append(table)

    # onFirstPage -> Define que a função draw_page_frame(canvas, doc) será chamada na primeira página do PDF para
    # desenhar algo (neste caso, as barras superior e inferior).

    # onLaterPages -> Define que a mesma função draw_page_frame(canvas, doc) será chamada em todas as
    # páginas subsequentes.

    # Gera o PDF chamando a função `draw_page_frame`
    doc.build(elements, onFirstPage=draw_page_frame_personalized, onLaterPages=draw_page_frame_personalized)


def draw_page_frame(canvas, doc):
    """Desenha as barras verdes no topo e na base de cada página."""

    # Caso seja uma página anterior a página 5, adiciona a imagem como Back Ground.
    if canvas.getPageNumber() <= 4:
        """
        Os dois valores 0, 0 representam as coordenadas X e Y onde a imagem será desenhada na página do PDF.

        Explicação:
            O sistema de coordenadas do ReportLab começa no canto inferior esquerdo da página, onde:
            X = 0 → Significa que a imagem começa na borda esquerda da página.
            Y = 0 → Significa que a imagem começa na borda inferior da página.

        Dessa forma, a imagem será desenhada a partir do canto inferior esquerdo da página e expandida até ocupar toda 
        a largura (width = A4[0]) e altura (height = A4[1]) da página.
        """
        canvas.drawImage(default_images[canvas.getPageNumber() - 1], 0, 0, width=CUSTOM_SIZE[0], height=CUSTOM_SIZE[1])

    # Desenha a página dinâmica apenas se for após a página 4.
    else:
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
        canvas.drawCentredString(width / 2, height - 42, "NOME DA EMPRESA")

        # # Texto inferior
        # canvas.drawCentredString(width / 2, 20, "")


def draw_page_frame_personalized(canvas, doc):
    """Desenha as barras verdes no topo e na base de cada página."""

    # Caso seja uma página anterior a página 5, adiciona a imagem como Back Ground.
    if canvas.getPageNumber() <= 4:
        """
        Os dois valores 0, 0 representam as coordenadas X e Y onde a imagem será desenhada na página do PDF.

        Explicação:
            O sistema de coordenadas do ReportLab começa no canto inferior esquerdo da página, onde:
            X = 0 → Significa que a imagem começa na borda esquerda da página.
            Y = 0 → Significa que a imagem começa na borda inferior da página.

        Dessa forma, a imagem será desenhada a partir do canto inferior esquerdo da página e expandida até ocupar toda 
        a largura (width = A4[0]) e altura (height = A4[1]) da página.
        """
        canvas.drawImage(default_images[canvas.getPageNumber() - 1], 0, 0, width=CUSTOM_SIZE[0], height=CUSTOM_SIZE[1])

    # Desenha a página dinâmica apenas se for após a página 4.
    else:
        width, height = CUSTOM_SIZE  # Obtém tamanho da página

        # Configura a cor verde
        canvas.setFillColorRGB(0.0, 0.47, 0.35)  # Verde escuro (RGB)

        # Desenha a barra superior
        canvas.rect(0,
                    height - 180,
                    width,
                    180,
                    fill=1,
                    stroke=0)

        # Desenha a barra inferior
        canvas.rect(0,
                    -2,
                    width,
                    180,
                    fill=1,
                    stroke=0)

        # Configura o texto dentro das barras
        canvas.setFillColorRGB(1, 1, 1)  # Cor branca para o texto
        canvas.setFont("Helvetica-Bold", 80)

        # Texto superior
        canvas.drawCentredString(width / 2, height - 120, "NOME DA EMPRESA")

        # # Texto inferior
        # canvas.drawCentredString(width / 2, 20, "")
