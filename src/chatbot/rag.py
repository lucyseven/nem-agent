import os
import openai
import docx
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer

class RAGPipeline:
    """
    A minimal RAG pipeline that:
      1) Loads and chunks .docx files.
      2) Embeds them locally using SentenceTransformers.
      3) Stores the chunks and their embeddings in memory.
      4) Retrieves the top-k relevant chunks for a query.
      5) Uses OpenAI's API for final answer generation.
    """

    def __init__(self,
                 doc_paths: List[str],
                 chunk_size: int = 300,
                 overlap: int = 50,
                 openai_model_name: str = "gpt-3.5-turbo",
                 local_model_name: str = "all-MiniLM-L6-v2"):
        """
        :param doc_paths: List of file paths to .docx files.
        :param chunk_size: Number of words per chunk.
        :param overlap: Overlap in words between chunks.
        :param openai_model_name: Model used for final answer generation.
        :param local_model_name: SentenceTransformers model for local embeddings.
        """
        self.doc_paths = doc_paths
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.openai_model_name = openai_model_name
        self.local_model_name = local_model_name

        # Load local embedding model
        self.embedder = SentenceTransformer(self.local_model_name)

        # Storage for (chunk_text, embedding_vector)
        self.docstore = []
        self._prepare_docs()

    def _prepare_docs(self):
        """Load, chunk, and embed documents, then store them in self.docstore."""
        all_texts = []
        for path in self.doc_paths:
            text = self._load_docx(path)
            chunks = self._chunk_text(text)
            all_texts.extend(chunks)
        embeddings = self._embed_texts(all_texts)
        self.docstore = list(zip(all_texts, embeddings))

    def _load_docx(self, path: str) -> str:
        """Load text from a .docx file."""
        doc = docx.Document(path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())
        return "\n".join(full_text)

    def _chunk_text(self, text: str) -> List[str]:
        """Simple word-based chunking of the input text."""
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            chunks.append(chunk_text)
            start += self.chunk_size - self.overlap
        return chunks

    def _embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """Embed a list of text chunks using the local SentenceTransformers model."""
        vectors = self.embedder.encode(texts, convert_to_numpy=True)
        return [v for v in vectors]

    def _embed_query(self, query: str) -> np.ndarray:
        """Convert the user query to an embedding vector locally."""
        return self.embedder.encode([query], convert_to_numpy=True)[0]

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve the top_k most similar text chunks to the user query.
        """
        query_emb = self._embed_query(query)
        similarities = []
        for chunk_text, chunk_emb in self.docstore:
            score = self._cosine_sim(query_emb, chunk_emb)
            similarities.append((score, chunk_text))
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [txt for _, txt in similarities[:top_k]]
        return top_chunks

    def generate_answer(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve top_k chunks and build a prompt using the retrieved context plus the user query.
        Then call OpenAI's API to generate the final answer.
        """
        relevant_chunks = self.retrieve(query, top_k=top_k)
        context = "\n\n".join(relevant_chunks)

        system_prompt = (
            "You are an expert on Net Energy Metering (NEM). "
            "Using the context provided below, answer the user's question in a clear and concise manner. "
            "Use different wording if asked the same question again."
            "If the context does not contain enough information, please indicate that further information may be needed.\n\n"
            f"Context:\n{context}"
        )
        user_prompt = f"User question: {query}"

        completion = openai.ChatCompletion.create(
            model=self.openai_model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            presence_penalty=0.5,
            frequency_penalty=0.5
        )
        answer = completion["choices"][0]["message"]["content"]
        return answer

    @staticmethod
    def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# Global pipeline instance (lazy initialization)
pipeline = None

def init_pipeline():
    """
    Initialize the RAG pipeline with all document paths.
    """
    global pipeline
    if pipeline is None:
        doc_paths = [
            "data/faq/top20q.docx",
            "data/nem_documents/nem_policy.docx",
            "data/website_scraped_data/web_info.docx"
        ]
        pipeline = RAGPipeline(
            doc_paths=doc_paths,
            chunk_size=300,
            overlap=50,
            openai_model_name="gpt-3.5-turbo",
            local_model_name="all-MiniLM-L6-v2"
        )

def get_response(user_input: str) -> str:
    """
    Streamlit-facing function that:
      1) Initializes the pipeline if not already done.
      2) Uses the pipeline to generate an answer for the given user input (or conversation history).
    """
    init_pipeline()
    return pipeline.generate_answer(user_input, top_k=3)
