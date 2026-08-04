





from sentence_transformers import SentenceTransformer

import config


class EmbeddingModel:
    def __init__(self):
        print(f"[embedding] Loading {config.EMBEDDING_MODEL_NAME}...")
        self.model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)

    def encode(self, texts):

        return self.model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

    def encode_query(self, query):   #Convert a single query into an embedding vector
        return self.model.encode([query], normalize_embeddings=True)[0]
