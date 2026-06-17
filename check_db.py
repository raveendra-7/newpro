import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

attacks = client.get_collection("attacks")
benign = client.get_collection("benign")

print("Attacks:", attacks.count())
print("Benign :", benign.count())