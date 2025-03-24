"""
Instagram Recipe Search App
"""
import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import re
from datetime import datetime
import os

def format_date(timestamp):
    """Format ISO timestamp to readable date"""
    if not timestamp:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return timestamp

def main():
    """Run the Streamlit app"""
    st.set_page_config(
        page_title="Instagram Recipe Search",
        layout="wide"
    )
    
    st.title("🍽️ Instagram Recipe Search")
    
    st.markdown("""
    ## Find recipes with AI-powered semantic search
    
    This demo shows how vector databases enable searching Instagram food content
    based on ingredients, cooking methods, or cuisine types.
    
    Try searching for:
    - "healthy vegetarian dinner"
    - "quick lunch ideas"
    - "asian inspired"
    """)
    
    # Search interface
    query = st.text_input("What would you like to cook?", placeholder="E.g., spicy dinner, breakfast ideas, etc.")
    
    # Advanced filters
    with st.expander("Advanced Filters"):
        col1, col2 = st.columns(2)
        
        with col1:
            min_likes = st.slider("Minimum likes:", min_value=0, max_value=3000, value=0, step=100)
        
        with col2:
            media_type = st.selectbox(
                "Media type:",
                options=["All Types", "IMAGE", "CAROUSEL_ALBUM", "VIDEO"]
            )
    
    # Number of results
    n_results = st.slider("Number of results:", min_value=1, max_value=10, value=3)
    
    # Search button
    search_button = st.button("Search Recipes")
    
    # Process search
    if search_button and query:
        try:
            # Use absolute path to ensure consistency
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, "chroma_db")
            
            # Initialize model and database
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create client with persistent storage
            client = chromadb.PersistentClient(db_path)
            
            try:
                # Use same collection name as in process_data.py
                collection_name = "instagram_posts"
                collection = client.get_collection(collection_name)
                
                # Prepare filter
                where_clause = {}
                if media_type != "All Types":
                    where_clause["media_type"] = media_type
                if min_likes > 0:
                    where_clause["like_count"] = {"$gte": min_likes}
                
                # Convert query to embedding and search
                query_embedding = model.encode(query).tolist()
                
                # Apply filters if any
                if where_clause:
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results,
                        where=where_clause
                    )
                else:
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results
                    )
                
                # Display results
                st.header("Recipes Found")
                
                if len(results['documents'][0]) > 0:
                    # Display each result
                    for i in range(len(results['documents'][0])):
                        col1, col2 = st.columns([1, 3])
                        
                        # Extract recipe title
                        caption = results['documents'][0][i]
                        title_match = re.search(r'^(.*?) - Another Day In Paradise', caption)
                        title = title_match.group(1) if title_match else "Recipe"
                        
                        with col1:
                            # Display post metrics
                            st.metric("Likes", results['metadatas'][0][i].get('like_count', 0))
                            st.text(f"Comments: {results['metadatas'][0][i].get('comments_count', 0)}")
                            
                            # Display date
                            post_date = format_date(results['metadatas'][0][i].get('timestamp', ''))
                            if post_date:
                                st.text(post_date)
                        
                        with col2:
                            # Recipe title
                            st.subheader(title)
                            
                            # Display content
                            st.markdown(caption[:300] + "..." if len(caption) > 300 else caption)
                            
                            # Display ingredients
                            ingredients = results['metadatas'][0][i].get('ingredients', '').split(',')
                            if ingredients and ingredients[0]:
                                st.markdown("**Main Ingredients:**")
                                ing_text = ", ".join([ing.strip() for ing in ingredients])
                                st.markdown(f"_{ing_text}_")
                            
                            # Display hashtags
                            hashtags = results['metadatas'][0][i].get('hashtags', '').split(',')
                            if hashtags and hashtags[0]:
                                hashtag_text = ' '.join([f"#{tag.strip()}" for tag in hashtags])
                                st.markdown(hashtag_text)
                            
                            # Display similarity
                            similarity = 1 - results['distances'][0][i]
                            st.progress(similarity)
                            st.markdown(f"**Match score:** {similarity:.1%}")
                        
                        st.divider()
                else:
                    st.warning("No matching recipes found with the current filters.")
                    
            except Exception as e:
                st.error(f"Error accessing vector database: {str(e)}")
                st.info("Please run process_data.py first to create the vector database.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()