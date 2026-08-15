"""
rag_node — embeds the transcript and retrieves the top-K most similar
chunks from kb_documents using pgvector cosine similarity.
"""
import os
import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI
from agents.state import BankState

_openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_DATABASE_URL = os.environ["DATABASE_URL"]

TOP_K = 5
SIMILARITY_THRESHOLD = 0.30


def _embed(text: str) -> list[float]:
    return _openai.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    ).data[0].embedding


def rag_node(state: BankState) -> BankState:
    embedding = _embed(state["transcript"])

    conn = psycopg2.connect(_DATABASE_URL, connect_timeout=10)
    register_vector(conn)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT title, category, content,
               1 - (embedding <=> %s::vector) AS similarity
        FROM kb_documents
        WHERE 1 - (embedding <=> %s::vector) > %s
        ORDER BY similarity DESC
        LIMIT %s;
        """,
        (embedding, embedding, SIMILARITY_THRESHOLD, TOP_K),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    chunks = [
        {"title": r[0], "category": r[1], "content": r[2], "similarity": round(float(r[3]), 4)}
        for r in rows
    ]
    return {**state, "retrieved_chunks": chunks}
