"""
Phase 1 — Retrieval Verification
Uses psycopg2 + pgvector directly. Runs 4 test queries and prints top-3 results.
Run: python test_retrieval.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
DATABASE_URL = os.environ["DATABASE_URL"]

TEST_QUERIES = [
    "What is the FD interest rate for 1 year?",
    "Should I put my savings in an equity mutual fund?",
    "What documents do I need for a home loan?",
    "What is the AML reporting threshold?",
]


def embed(text: str) -> list[float]:
    return openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    ).data[0].embedding


def test_retrieval():
    print("=== Phase 1 Retrieval Test ===\n")

    conn = psycopg2.connect(DATABASE_URL, connect_timeout=15)
    register_vector(conn)
    cur = conn.cursor()

    for query in TEST_QUERIES:
        print(f'Query: "{query}"')
        embedding = embed(query)

        cur.execute(
            """
            SELECT title, category,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM kb_documents
            WHERE 1 - (embedding <=> %s::vector) > 0.3
            ORDER BY similarity DESC
            LIMIT 3;
            """,
            (embedding, embedding),
        )
        rows = cur.fetchall()

        if not rows:
            print("  [NO RESULTS] — check seeding and threshold\n")
        else:
            for rank, (title, category, similarity) in enumerate(rows, 1):
                print(f"  [{rank}] ({category}) {title} — similarity: {similarity:.3f}")
        print()

    cur.close()
    conn.close()
    print("[PASS] Retrieval test complete.")


if __name__ == "__main__":
    test_retrieval()
