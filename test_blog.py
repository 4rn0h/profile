# test_blog.py
from app import create_app
from models import BlogPost

def test_blog_functionality():
    app = create_app()
    
    with app.app_context():
        print("=== Testing Blog Functionality ===")
        
        # Test if we can query blog posts
        try:
            posts = BlogPost.query.all()
            print(f"✅ Found {len(posts)} blog posts in database")
            
            for post in posts:
                print(f"  - {post.title}")
                print(f"    Slug: {post.slug}")
                print(f"    Read Time: {post.read_time}")
                print(f"    Category: {post.category}")
                print(f"    Tags: {post.tags}")
                print()
                
        except Exception as e:
            print(f"❌ Error querying blog posts: {e}")
            
        # Test content loader functions
        try:
            from services.content_loader import get_all_blog_posts, get_recent_blog_posts
            
            all_posts = get_all_blog_posts()
            recent_posts = get_recent_blog_posts()
            
            print(f"✅ Content loader working:")
            print(f"   - All posts: {len(all_posts)}")
            print(f"   - Recent posts: {len(recent_posts)}")
            
        except Exception as e:
            print(f"❌ Error with content loader: {e}")

if __name__ == '__main__':
    test_blog_functionality()