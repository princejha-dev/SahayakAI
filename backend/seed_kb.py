"""
Phase 1 — Knowledge Base Seeding
Uses psycopg2 directly with the DATABASE_URL (postgres connection string).
Safe to re-run — skips entries whose title already exists in kb_documents.

Run: python seed_kb.py
"""
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI
from kb_data import KB_ENTRIES

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
DATABASE_URL = os.environ["DATABASE_URL"]
EMBED_MODEL = "text-embedding-3-small"


def get_conn():
    return psycopg2.connect(DATABASE_URL, connect_timeout=15)


def embed_text(text: str, retries: int = 3) -> list[float]:
    for attempt in range(1, retries + 1):
        try:
            response = openai_client.embeddings.create(
                model=EMBED_MODEL,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            if attempt == retries:
                raise
            wait = 2 ** attempt
            print(f"          Retry {attempt}/{retries} after {wait}s — {e}")
            time.sleep(wait)


def seed():
    print(f"Connecting to Supabase postgres...")
    conn = get_conn()
    register_vector(conn)
    cur = conn.cursor()

    # Fetch already-existing titles
    cur.execute("SELECT title FROM kb_documents;")
    existing_titles = {row[0] for row in cur.fetchall()}
    to_insert = [e for e in KB_ENTRIES if e["title"] not in existing_titles]

    print(f"Total entries: {len(KB_ENTRIES)}")
    print(f"Already in DB: {len(existing_titles)}")
    print(f"To insert:     {len(to_insert)}\n")

    inserted = 0
    errors = 0

    for i, entry in enumerate(KB_ENTRIES, 1):
        if entry["title"] in existing_titles:
            print(f"[{i:02d}/{len(KB_ENTRIES)}] SKIP: {entry['title'][:60]}")
            continue

        try:
            print(f"[{i:02d}/{len(KB_ENTRIES)}] Embedding: {entry['title'][:60]}...")
            embedding = embed_text(entry["content"])

            cur.execute(
                """
                INSERT INTO kb_documents (title, category, content, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (entry["title"], entry["category"], entry["content"], embedding),
            )
            conn.commit()
            print(f"          Inserted OK")
            inserted += 1

        except Exception as e:
            conn.rollback()
            print(f"          ERROR: {e}")
            errors += 1

    cur.close()
    conn.close()

    print(f"\n--- Seeding complete ---")
    print(f"Inserted: {inserted} | Errors: {errors}")
    if errors:
        print("Re-run 'python seed_kb.py' to retry failed entries.")
    else:
        print("All entries seeded successfully!")


if __name__ == "__main__":
    seed()
