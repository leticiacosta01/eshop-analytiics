from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("A conexão com MongoDB não foi configurada!")

cliente = MongoClient(MONGO_URI)

banco = cliente["shop_analytics"]

colecao = banco["clientes"]

pedidos = banco["pedidos"]

produtos = banco["produtos"]

dados = list(colecao.find())
df = pd.DataFrame(dados)
dados_pedidos = list(pedidos.find())
df_pedidos = pd.DataFrame(dados_pedidos)
dados_produtos = list(produtos.find())
df_produtos = pd.DataFrame(dados_produtos)

print("\nTABELA DE PRODUTOS:")
print(df_produtos)

print("\nANÁLISE DE ESTOQUE:")
produtos_baixo_estoque = df_produtos[df_produtos["estoque"] < 15]
print("\nProdutos com estoque baixo:")
print(produtos_baixo_estoque[["nome", "estoque", "quantidade_vendida"]])

print("\nRANKING DE PRODUTOS MAIS VENDIDOS:")
ranking_produtos = df_produtos.sort_values(
    by="quantidade_vendida",
    ascending=False
)
print(ranking_produtos[["nome", "quantidade_vendida"]])

print("\nVALOR ESTIMADO DAS VENDAS POR PRODUTO:")
df_produtos["valor_vendido"] = (
    df_produtos["preco"] * df_produtos["quantidade_vendida"]
)
print(
    df_produtos[["nome", "valor_vendido"]]
)
print("\nRECOMENDAÇÃO DE PRODUTOS:")
produto_recomendado = ranking_produtos.iloc[0]
print("Produto recomendado:", produto_recomendado["nome"])
print("Quantidade vendida:", produto_recomendado["quantidade_vendida"])
print("\nCOLUNAS DOS PEDIDOS:")
print(df_pedidos.columns.tolist())

print("\nNOMES EXATOS")
print([repr(coluna)for coluna in df_pedidos.columns])

df_pedidos_relatorio = df_pedidos.copy()

mapa_clientes = {
    nome: f"Cliente {i+1}"
    for i, nome in enumerate(df_pedidos["cliente_nome"].dropna().unique())
}
df_pedidos_relatorio["cliente_nome"] = (
    df_pedidos_relatorio["cliente_nome"]
    .map(mapa_clientes)
    .fillna("Cliente não identificado")
)

print("\nTabela de pedidos com idenificação protegida:")
print(df_pedidos_relatorio)

faturamento = df_pedidos["valor_total"].sum()
print("\nFaturamento total:", faturamento)

print("\nPedidos por status:")
print(df_pedidos["status"].value_counts())

print("\nQuantidade vendida por produto:")
print(df_pedidos.groupby("produto")["quantidade"].sum())

print("\nFaturamento por cidade:")
faturamento_cidade = df_pedidos.groupby("cidade_entrega")["valor_total"].sum()
print(faturamento_cidade.sort_values(ascending=False))

print("\nFaturamento por forma de pagamento:")
faturamento_pagamento = df_pedidos.groupby("forma_pagamento")["valor_total"].sum()
print(faturamento_pagamento)

print("\nQuantidade de pedidos por forma de pagamento:")
print(df_pedidos["forma_pagamento"].value_counts())

print("\nTicket médio dos pedidos:")
ticket_medio = df_pedidos["valor_total"].mean()
print("R$", round(ticket_medio, 2))

print("\nFaturamento por produto:")
faturamento_produto = df_pedidos.groupby("produto")["valor_total"].sum()
print(faturamento_produto.sort_values(ascending=False))

print("\nTabela de clientes:")
df_clientes_privacidade = df.copy()

df_clientes_privacidade["nome"] = [
    f"Cliente {i+1}" for i in range(len(df_clientes_privacidade))
]
df_clientes_privacidade["email"] = "Protegido"

print(df_clientes_privacidade)

media_pedidos = df["pedidos_realizados"].mean()
print("\nMédia de pedidos por cliente:", media_pedidos)
print("Conexão realizada com sucesso!")

clientes_ativos = df["ativo"].sum()

print("\nQuantidade de clientes ativos:", clientes_ativos)

clientes_frequentes = df[df["pedidos_realizados"] > 5].copy()

clientes_frequentes["nome"] = [
    f"Cliente {i+1}"
    for i in range(len(clientes_frequentes))
]
print("\nClientes frequentes com identificação protegida:")
print(clientes_frequentes[["nome", "pedidos_realizados"]])

