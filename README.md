# FastAPI Social App

A simple social network simulation built with FastAPI featuring basic CRUD operations: user registration, post creation, likes, search, and updates.

## 🚀 Features

- ✅ User registration and authentication  
- 📝 Create, edit, and delete posts  
- ❤️ Like posts  
- 🔍 Retrieve all posts or a single post by ID  
- 🔐 JWT authentication (OAuth2 password flow)  
- 📄 Fully documented API with Swagger UI and ReDoc  

## 🛠 How to Run

1. Clone the repository:

```bash
git clone https://github.com/Taqtaq/fastapi-social-app.git
cd fastapi-social-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --reload
```

4. Open API documentation in your browser:  
Swagger UI: http://127.0.0.1:8000/docs  
ReDoc: http://127.0.0.1:8000/redoc  


## 🔧 Technologies
FastAPI  
Pydantic  
SQLAlchemy  
PostgreSQL or SQLite  
JWT (JSON Web Tokens)  


## 📂 Project Structure
```
📁 app/
├── 📁 routers/                 # API route handlers
│   ├── auth.py                # Authentication and login logic
│   ├── post.py                # Post-related endpoints
│   ├── user.py                # User-related endpoints
│   ├── vote.py                # Voting functionality
│   └── __init__.py            # Initializes the routers module
├── config.py                  # Application configuration settings
├── database.py                # Database connection and setup
├── main.py                    # Application entry point
├── models.py                  # SQLAlchemy models (database tables)
├── oauth2.py                  # OAuth2 token handling and security
├── schemas.py                 # Pydantic models for request/response validation
├── utils.py                   # Utility functions
requirements.txt             # Project dependencies
```


## Notes
This project is designed for learning and can be extended with features like comments, followers, photos, and more.


## Contact

If you have any questions, feel free to reach out: https://t.me/pumba_taq