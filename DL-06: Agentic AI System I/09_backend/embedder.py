### embedder.py - load the embedding model (sentence-transformers, PyTorch) once
### used by 05 (vector search) and 03/04 (local classifiers)

import torch
import config

_model = None


def get_device():
    if config.LOCAL_MODEL_DEVICE == "cuda" and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def get_model():
    ### load on first use; on failure raise so the caller can degrade
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        ### force .safetensors (torch < 2.6 can't load .bin)
        _model = SentenceTransformer(config.EMBEDDING_MODEL, device=get_device(),
                                     model_kwargs={"use_safetensors": True})
    return _model


def encode(texts):
    ### returns normalized [n_texts, dim] tensor (cosine = dot product)
    model = get_model()
    with torch.no_grad():
        vectors = model.encode(texts, convert_to_tensor=True, normalize_embeddings=True,
                               batch_size=16, show_progress_bar=False)
    return vectors.float().cpu()
