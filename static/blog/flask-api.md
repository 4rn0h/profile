# Building Secure APIs with Flask

Securing APIs is a must-have for any backend developer. In this post, I walk you through how I used Flask to build a REST API with token-based authentication.

## Key Topics

- JWT (JSON Web Tokens)
- User Authentication
- Role-Based Access Control
- Flask extensions: `flask-jwt-extended`

## Sample: Protecting Routes

```python
@app.route('/dashboard')
@jwt_required()
def dashboard():
    return jsonify(message="You are viewing a protected route")
```

## Lessons Learned

- Token-based systems are stateless and scale well.
- Never store sensitive data in JWT payloads.
