# freeze.py
from flask_frozen import Freezer
from app import create_app
import os
import shutil
import sys

# Add freeze flag to sys.argv for app detection
sys.argv.append('freeze')

# Create the app
app = create_app()

# Initialize the freezer
freezer = Freezer(app)

# ----- FILTER ADMIN ROUTES -----

def should_freeze_url(url):
    """Check if a URL should be frozen."""
    # List of URL patterns to skip
    skip_patterns = [
        '/admin',
        '/login',
        '/logout',
        '/migrate-db',
        '/admin-init',
        '/posts',
        '/new',
        '/test',
        '/edit'
    ]
    
    # Skip if URL matches any pattern
    for pattern in skip_patterns:
        if url.startswith(pattern) or url.endswith(pattern):
            return False
    
    # Skip if 'admin' is in the URL
    if 'admin' in url:
        return False
    
    return True

# ----- BLOG POST GENERATORS -----

@freezer.register_generator
def blog_post():
    """Generate a static page for each blog post."""
    with app.app_context():
        try:
            from models import BlogPost
            posts = BlogPost.query.all()
            if posts:
                for post in posts:
                    slug = post.slug if post.slug else f"post-{post.id}"
                    yield {'slug': slug}
            else:
                blog_dir = os.path.join('static', 'blog')
                if os.path.exists(blog_dir):
                    for filename in os.listdir(blog_dir):
                        if filename.endswith('.md'):
                            slug = filename.replace('.md', '')
                            yield {'slug': slug}
        except Exception as e:
            print(f"⚠️ Database not available, using markdown files: {e}")
            blog_dir = os.path.join('static', 'blog')
            if os.path.exists(blog_dir):
                for filename in os.listdir(blog_dir):
                    if filename.endswith('.md'):
                        slug = filename.replace('.md', '')
                        yield {'slug': slug}

# ----- PROJECT GENERATORS -----

@freezer.register_generator
def projects():
    """Generate all projects page."""
    yield {}

# ----- MAIN PAGES -----

@freezer.register_generator
def index():
    yield {}

@freezer.register_generator
def about_me():
    yield {}

@freezer.register_generator
def blog():
    yield {}

@freezer.register_generator
def contact():
    yield {}

# ----- CUSTOM FREEZE FUNCTION -----

def freeze_with_filtering():
    """Freeze only public URLs, skipping admin routes."""
    from flask_frozen import Freezer
    import sys
    
    print("📋 Filtering URLs...")
    print("-" * 50)
    
    # Get all URLs from the freezer
    with app.app_context():
        all_urls = []
        
        # Get all routes from the app
        for rule in app.url_map.iter_rules():
            url = str(rule)
            endpoint = rule.endpoint
            
            # Skip static
            if endpoint == 'static':
                continue
            
            # Skip admin endpoints
            if endpoint.startswith('admin.') or endpoint == 'admin':
                continue
            
            # Skip if URL contains admin
            if '/admin' in url:
                continue
            
            # Add the URL
            if should_freeze_url(url):
                all_urls.append(url)
                print(f"✅ Including: {url}")
            else:
                print(f"⏭️ Skipping: {url}")
        
        print("-" * 50)
        print(f"📋 Freezing {len(all_urls)} URLs...")
        print("-" * 50)
        
        # Freeze each URL
        for url in all_urls:
            try:
                # Clean the URL
                clean_url = url
                if clean_url.startswith('/'):
                    clean_url = clean_url[1:]
                if not clean_url:
                    clean_url = 'index'
                
                print(f"   🏗️ Building: /{clean_url}")
                
                # Build the URL
                freezer._build_one(url, None)
            except Exception as e:
                print(f"   ⚠️ Error building {url}: {e}")

# Override the freeze method
freezer.freeze = freeze_with_filtering

# ----- COPY STATIC FILES -----

def copy_static_files():
    print("📁 Copying static files...")
    static_src = os.path.join(os.path.dirname(__file__), 'static')
    static_dst = os.path.join(os.path.dirname(__file__), 'build', 'static')
    
    if os.path.exists(static_src):
        if os.path.exists(static_dst):
            shutil.rmtree(static_dst)
        shutil.copytree(static_src, static_dst)
        print(f"✅ Static files copied")
    
    favicon_src = os.path.join(os.path.dirname(__file__), 'static', 'favicon.ico')
    if os.path.exists(favicon_src):
        favicon_dst = os.path.join(os.path.dirname(__file__), 'build')
        shutil.copy2(favicon_src, favicon_dst)
        print(f"✅ Favicon copied")

def copy_html_files():
    print("📄 Copying HTML files...")
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    html_files = ['404.html', '403.html', '500.html']
    
    for html_file in html_files:
        src = os.path.join(template_dir, html_file)
        if os.path.exists(src):
            dst = os.path.join(os.path.dirname(__file__), 'build', html_file)
            shutil.copy2(src, dst)
            print(f"✅ {html_file} copied")

# ----- RUN THE FREEZE -----

if __name__ == '__main__':
    # Clean build directory
    build_dir = os.path.join(os.path.dirname(__file__), 'build')
    if os.path.exists(build_dir):
        print(f"🧹 Cleaning existing build directory...")
        shutil.rmtree(build_dir)
    
    os.makedirs(build_dir, exist_ok=True)
    
    print("🔨 Starting freeze process...")
    print("=" * 50)
    
    try:
        # Run the freeze with filtering
        freezer.freeze()
        
        print("✅ HTML generation complete!")
        print("-" * 50)
        copy_static_files()
        print("-" * 50)
        copy_html_files()
        
        # Create _redirects file for Netlify
        print("-" * 50)
        redirects_dst = os.path.join(os.path.dirname(__file__), 'build', '_redirects')
        with open(redirects_dst, 'w') as f:
            f.write("/*    /index.html   200\n")
            f.write("/blog/*    /blog/index.html   200\n")
            f.write("/about_me    /about_me   200\n")
            f.write("/projects    /projects   200\n")
            f.write("/contact    /contact   200\n")
        print("✅ _redirects file created for Netlify")
        
        # .nojekyll for GitHub Pages
        nojekyll_dst = os.path.join(os.path.dirname(__file__), 'build', '.nojekyll')
        with open(nojekyll_dst, 'w') as f:
            f.write("")
        print("✅ .nojekyll file created for GitHub Pages")
        
        print("=" * 50)
        print("🎉 Freeze complete! Files are in the 'build' directory.")
        
        # Show build size
        total_size = 0
        file_count = 0
        for dirpath, dirnames, filenames in os.walk('build'):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
                file_count += 1
        print(f"📊 Build: {file_count} files, {total_size / 1024 / 1024:.2f} MB")
        
        # List generated pages
        print("\n📄 Generated pages:")
        for root, dirs, files in os.walk('build'):
            if 'static' in root:
                continue
            for f in files:
                if f.endswith('.html') or f.endswith('.htm'):
                    rel_path = os.path.relpath(os.path.join(root, f), 'build')
                    if rel_path == 'index.html':
                        print(f"   - /")
                    elif rel_path.endswith('index.html'):
                        dir_name = os.path.dirname(rel_path)
                        if dir_name:
                            print(f"   - /{dir_name}/")
                    else:
                        print(f"   - /{rel_path}")
        
    except Exception as e:
        print(f"❌ Error during freeze: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)