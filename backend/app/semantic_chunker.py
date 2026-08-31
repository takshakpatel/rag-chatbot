from __future__ import annotations

import re
from langchain_core.documents import Document
from langchain_text_splitters import NLTKTextSplitter


def chunk_documents_semantic(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """Sentence-aware chunking using NLTK sentence tokenization.

    Unlike the recursive character splitter, this respects sentence boundaries.
    Chunks are built by accumulating sentences until the size limit is reached,
    then starting a new chunk with overlap from the last few sentences.
    """
    all_sentences: list[tuple[str, Document]] = []

    for doc in documents:
        sentences = re.split(r'(?<=[.!?])\s+', doc.page_content)
        for sent in sentences:
            sent = sent.strip()
            if sent:
                all_sentences.append((sent, doc))

    chunks: list[Document] = []
    current_sents: list[str] = []
    current_docs: list[Document] = []
    current_len = 0

    for sent, doc in all_sentences:
        sent_len = len(sent)

        if current_len + sent_len > chunk_size and current_sents:
            chunk_text = " ".join(current_sents)
            source = current_docs[0].metadata.get("source", "unknown")
            metadata = {
                "source": source,
                "filename": current_docs[0].metadata.get("filename", ""),
                "chunk_index": len(chunks),
                "strategy": "semantic",
            }
            chunks.append(Document(page_content=chunk_text, metadata=metadata))

            overlap_sents: list[str] = []
            overlap_len = 0
            for s in reversed(current_sents):
                if overlap_len + len(s) > chunk_overlap:
                    break
                overlap_sents.insert(0, s)
                overlap_len += len(s)

            current_sents = overlap_sents
            current_docs = [doc] * len(overlap_sents)
            current_len = overlap_len

        current_sents.append(sent)
        current_docs.append(doc)
        current_len += sent_len

    if current_sents:
        chunk_text = " ".join(current_sents)
        source = current_docs[0].metadata.get("source", "unknown")
        metadata = {
            "source": source,
            "filename": current_docs[0].metadata.get("filename", ""),
            "chunk_index": len(chunks),
            "strategy": "semantic",
        }
        chunks.append(Document(page_content=chunk_text, metadata=metadata))

    return chunks
