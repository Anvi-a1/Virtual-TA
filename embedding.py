import os
import faiss
import json
import numpy as np
from typing import List, Dict
from bs4 import BeautifulSoup
import markdown as md
from dotenv import load_dotenv
import google.generativeai as genai
import time

load_dotenv()

# CONFIGURATION
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Embedding & FAISS parameters
EMBED_DIM = 768  # Gemini embedding dimension
BATCH_SIZE = 100  # Gemini has higher rate limits
CHUNK_SIZE = 2000  # words per chunk (Gemini handles longer context well)
CHUNK_OVERLAP = 200

# Initialize FAISS
index = faiss.IndexFlatIP(EMBED_DIM)
metadata: List[Dict] = []


def chunk_by_words(text: str, max_words: int, overlap: int) -> List[str]:
    """Split text into chunks by word count with overlap"""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += max_words - overlap
    return chunks


def embed_text(text: str) -> list:
    """Get normalized embedding from Gemini API"""
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document"
    )
    embedding = np.array(result['embedding'], dtype=np.float32)
    normalized_embedding = embedding / np.linalg.norm(embedding)
    return normalized_embedding.tolist()


def safe_embed(text: str, retry_count: int = 0) -> list:
    """Embed text with error handling for rate limits"""
    try:
        return embed_text(text)
    except Exception as e:
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            if retry_count < 3:
                wait_time = 10 * (retry_count + 1)
                print(f"Rate limit hit, waiting {wait_time}s...")
                time.sleep(wait_time)
                return safe_embed(text, retry_count + 1)
        elif len(text) > 10000:  # If text too long, split it
            mid = len(text) // 2
            left = safe_embed(text[:mid])
            right = safe_embed(text[mid:])
            return ((np.array(left) + np.array(right)) / 2).tolist()
        raise


def load_markdown(path: str) -> str:
    """Load and convert markdown to plain text"""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    html = md.markdown(raw)
    return BeautifulSoup(html, "html.parser").get_text("\n")


def ingest_markdown_files():
    """Process markdown files from markdown_files folder"""
    batch_texts, batch_meta = [], []
    markdown_dir = "markdown_files"
    
    if not os.path.exists(markdown_dir):
        print(f"Warning: {markdown_dir} directory not found")
        return batch_texts, batch_meta
    
    print(f"\n=== Processing Markdown Files ===")
    files = [f for f in os.listdir(markdown_dir) if f.endswith(".md")]
    
    for fname in files:
        full_path = os.path.join(markdown_dir, fname)
        text = load_markdown(full_path)
        word_count = len(text.split())
        print(f"Loaded {fname}: {len(text)} chars, {word_count} words")
        
        chunks = chunk_by_words(text, max_words=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        
        for idx, chunk in enumerate(chunks):
            meta = {
                "source": f"Course: {fname.replace('.md', '')}",
                "type": "course_content",
                "chunk_id": idx,
                "total_chunks": len(chunks)
            }
            batch_texts.append(chunk)
            batch_meta.append(meta)
    
    print(f"Created {len(batch_texts)} chunks from {len(files)} markdown files")
    return batch_texts, batch_meta


def ingest_discourse_json():
    """Process discourse posts from discourse_posts.json"""
    batch_texts, batch_meta = [], []
    discourse_file = "discourse_posts.json"
    
    if not os.path.exists(discourse_file):
        print(f"Warning: {discourse_file} not found")
        return batch_texts, batch_meta
    
    print(f"\n=== Processing Discourse Posts ===")
    with open(discourse_file, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    # Group posts by topic_id
    topics = {}
    for post in posts:
        topic_id = post["topic_id"]
        if topic_id not in topics:
            topics[topic_id] = {
                "title": post.get("topic_title", "N/A"),
                "posts": []
            }
        topics[topic_id]["posts"].append(post)
    
    print(f"Found {len(posts)} posts across {len(topics)} topics")
    
    # Process each topic
    for topic_id, topic_data in topics.items():
        posts_list = sorted(topic_data["posts"], key=lambda x: x['post_number'])
        topic_title = topic_data["title"]
        
        # Combine all posts in topic
        topic_text = f"Topic: {topic_title}\n\n"
        topic_text += "\n\n---\n\n".join([
            f"Post #{p['post_number']}: {p['content']}" 
            for p in posts_list
        ])
        
        chunks = chunk_by_words(topic_text, max_words=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        
        for idx, chunk in enumerate(chunks):
            meta = {
                "source": f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}",
                "type": "discourse_post",
                "topic_id": topic_id,
                "topic_title": topic_title,
                "chunk_id": idx,
                "total_chunks": len(chunks)
            }
            batch_texts.append(chunk)
            batch_meta.append(meta)
    
    print(f"Created {len(batch_texts)} chunks from discourse posts")
    return batch_texts, batch_meta


def index_batch(texts: List[str], metas: List[Dict]):
    """Embed texts and add to FAISS index"""
    print(f"\nEmbedding batch of {len(texts)} chunks...")
    embs = []
    for i, text in enumerate(texts):
        if i % 10 == 0:
            print(f"  Embedding {i+1}/{len(texts)}...")
        emb = safe_embed(text)
        embs.append(emb)
    
    arr = np.array(embs, dtype=np.float32)
    index.add(arr)
    metadata.extend([{"text": t, **m} for t, m in zip(texts, metas)])
    print(f"✓ Indexed {len(texts)} chunks; total index size: {index.ntotal}")


def main():
    """Main ingestion pipeline"""
    print("=" * 60)
    print("VirtualTA Embedding Pipeline (Gemini)")
    print("=" * 60)
    
    # Collect all texts and metadata
    all_texts, all_meta = [], []
    
    # Process markdown files
    md_texts, md_meta = ingest_markdown_files()
    all_texts.extend(md_texts)
    all_meta.extend(md_meta)
    
    # Process discourse posts
    disc_texts, disc_meta = ingest_discourse_json()
    all_texts.extend(disc_texts)
    all_meta.extend(disc_meta)
    
    if not all_texts:
        print("\n❌ No data found to process!")
        print("Make sure you have:")
        print("  - markdown_files/ folder with .md files")
        print("  - discourse_posts.json file")
        return
    
    print(f"\n{'=' * 60}")
    print(f"Total chunks to embed: {len(all_texts)}")
    print(f"{'=' * 60}\n")
    
    # Process in batches
    for i in range(0, len(all_texts), BATCH_SIZE):
        batch_texts = all_texts[i:i+BATCH_SIZE]
        batch_meta = all_meta[i:i+BATCH_SIZE]
        index_batch(batch_texts, batch_meta)
    
    # Save outputs
    os.makedirs("model/", exist_ok=True)
    
    print(f"\n{'=' * 60}")
    print("Saving outputs...")
    faiss.write_index(index, "model/virtual-ta.faiss")
    print("✓ Saved FAISS index: model/virtual-ta.faiss")
    
    with open("model/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print("✓ Saved metadata: model/metadata.json")
    
    print(f"{'=' * 60}")
    print("✓ Ingestion Complete!")
    print(f"  Total indexed chunks: {index.ntotal}")
    print(f"  Index dimension: {EMBED_DIM}")
    print(f"  Model: Gemini text-embedding-004")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
