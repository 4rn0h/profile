# seed_db.py
from app import create_app
from models import db, Project, BlogPost
from datetime import datetime

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Optional reset (for dev only  comment out in production)
        # db.drop_all()
        # db.create_all()

        # Sample projects
        projects = [
            Project(
                title="Flask REST API",
                description="RESTful inventory API with Flask & JWT.",
                image_url="/static/img/flask_api.png",
                project_url="https://inventory.example.com",
                github_url="https://github.com/okothouko/flask-inventory-api"
            ),
            Project(
                title="CI/CD Pipeline with Jenkins",
                description="Automated Docker-based CI/CD pipeline using Jenkins.",
                image_url="/static/img/devops_project.png",
                project_url="https://cicd.example.com",
                github_url="https://github.com/okothouko/jenkins-pipeline"
            ),
            Project(
                title="ETL Pipeline with BigQuery",
                description="Python-based ETL pipeline for sales data analytics with GCP BigQuery.",
                image_url="/static/img/data_etl.png",
                project_url="https://etl.example.com",
                github_url="https://github.com/okothouko/etl-bigquery"
            )
        ]

        # Sample blog posts
        blog_posts = [
            BlogPost(
                title="Building Secure APIs with Flask",
                slug="building-secure-apis-with-flask",
                content="In this post, I walk through Flask-JWT, route protection, and best practices.",
                date_posted=datetime(2025, 5, 10),
                category="Backend Development",   # works only if you added column
                tags="flask,security,api"
            ),
            BlogPost(
                title="Automating CI/CD with Jenkins & Docker",
                slug="automating-ci-cd-with-jenkins-docker",
                content="CI/CD pipeline for Python microservices: Jenkins + GitHub + Docker.",
                date_posted=datetime(2025, 4, 18),
                category="DevOps",
                tags="devops,jenkins,docker"
            )
        ]

        # Insert projects if not already there
        for project in projects:
            existing = Project.query.filter_by(title=project.title).first()
            if not existing:
                db.session.add(project)

        # Insert blog posts if not already there
        for post in blog_posts:
            existing = BlogPost.query.filter_by(slug=post.slug).first()
            if not existing:
                db.session.add(post)
        
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
