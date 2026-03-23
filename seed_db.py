# seed_db.py
from app import create_app
from models import db, Project, BlogPost
from datetime import datetime
import os

# helper to load markdown files from static/blog
BASE_DIR = os.path.dirname(__file__)
def load_md(filename):
    path = os.path.join(BASE_DIR, 'static', 'blog', filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Clear existing data to avoid duplicates and ensure clean state
        print("Clearing existing data...")
        try:
            db.session.query(BlogPost).delete()
            db.session.query(Project).delete()
            db.session.commit()
            print("Database cleared.")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing database: {e}")

        # Sample projects
        projects = [
            Project(
                title="Flask REST API",
                description="RESTful inventory API with Flask & JWT.",
                image_url="/static/img/flask_api.png",
                project_url="https://inventory.example.com",
                github_url="https://github.com/4rn0h/flask-inventory-api"
            ),
            Project(
                title="CI/CD Pipeline with Jenkins",
                description="Automated Docker-based CI/CD pipeline using Jenkins.",
                image_url="/static/img/devops_project.png",
                project_url="https://cicd.example.com",
                github_url="https://github.com/4rn0h/jenkins-pipeline"
            ),
            Project(
                title="ETL Pipeline with BigQuery",
                description="Python-based ETL pipeline for sales data analytics with GCP BigQuery.",
                image_url="/static/img/data_etl.png",
                project_url="https://etl.example.com",
                github_url="https://github.com/4rn0h/etl-bigquery"
            )
        ]

        # Consolidated blog posts - match slugs with filenames
        blog_posts = [
            BlogPost(
                title="Building Secure APIs with Flask",
                slug="flask_jwt_blog",
                content=load_md('flask_jwt_blog.md'),
                date_posted=datetime(2025, 5, 10),
                category="Backend Development",
                tags="Flask, JWT, Authentication, Security, Python, Backend",
                is_published=True
            ),
            BlogPost(
                title="Automating CI/CD with Jenkins & Docker",
                slug="jenkins_docker_cicd",
                content=load_md('jenkins_docker_cicd.md'),
                date_posted=datetime(2025, 4, 18),
                category="DevOps",
                tags="Jenkins, Docker, CI/CD, DevOps, Containerization",
                is_published=True
            ),
            BlogPost(
                title="ETL Pipeline with BigQuery",
                slug="etl-pipeline",
                content=load_md('etl-pipeline.md'),
                date_posted=datetime(2025, 3, 1),
                category="Data Engineering",
                tags="ETL, BigQuery, GCP, Python, Data Pipelines",
                is_published=True
            ),
            BlogPost(
                title="Building RESTful APIs with Flask",
                slug="flask-api",
                content=load_md('flask-api.md'),
                date_posted=datetime(2025, 2, 15),
                category="Backend Development",
                tags="Python, Flask, REST API, Backend",
                is_published=True
            ),
            BlogPost(
                title="CI/CD Automation with Jenkins",
                slug="jenkins-devops",
                content=load_md('jenkins-devops.md'),
                date_posted=datetime(2025, 1, 20),
                category="DevOps",
                tags="Jenkins, CI/CD, DevOps, Automation",
                is_published=True
            ),
            BlogPost(
                title="Payment API Integration with Django",
                slug="django_payment_api",
                content=load_md('django_payment_api.md'),
                date_posted=datetime(2025, 6, 5),
                category="Backend Development",
                tags="Python, Django, Payment Processing, API, Stripe, Backend",
                is_published=True
            ),
            BlogPost(
                title="Container Orchestration with AWS ECS Fargate",
                slug="aws_ecs_fargate",
                content=load_md('aws_ecs_fargate.md'),
                date_posted=datetime(2025, 7, 12),
                category="Cloud & DevOps",
                tags="AWS, ECS, Fargate, Containerization, Cloud, DevOps",
                is_published=True
            )
        ]

        # Insert projects
        for project in projects:
            db.session.add(project)

        # Insert blog posts
        for post in blog_posts:
            db.session.add(post)
        
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()