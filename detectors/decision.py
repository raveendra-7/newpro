import re
import chromadb
from sentence_transformers import SentenceTransformer

print("[INFO] Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("[INFO] Connecting to ChromaDB...")
client = chromadb.PersistentClient(path="./chroma_db")

try:
    attacks_collection = client.get_collection("attacks")
    attack_count = attacks_collection.count()
    print(f"[INFO] Loaded attacks collection with {attack_count} vectors")
except Exception as e:
    print(f"[WARNING] Could not load attacks collection: {e}")
    attacks_collection = None

ATTACK_PATTERNS = [
    r"ignore.*previous.*instruction",
    r"forget.*everything",
    r"system.*prompt",
    r"you.*are.*now",
    r"new.*instruction",
    r"bypass",
    r"override",
    r"hack",
    r"jailbreak",
    r"do.*not.*follow",
    r"disregard.*instruction",
]


def evaluate_prompt(prompt: str) -> dict:
    """
    Evaluate a prompt for potential injection attacks.
    Uses 2 methods: Regex patterns + Semantic similarity via ChromaDB.
    """
    
    regex_matches = []
    for pattern in ATTACK_PATTERNS:
        if re.search(pattern, prompt.lower()):
            regex_matches.append(pattern)
    
    regex_score = len(regex_matches) / len(ATTACK_PATTERNS)
    
    avg_distance = 0
    min_distance = 1.0
    nearest_attack = None
    top_distances = []
    
    if attacks_collection is not None:
        try:
            embedding = model.encode(prompt, normalize_embeddings=True)
            
            results = attacks_collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=5
            )
            
            if results and results["distances"] and len(results["distances"]) > 0:
                distances = results["distances"][0]
                top_distances = [float(d) for d in distances]
                
                similarities = [1 - d for d in distances]
                avg_distance = sum(similarities) / len(similarities) if similarities else 0
                min_distance = min(similarities) if similarities else 1.0
                
                if results["documents"] and len(results["documents"]) > 0:
                    docs = results["documents"][0]
                    nearest_attack = docs[0] if docs else None
        except Exception as e:
            print(f"[ERROR] ChromaDB query error: {e}")
    
    risk_score = (regex_score * 0.3) + (min_distance * 0.7)
    blocked = risk_score > 0.5 or min_distance > 0.7
    
    return {
        "blocked": blocked,
        "risk_score": round(risk_score, 3),
        "avg_distance": round(avg_distance, 3),
        "min_distance": round(min_distance, 3),
        "regex_score": round(regex_score, 3),
        "regex_matches": regex_matches,
        "nearest_attack": nearest_attack,
        "top_distances": top_distances,
        "decision": "BLOCKED" if blocked else "ALLOWED"
    }
