import os
import markdown
from models import Project, BlogPost

# Base directory for the application
BASE_DIR = os.path.dirname(os.path.dirname(__file__)) if os.path.dirname(__file__) else os.getcwd()

def get_blog_markdown_html(slug):
    """Load a markdown file from static/blog/<slug>.md and return HTML, or None if not found."""
    md_path = os.path.join(BASE_DIR, 'static', 'blog', f"{slug}.md")
    if not os.path.exists(md_path):
        # Try to find the best matching markdown file by token overlap
        try:
            files = [f for f in os.listdir(os.path.join(BASE_DIR, 'static', 'blog')) if f.endswith('.md')]
        except Exception:
            return None

        import re
        def tokens(s):
            return set([t.lower() for t in re.split(r'[^0-9a-zA-Z]+', s) if t])

        slug_tokens = tokens(slug)
        best_file = None
        best_score = 0
        for f in files:
            name = os.path.splitext(f)[0]
            t = tokens(name)
            score = len(slug_tokens & t)
            if score > best_score:
                best_score = score
                best_file = f

        if best_score > 0 and best_file:
            md_path = os.path.join(BASE_DIR, 'static', 'blog', best_file)
        else:
            return None
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        # convert to HTML with useful extensions
        html = markdown.markdown(md_text, extensions=['fenced_code', 'codehilite', 'tables', 'toc'])
        return html
    except Exception:
        return None


def html_to_excerpt(html_text, words=30):
    """Convert HTML to a plain-text excerpt of up to `words` words, returned as a safe HTML paragraph."""
    import re
    import html as _html

    if not html_text:
        return ''

    # remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_text)
    # unescape HTML entities
    text = _html.unescape(text).strip()
    if not text:
        return ''

    parts = text.split()
    if len(parts) <= words:
        excerpt_text = ' '.join(parts)
    else:
        excerpt_text = ' '.join(parts[:words]) + '...'

    # wrap in paragraph for safe rendering in templates
    return f"<p>{excerpt_text}</p>"

def get_featured_projects():
    return Project.query.order_by(Project.id.desc()).limit(3).all()

def get_all_projects():
    return Project.query.order_by(Project.id.desc()).all()

def get_recent_blog_posts():
    return BlogPost.query.order_by(BlogPost.date_posted.desc()).limit(3).all()

def get_all_blog_posts():
    return BlogPost.query.order_by(BlogPost.date_posted.desc()).all()