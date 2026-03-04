from common import Common
from typing import Dict
import pandas as pd
from typing import Optional, Dict
from datetime import datetime, timedelta
import json
api = Common()



# lista_todos_pedidos = api.get_all_ongsys("pedidos")
# lista_pedidos = lista_todos_pedidos # Transformando em lista para o loop

# rows_pedido = []
# rows_detalhes = []
# rows_logs = []

# for pedido in lista_pedidos:
#     # 1. Tabela PEDIDO (Dados gerais)
#     # Removemos as listas internas para não sujar a tabela principal
#     info_pedido = pedido.copy()
#     itens = info_pedido.pop('itensPedido')
#     logs = info_pedido.pop('logs')
    
#     # "Achatar" dicionários internos (fornecedor e localEntrega)
#     info_pedido['fornecedor_nome'] = info_pedido['fornecedor'].get('nome')
#     info_pedido['cidade_entrega'] = info_pedido['localEntrega'].get('cidade')
#     # Remova os dicionários originais se quiser a planilha limpa
#     del info_pedido['fornecedor']
#     del info_pedido['localEntrega']
    
#     rows_pedido.append(info_pedido)

#     # 2. Tabela DETALHEPEDIDO
#     for item in itens:
#         item['idPedido'] = pedido['idPedido'] # Chave de ligação
#         rows_detalhes.append(item)

#     # 3. Tabela LOGSPEDIDO
#     for log in logs:
#         log['idPedido'] = pedido['idPedido'] # Chave de ligação
#         rows_logs.append(log)

# # Criar os DataFrames
# df_pedido = pd.DataFrame(rows_pedido)
# df_detalhes = pd.DataFrame(rows_detalhes)
# df_logs = pd.DataFrame(rows_logs)

# # Salvar em um arquivo Excel com 3 abas (planilhas)
# df_pedido.to_csv('pedido.csv', index=False, sep=';', encoding='utf-8-sig')
# df_detalhes.to_csv('detalhepedido.csv', index=False, sep=';', encoding='utf-8-sig')
# df_logs.to_csv('logspedido.csv', index=False, sep=';', encoding='utf-8-sig')

# print("Arquivos CSV gerados: pedido.csv, detalhepedido.csv e logspedido.csv")  



print("Iniciando busca paginada...")

todos_os_registros = []
inicio = 0
tamanho_pagina = 500
continuar = True

print("Coletando lista de nomes...")

while continuar:
    parametros = {
        "limit_start": inicio,
        "limit_page_length": tamanho_pagina,
        "fields": '["name"]'
    }

    resp_lista = api.erp_request("GET", "Stock Entry", params=parametros)
    dados_json = json.loads(resp_lista.text)
    lista_atual = dados_json.get("data", [])

    if not lista_atual:
        print(f"Busca finalizada. Total de nomes coletados: {len(todos_os_registros)}")
        break

    # --- O APPEND/EXTEND ACONTECE AQUI ---
    # Usamos extend para adicionar os itens da página atual na lista principal
    todos_os_registros.extend(lista_atual)
    
    print(f"Página processada: {inicio} até {inicio + len(lista_atual)}")

    inicio += tamanho_pagina


pedidos_rows = []
detalhes_rows = []

for registro in todos_os_registros:
    print(f"Processando registro: {registro['name']}")
    pedido = api.erp_request("GET", f"Stock Entry/{registro['name']}")
    dados_pedido = json.loads(pedido.text).get("data", {})
    ##converta para texto

    pedido_copy = dados_pedido.copy()
    items = pedido_copy.pop('items', [])
    pedido_copy.pop('additional_costs', None) # Remove campos de lista vazios
    pedidos_rows.append(pedido_copy)
    for item in items:
    # É boa prática manter o ID do pai para conseguir relacionar os CSVs depois
        item['parent_order_id'] = registro.get('name')
        detalhes_rows.append(item)

df_pedidos = pd.DataFrame(pedidos_rows)
df_detalhes = pd.DataFrame(detalhes_rows)

df_pedidos.to_csv('erp_pedidos.csv', index=False, encoding='utf-8-sig', sep=';')
df_detalhes.to_csv('erp_pedidosdetalhe.csv', index=False, encoding='utf-8-sig', sep=';')

print("Arquivos 'erp_pedidos.csv' e 'erp_pedidosdetalhe.csv' gerados com sucesso!")