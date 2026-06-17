from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import chromadb

print("Loading model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="./chroma_db"
)

attack_collection = client.get_or_create_collection(
    name="attacks",
    metadata={
        "hnsw:space": "cosine"
    }
)

seen_prompts = set()

MAX_MICROSOFT = 1000
MAX_NEURAL = 2600
MAX_HACK = 10000


def is_duplicate(prompt):

    normalized = " ".join(
        prompt.lower().split()
    )

    if normalized in seen_prompts:
        return True

    seen_prompts.add(normalized)

    return False


# =====================================================
# MICROSOFT
# =====================================================

print("\nLoading Microsoft dataset...")

dataset = load_dataset(
    "microsoft/llmail-inject-challenge"
)

phase1 = dataset["Phase1"]

microsoft_count = 0

for row in phase1:

    if microsoft_count >= MAX_MICROSOFT:
        break

    prompt = row["body"]

    if not prompt:
        continue

    if is_duplicate(prompt):
        continue

    embedding = model.encode(
        prompt,
        normalize_embeddings=True
    ).tolist()

    attack_collection.add(
        ids=[f"ms_{microsoft_count}"],
        documents=[prompt],
        embeddings=[embedding],
        metadatas=[{
            "source": "microsoft"
        }]
    )

    microsoft_count += 1

    if microsoft_count % 100 == 0:
        print(
            f"Microsoft: {microsoft_count}"
        )

# =====================================================
# NEURALCHEMY
# =====================================================

print("\nLoading Neuralchemy dataset...")

dataset = load_dataset(
    "neuralchemy/Prompt-injection-dataset",
    "core"
)

train = dataset["train"]

neural_count = 0

for row in train:

    if neural_count >= MAX_NEURAL:
        break

    if row["label"] != 1:
        continue

    prompt = row["text"]

    if not prompt:
        continue

    if is_duplicate(prompt):
        continue

    embedding = model.encode(
        prompt,
        normalize_embeddings=True
    ).tolist()

    attack_collection.add(
        ids=[f"neural_{neural_count}"],
        documents=[prompt],
        embeddings=[embedding],
        metadatas=[{
            "source": "neuralchemy",
            "category": row["category"],
            "severity": row["severity"]
        }]
    )

    neural_count += 1

    if neural_count % 100 == 0:
        print(
            f"Neuralchemy: {neural_count}"
        )

# =====================================================
# HACKAPROMPT
# =====================================================

print("\nLoading HackAPrompt dataset...")

dataset = load_dataset(
    "hackaprompt/hackaprompt-dataset"
)

train = dataset["train"]

hack_count = 0

for row in train:

    if hack_count >= MAX_HACK:
        break

    prompt = row["prompt"]

    if not prompt:
        continue

    if is_duplicate(prompt):
        continue

    embedding = model.encode(
        prompt,
        normalize_embeddings=True
    ).tolist()

    attack_collection.add(
        ids=[f"hack_{hack_count}"],
        documents=[prompt],
        embeddings=[embedding],
        metadatas=[{
            "source": "hackaprompt",
            "level": row["level"],
            "score": row["score"]
        }]
    )

    hack_count += 1

    if hack_count % 100 == 0:
        print(
            f"HackAPrompt: {hack_count}"
        )

# =====================================================
# SUMMARY
# =====================================================

print()
print("Population complete")
print()

print(
    "Microsoft attacks:",
    microsoft_count
)

print(
    "Neuralchemy attacks:",
    neural_count
)

print(
    "HackAPrompt attacks:",
    hack_count
)

print()

print(
    "Unique prompts:",
    len(seen_prompts)
)

print()

print(
    "Total attack vectors:",
    attack_collection.count()
)