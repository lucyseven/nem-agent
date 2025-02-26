import faiss
import numpy as np
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

class VectorSearch:
    def __init__(self):
        self.embeddings_model = OpenAIEmbeddings()
        self.vector_db = None

    def create_vector_store(self, docs):
        """Create FAISS vector store from NEM documents"""
        embeddings = self.embeddings_model.embed_documents(docs)
        index = faiss.IndexFlatL2(len(embeddings[0]))
        index.add(np.array(embeddings, dtype=np.float32))
        self.vector_db = index

    def search(self, query, k=3):
        """Retrieve top-k relevant documents"""
        query_embedding = self.embeddings_model.embed_query(query)
        distances, indices = self.vector_db.search(np.array([query_embedding]), k)
        return indices[0]  # Return indices of relevant documents