print("Total de clientes frequentes:", len(clientes_frequentes))

print("\nQuantidades de clientes por cidade:")

print(df["cidade"].value_counts())

total_pedidos = df["pedidos_realizados"].sum()
print("\nTotal de pedidos realizados:", total_pedidos)

maior_cliente = df.loc[df["pedidos_realizados"].idxmax()]

print("\n========== RELATÓRIO SHOP ANALYTICS ==========")

print("Total de clientes:", len(df))
print("Clientes ativos:", clientes_ativos)
print("Total de pedidos:", total_pedidos)
print("Média de pedidos:", round(media_pedidos, 2))

print("Maior comprador: Cliente identificado")
print("Pedidos do maior comprador:",
       maior_cliente["pedidos_realizados"]
)


print("===============================================")

print("\nCliente com mais pedidos:")
print(maior_cliente["nome"])
print("Pedidos realizados:", maior_cliente["pedidos_realizados"])

print("\nCOLUNAS DOS PEDIDOS:")
print(df_pedidos.columns.tolist())

print("\nNOMES EXATOS DAS COLUNAS:")
print([repr(coluna)for coluna in df_pedidos.columns])

try:
    banco.command("ping")
    print("MongoDB conectado com sucesso!")

    print("Quantidade de clientes:", colecao.count_documents({}))

except PyMongoError as erro:
    print("Erro na conexão:", erro)

finally:
    cliente.close()


#gráfico de pedidos por status
pedidos_status = df_pedidos["status"].value_counts()

plt.figure(figsize=(8, 5))

pedidos_status.plot(kind="bar")

plt.title("Quantidade de Pedidos por Status")
plt.xlabel("Status dos Pedidos")
plt.ylabel("Quantidade")

plt.xticks(rotation=0)

plt.tight_layout()
plt.show()


#GRAFICO DE FATURAMENTO POR PRODUTO

faturamento_produto = df_pedidos.groupby("produto")["valor_total"].sum()

plt.figure(figsize=(8, 5))

faturamento_produto.plot(kind="bar", color="green")

plt.title("Faturamento Por Produto")
plt.xlabel("Produtos")
plt.ylabel("Faturamento (R$)")

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()


#GRAFICO DE FATURAMENTO POR CIDADE

faturamento_cidade = df_pedidos.groupby("cidade_entrega")["valor_total"].sum()

plt.figure(figsize=(8, 5))

faturamento_cidade.plot(kind="bar", color="orange")

plt.title("Faturamento Por Cidade")
plt.xlabel("Cidades")
plt.ylabel("Faturamento (R$)")

plt.xticks(rotation=0)
plt.tight_layout()

plt.show()


#GRAFICO DE FATURAMENTO POR FORMA DE PAGAMENTO

faturamento_pagamento = df_pedidos.groupby("forma_pagamento")["valor_total"].sum()

plt.figure(figsize=(8, 5))

faturamento_pagamento.plot(kind="bar", color="purple")

plt.title("Faturamento Por Forma de Pagamento")
plt.xlabel("Forma de Pagamento")
plt.ylabel("Faturamento (R$)")

plt.xticks(rotation=0)

plt.tight_layout()
plt.show()


#GRAFICO DE QUANTIDADE DE PEDIDOS POR PAGAMENTO

quantidade_pagamento = df_pedidos["forma_pagamento"].value_counts()

plt.figure(figsize=(8, 5))

quantidade_pagamento.plot(kind="bar", color="skyblue")

plt.title("Quantidade de Pedidos Por Forma de Pagamento")
plt.xlabel("Forma de Pagamento")
plt.ylabel("Quantidade de Pedidos")

plt.xticks(rotation=0)

plt.tight_layout()
plt.show()


#DASHBOARD SHOP ANALYTICS

fig, axs = plt.subplots(2, 3, figsize=(16, 10))

fig.suptitle(
    "SHOP ANALYTICS - DASHBOARD",
    fontsize=20,
    fontweight="bold"
)
faturamento_total = df_pedidos["valor_total"].sum()
ticket_medio = df_pedidos["valor_total"].mean()

fig.text(
    0.25, 0.92,
    f"Faturamento Total: R$ {faturamento_total:2f}",
    ha="center",
    fontsize=13
)

