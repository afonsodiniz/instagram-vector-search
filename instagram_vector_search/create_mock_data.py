"""
Create mock Instagram data for vector search demo
"""
import json
import os
import random
from datetime import datetime, timedelta
import polars as pl

def random_date():
    """Generate a random date within the past year"""
    now = datetime.now()
    days_back = random.randint(1, 365)
    return (now - timedelta(days=days_back)).isoformat()

def main():
    """Generate mock Instagram recipe posts"""
    print("Creating mock Instagram data...")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Create sample posts based on real content
    posts = [
        {
            "id": "1001",
            "caption": "Smokey Breaded Aubergine with Tomato and Burrata - Another Day In Paradise\nThis is basically an aubergine/eggplant parmesan - a classic I have love for but don't really get down with these days. I usually want it to taste more like aubergine, with a bit of crunch, and have something bright and acidic to cut through it beyond the tomato sauce.",
            "media_type": "CAROUSEL_ALBUM",
            "permalink": "https://instagram.com/p/mock1001",
            "timestamp": random_date(),
            "like_count": random.randint(500, 3000),
            "comments_count": random.randint(20, 150),
            "hashtags": ["aubergine", "eggplant", "burrata", "recipe", "vegetarian"],
            "ingredients": ["aubergine", "flour", "breadcrumbs", "egg", "milk", "tomatoes", "shallot", "garlic", "basil", "burrata"]
        },
        {
            "id": "1002",
            "caption": "Spicy Carottes Râpées, and Chicken With Pan Sauce - Another Day In Paradise\nI love the classic French shredded carrot salad, and highly recommend you have it in your back pocket if you don't already. This version is not the classic, but still hits a lot of the same notes.",
            "media_type": "IMAGE",
            "permalink": "https://instagram.com/p/mock1002",
            "timestamp": random_date(),
            "like_count": random.randint(500, 3000),
            "comments_count": random.randint(20, 150),
            "hashtags": ["french", "carrots", "chicken", "recipe", "pansauce"],
            "ingredients": ["carrots", "chicken", "herbs", "vinegar"]
        },
        {
            "id": "1003",
            "caption": "Pork Belly Rice - Another Day In Paradise\nI've been throwing stuff in my rice cooker to see what happens since I've had one - this combo is my favourite so far. Always with something fresh and pickled near by.",
            "media_type": "CAROUSEL_ALBUM",
            "permalink": "https://instagram.com/p/mock1004",
            "timestamp": random_date(),
            "like_count": random.randint(500, 3000),
            "comments_count": random.randint(20, 150),
            "hashtags": ["porkbelly", "rice", "ricecooker", "asian"],
            "ingredients": ["pork belly", "sushi rice", "ginger", "garlic", "soy sauce", "sesame oil"]
        }
    ]
    
    # Save to JSON format (works fine with nested data)
    with open('data/instagram_posts.json', 'w') as f:
        json.dump(posts, f, indent=2)

    # Prepare data for CSV by flattening nested structures
    csv_data = []
    for post in posts:
        csv_post = post.copy()
        # Convert lists to comma-separated strings
        if "hashtags" in csv_post:
            csv_post["hashtags"] = ",".join(csv_post["hashtags"])
        if "ingredients" in csv_post:
            csv_post["ingredients"] = ",".join(csv_post["ingredients"])
        csv_data.append(csv_post)

    # Save to CSV format using Polars
    df = pl.DataFrame(csv_data)
    df.write_csv('data/instagram_posts.csv')
    
    print(f"Created mock dataset with {len(posts)} Instagram posts")
    print(f"Data saved to data/instagram_posts.json and data/instagram_posts.csv")

if __name__ == "__main__":
    main()