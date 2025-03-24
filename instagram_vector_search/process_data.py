"""
Process Instagram data and load into Chroma vector database
"""
import json
import os
import polars as pl
from sentence_transformers import SentenceTransformer
import chromadb

def main():
    """Process Instagram data into vector database"""
    print("Processing Instagram data...")
    
    # Check for data files
    if not os.path.exists('data/instagram_posts.csv'):
        print("No data found. Please run create_mock_data first.")
        return
    
    # Load data
    df = pl.read_csv('data/instagram_posts.csv')
    print(f"Loaded {len(df)} posts from CSV file")
    
    # Use absolute path to ensure consistency
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, "chroma_db")
    
    # Initialize Chroma client with persistent storage
    client = chromadb.PersistentClient(db_path)
    
    # Use consistent collection name
    collection_name = "instagram_posts"
    
    # Remove collection if it exists
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    # Create collection
    collection = client.create_collection(collection_name)
    
    # Initialize sentence transformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Process posts
    documents = []
    metadatas = []
    ids = []
    
    # Convert DataFrame to records
    posts = df.to_dicts()
    
    for i, post in enumerate(posts):
        # Create text for embedding
        caption = post.get('caption', '')
        hashtags = post.get('hashtags', '').split(',')
        ingredients = post.get('ingredients', '').split(',')
        
        # Combine text elements for embedding
        text_for_embedding = f"{caption} {' '.join(['#' + tag for tag in hashtags])} Ingredients: {', '.join(ingredients)}"
        documents.append(text_for_embedding)
        
        # Extract metadata
        metadata = {
            'post_id': post.get('id', str(i)),
            'permalink': post.get('permalink', ''),
            'media_type': post.get('media_type', ''),
            'timestamp': post.get('timestamp', ''),
            'like_count': int(post.get('like_count', 0)),
            'comments_count': int(post.get('comments_count', 0)),
            'hashtags': post.get('hashtags', ''),
            'ingredients': post.get('ingredients', '')
        }
        metadatas.append(metadata)
        ids.append(str(i))
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = model.encode(documents).tolist()
    
    # Add to collection
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Added {len(documents)} posts to vector database")
    print(f"Database stored at: {db_path}")

if __name__ == "__main__":
    main()
