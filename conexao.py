import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

cliente = MongoClient(os.getenv("MONGO_URI"))

try:
    cliente.admin.command("ping")
    print("MongoDB conectado com sucesso!")

    banco = cliente["shop_analytics"]
    colecao = banco["clientes"]

    print("Coleções disponíveis:", banco.list_collection_names())
    print("Quantidade de clientes:", colecao.count_documents({}))

    print("\nClientes cadastrados:")
    for pessoa in colecao.find():
        print(pessoa)

except PyMongoError as erro:
    print("\nERRO NA CONEXÃO:")
    print(erro)

finally:
    cliente.close()