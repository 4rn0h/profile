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

        # Sample blog posts - now includes all 7 blog posts
        blog_posts = [
            BlogPost(
                title="Building Secure APIs with Flask",
                slug="building-secure-apis-with-flask",
                content=load_md('flask_jwt_blog.md') or "In this post, I walk through Flask-JWT, route protection, and best practices.",
                date_posted=datetime(2025, 5, 10),
                category="Backend Development",
                tags="Flask, JWT, Authentication, Security, Python, Backend"
            ),
            BlogPost(
                title="Automating CI/CD with Jenkins & Docker",
                slug="automating-ci-cd-with-jenkins-docker",
                content=load_md('jenkins_docker_cicd.md') or "CI/CD pipeline for Python microservices: Jenkins + GitHub + Docker.",
                date_posted=datetime(2025, 4, 18),
                category="DevOps",
                tags="Jenkins, Docker, CI/CD, DevOps, Containerization"
            ),
            BlogPost(
                title="ETL Pipeline with BigQuery",
                slug="etl-pipeline-with-bigquery",
                content=load_md('etl-pipeline.md'),
                date_posted=datetime(2025, 3, 1),
                category="Data Engineering",
                tags="ETL, BigQuery, GCP, Python, Data Pipelines, Apache Airflow"
            ),
            BlogPost(
                title="Building RESTful APIs with Flask",
                slug="building-restful-apis-with-flask",
                content=load_md('flask-api.md') or "Comprehensive guide to building REST APIs with Flask framework.",
                date_posted=datetime(2025, 2, 15),
                category="Backend Development",
                tags="Python, Flask, REST API, Backend"
            ),
            BlogPost(
                title="CI/CD Automation with Jenkins",
                slug="ci-cd-automation-with-jenkins",
                content=load_md('jenkins-devops.md') or "Setting up Jenkins for continuous integration and deployment.",
                date_posted=datetime(2025, 1, 20),
                category="DevOps",
                tags="Jenkins, CI/CD, DevOps, Automation"
            ),
            BlogPost(
                title="Payment API Integration with Django",
                slug="payment-api-integration-with-django",
                content=load_md('django_payment_api.md') or "Implementing payment processing with Django and Stripe API.",
                date_posted=datetime(2025, 6, 5),
                category="Backend Development",
                tags="Python, Django, Payment Processing, API, Stripe, Backend"
            ),
            BlogPost(
                title="Container Orchestration with AWS ECS Fargate",
                slug="container-orchestration-with-aws-ecs-fargate",
                content=load_md('aws_ecs_fargate.md') or "Deploying and managing containers using AWS ECS Fargate.",
                date_posted=datetime(2025, 7, 12),
                category="Cloud & DevOps",
                tags="AWS, ECS, Fargate, Containerization, Cloud, DevOps"
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