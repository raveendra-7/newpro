from sentence_transformers import SentenceTransformer
import chromadb


# =====================================================
# MODEL
# =====================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# =====================================================
# CHROMA DB
# =====================================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    "attacks"
)


# =====================================================
# SEMANTIC SEARCH
# =====================================================

def semantic_search(
    prompt,
    top_k=10
):

    query_embedding = model.encode(
        prompt,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k
    )

    distances = results["distances"][0]
    documents = results["documents"][0]

    similarities = [
        1 - distance
        for distance in distances
    ]

    top1_similarity = similarities[0]

    top3_similarity = (
        sum(similarities[:3])
        /
        min(3, len(similarities))
    )

    semantic_score = round(
        top3_similarity * 100,
        2
    )

    return {

        # Main score used by decision.py
        "semantic_score":
            semantic_score,

        # Closest attack vector
        "nearest_attack":
            documents[0],

        # Internal values for threshold tuning
        "top1_similarity":
            round(
                top1_similarity,
                4
            ),

        "top3_similarity":
            round(
                top3_similarity,
                4
            )
    }


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":

    while True:

        prompt = input(
            "\nPrompt: "
        ).strip()

        if prompt.lower() in [
            "exit",
            "quit"
        ]:
            break

        result = semantic_search(
            prompt
        )

        print(
            "\nSemantic Score:",
            result[
                "semantic_score"
            ]
        )

        print(
            "\nClosest Attack:"
        )

        print(
            result[
                "nearest_attack"
            ]
        )