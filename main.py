from teste import informations
from datetime import datetime
from functions.pdf_functions.pdf_functions import generate_pdf_a4

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

generate_pdf_a4(informations, 'tabela_de_produtos_real.pdf')

tempo_final = datetime.now()

print(f'Tempo percorrido: {tempo_final - tempo_inicial}')