fig.text(
    0.70, 0.92,
    f"Ticket Médio: R$ {ticket_medio:.2f}",
    ha="center",
    fontsize=13
)

#1 - Pedidos por status
df_pedidos["status"].value_counts().plot(
    kind="bar", ax=axs[0, 0]
)
axs[0, 0].set_title("Pedidos por Status")

#2 - Faturamento por produto
df_pedidos.groupby("produto")["valor_total"].sum().plot(
    kind="bar", ax=axs[0, 1]
)
axs[0, 1].set_title("Faturamento por Produto")

#3 - Faturamento por cidade
df_pedidos.groupby("cidade_entrega")["valor_total"].sum().plot(
    kind="bar", ax=axs[0, 2]
)
axs[0, 2].set_title("Faturamento por Cidade")

#4 - Faturamento por pagamento
df_pedidos.groupby("forma_pagamento")["valor_total"].sum().plot(
    kind="bar", ax=axs[1, 0]
)
axs[1, 0].set_title("Faturamento por Pagamento")

#5 - Quantidade por pagamento
df_pedidos["forma_pagamento"].value_counts().plot(
    kind="bar", ax=axs[1, 1]
)
axs[1, 1].set_title("Pedidos por Pagamentos")

axs[1, 2].axis("off")

fig.suptitle("SHOP ANALYTICS - DASHBOARD", fontsize=18)

plt.tight_layout()
plt.savefig("dashboard_shop_analytics.png", dpi=300, bbox_inches="tight")
plt.show()

print("\nRECOMENDAÇÕES PERSONALIZADAS:")

compras_clientes = df_pedidos.groupby(
    "cliente_nome"
)["produto"].apply(list)

for i, (cliente_nome, comprados) in enumerate(compras_clientes.items()):

    opcoes = ranking_produtos[
        ~ranking_produtos["nome"].isin(comprados)
    ]

    if not opcoes.empty:
        sugestao = opcoes.iloc[0]["nome"]

        print(f"Cliente {i+1}: recomendamos {sugestao}")

    else:
        print(f"Cliente{i+1}: já comprou todos os produtos.")


print("\nANÁLISE LOGÍSTICA POR CIDADE:")

logistica = pd.crosstab(
    df_pedidos["cidade_entrega"],
    df_pedidos["status"]
)
print(logistica)

print("\nTOTAL DE PEDIDOS POR CIDADE:")

pedidos_por_cidade = df_pedidos["cidade_entrega"].value_counts()
print(pedidos_por_cidade)

print("\nPEDIDOS QUE PRECISAM DE ATENÇÃO:")

pedidos_pendentes = df_pedidos[
    df_pedidos["status"] != "Entregue"
]
print("Total de pedidos não entregues:", len(pedidos_pendentes))
print(pedidos_pendentes[["cliente_nome", "produto", "status", "cidade_entrega"]])

print("\nPERCENTUAL DE PEDIDOS ENTREGUES:")

total = len(df_pedidos)

entregues = len(df_pedidos[
    df_pedidos["status"] == "Entregue"
])
percentual = (entregues / total) * 100
print(f"Pedidos entregues: {percentual:.2f}%")

print("\n VALOR TOTAL DOS PEDIDOS PENDENTES")
valor_pendente = pedidos_pendentes["valor_total"].sum()
print(f"R$ {valor_pendente:.2f}")

print("\nCIDADE COM MAIS PEDIDOS PENDENTES:")

pendentes_por_cidade = pedidos_pendentes["cidade_entrega"].value_counts()
print(pendentes_por_cidade)

if not pendentes_por_cidade.empty:
    print("Cidade que precisa de atenção:", pendentes_por_cidade.idxmax())

print("\n========== SEGURANÇA E PRIVACIDADE ==========")

clientes_anonimos = {
    nome: f"cliente {i+1}"
    for i, nome in enumerate(df_pedidos["cliente_nome"].dropna().unique())
}
df_pedidos_privacidade = df_pedidos.copy()

df_pedidos_privacidade["cliente_nome"] = (
    df_pedidos_privacidade["cliente_nome"]
    .map(clientes_anonimos)
    .fillna("Cliente não identificado")
)

print("\nPedidos com identificação protegida:")

print(
    df_pedidos_privacidade[
        ["cliente_nome", "produto", "valor_total"]
    ]
)