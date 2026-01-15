# test_admin.py
from app import create_app

app = create_app()

with app.app_context():
    # List all registered routes
    for rule in app.url_map.iter_rules():
        if 'admin' in rule.rule:
            print(f"Route: {rule.rule} -> {rule.endpoint}")
    
    # Check if admin blueprint is registered
    print("\nRegistered blueprints:")
    for name, blueprint in app.blueprints.items():
        print(f"- {name}: {blueprint}")