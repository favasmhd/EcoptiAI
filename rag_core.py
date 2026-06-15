import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =====================================
# LOAD DATA
# =====================================
with open("products_demo.json", "r") as f:
    products = json.load(f)

if not products:
    raise ValueError("Product data is empty")

# =====================================
# EMBEDDING MODEL
# =====================================
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

product_texts = [
    f"{p['product_name']}. {p['description']}"
    for p in products
]

# Precompute embeddings
product_embeddings = np.array(
    embedding_model.encode(product_texts, convert_to_numpy=True)
)

# Normalize embeddings (good practice)
product_embeddings = product_embeddings / np.linalg.norm(
    product_embeddings, axis=1, keepdims=True
)

# =====================================
# RETRIEVAL FUNCTION
# =====================================
def retrieve_similar_products(query: str, top_k: int = 3):
    if not query.strip():
        return []

    query_embedding = embedding_model.encode(
        query, convert_to_numpy=True
    )
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    similarities = cosine_similarity(
        [query_embedding], product_embeddings
    )[0]

    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        product = products[idx]

        results.append({
            "handle": product.get("handle"),  # real identifier
            "product_name": product.get("product_name", ""),
            "description": product.get("description", ""),
            "similarity_score": float(similarities[idx])
        })


    return results

