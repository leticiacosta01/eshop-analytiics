import streamlit as st
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd

st.set_page_config(
    page_title="eShop Analytics",
    page_icon="🛒​",
    layout="wide"
)

st.title("🛒​ eShop Brasil")
st.subheader("Sistema de Gestão e Análise de Dados")

st.write("Bem-vindo ao painel de gerenciamentoe análise de dados !")

st.divider()

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

try:
    cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    banco = cliente["shop_analytics"]

    banco.command("ping")

    st.success("MongoDB conectado com sucesso!")

    st.subheader("Dados cadastrados")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Clientes", banco["clientes"].count_documents({}))

    with col2:
        st.metric("Pedidos", banco["pedidos"].count_documents({}))

    with col3:
        st.metric("Produtos", banco["produtos"].count_documents({}))

except Exception as erro:
    st.error(f"Erro na conexão com MongoDB: {erro}")

st.divider()

st.subheader("📊​ consultar dados do sistema")

opcao = st.selectbox(
    "Escolha os dados que deseja visualizar:",
    ["Clientes", "Pedidos", "Produtos"]
)
colecoes = {
    "Clientes": "clientes",
    "Pedidos": "pedidos",
    "Produtos": "produtos"
}

documentos = list(
    banco[colecoes[opcao]].find().limit(100)
)

if documentos:
    df = pd.DataFrame(documentos)
    df["_id"] = df["_id"].astype(str)

    if opcao == "Clientes" and "nome" in df.columns:
        df["nome"] = [f"Cliente {i+1}" for i in range(len(df))]

    if "email" in df.columns:
        df["email"] = "Protegido"

    if "cliente_nome" in df.columns:
        df["cliente_nome"] = "Cliente identificado"

    st.dataframe(df, use_container_width=True)

else:
    st.warning("Nenhum registro encontrado.")

st.divider()

st.subheader("➕​ Cadastrar novo produto")

with st.form("form_produto"):

    nome = st.text_input("Nome do produto")

    categoria = st.text_input("Categoria")

    preco = st.number_input(
        "Preço (R$)", min_value=0.0, step=10.0
    )

    estoque = st.number_input(
        "Estoque", min_value=0, step=1
    )

    quantidade_vendida = st.number_input(
        "Quantidade vendida", min_value=0, step=1
    )

    cadastrar = st.form_submit_button("Cadastrar produto")

if cadastrar:
    if nome.strip() and categoria.strip():

        try:
            banco["produtos"].insert_one({
                "nome": nome,
                "categoria": categoria,
                "preco": preco,
                "estoque": estoque,
                "quantidade_vendida": quantidade_vendida
            })

            st.success("Produto cadastrado com sucesso!")
            st.rerun()

        except Exception as erro:
            st.error(f"Erro ao cadastrar produto: {erro}")

    else:
        st.warning("Preencha o nome a categoria.")

st.divider()

st.subheader("✏️ Editar produto")

produtos_edicao = list(banco["produtos"].find())

if produtos_edicao:

    produto_selecionado = st.selectbox(
        "Escolha o produto que deseja editar:",
        produtos_edicao,
        format_func=lambda p: p.get("nome", "Produto sem nome")
    )

    with st.form("form_editar_produto"):

        novo_nome = st.text_input(
            "Nome do produto",
            value=produto_selecionado.get("nome", "")
        )

        nova_categoria = st.text_input(
            "Categoria",
            value=produto_selecionado.get("categoria", "")
        )

        novo_preco = st.number_input(
            "Preço (R$)",
            min_value=0.0,
            value=float(produto_selecionado.get("preco", 0)),
            step=10.0
        )

        novo_estoque = st.number_input(
            "Estoque",
            min_value=0,
            value=int(produto_selecionado.get("estoque", 0)),
            step=1
        )

        nova_quantidade = st.number_input(
            "Quantidade vendida",
            min_value=0,
            value=int(produto_selecionado.get("quantidade_vendida", 0)),
            step=1
        )

        editar = st.form_submit_button("Salvar alterações")

        if editar:
            banco["produtos"].update_one(
                {"_id": produto_selecionado["_id"]},
                {"$set": {
                    "nome": novo_nome,
                    "categoria": nova_categoria,
                    "preco": novo_preco,
                    "estoque": novo_estoque,
                    "quantidade_vendida": nova_quantidade
                }}
            )

            st.success("Produto atualizado com sucesso!")
            st.rerun()

else:
    st.warning("Não existem produtos para editar.")

st.divider()

st.subheader("🗑️ Excluir produto")

produtos_exclusao = list(banco["produtos"].find())

if produtos_exclusao:

    produto_excluir = st.selectbox(
        "Escolha o produto que deseja excluir:",
        produtos_exclusao,
        format_func=lambda p: p.get("nome", "Produto sem nome"),
        key="produto_excluir"
    )

    confirmar = st.checkbox(
        "Confirmo que desejo excluir este produto."
    )

    if st.button("Excluir produto"):
        if confirmar:
            banco["produtos"].delete_one(
                {"_id": produto_excluir["_id"]}
            )

            st.success("Produto excluído com sucesso!")
            st.rerun()
        else:
            st.warning("Marque a confirmação antes de excluir.")

else:
    st.warning("Não existem produtos para excluir.")

st.divider()

st.subheader("🔗 Integração de pedidos e produtos")

pedidos = list(banco["pedidos"].find())
produtos = list(banco["produtos"].find())

if pedidos and produtos:

    df_pedidos = pd.DataFrame(pedidos)
    df_produtos = pd.DataFrame(produtos)

    df_integrado = pd.merge(
        df_pedidos,
        df_produtos,
        left_on="produto",
        right_on="nome",
        how="left",
        suffixes=("_pedido", "_produto")
    )

    colunas = [
        "produto",
        "categoria",
        "quantidade",
        "valor_total",
        "estoque"
    ]

    df_integrado = df_integrado[
        [c for c in colunas if c in df_integrado.columns]
    ]

    st.dataframe(df_integrado, use_container_width=True)

else:
    st.warning("Não existem dados suficientes para a integração.")

st.divider()

st.subheader("🚚 Análise logística por cidade")

if "cidade_entrega" in df_pedidos.columns:

    pedidos_por_cidade = (
        df_pedidos["cidade_entrega"]
        .value_counts()
        .reset_index()
    )

    pedidos_por_cidade.columns = [
        "Cidade",
        "Quantidade de pedidos"
    ]

    st.bar_chart(
        pedidos_por_cidade,
        x="Cidade",
        y="Quantidade de pedidos"
    )

else:
    st.warning("Coluna de cidade de entrega não encontrada.")

st.divider()

st.subheader("📦 Acompanhamento dos pedidos")

pedidos_status = list(banco["pedidos"].find())

if pedidos_status:

    df_status = pd.DataFrame(pedidos_status)

    pedidos_por_status = (
        df_status["status"]
        .value_counts()
        .reset_index()
    )

    pedidos_por_status.columns = [
        "Status",
        "Quantidade"
    ]

    st.bar_chart(
        pedidos_por_status,
        x="Status",
        y="Quantidade"
    )

else:
    st.warning("Nenhum pedido encontrado.")