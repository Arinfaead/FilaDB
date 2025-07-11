import asyncio
from sqlmodel import Session, select
from .core.database import engine, create_db_and_tables
from .core.security import get_password_hash
from .models.user import User, UserRole


def create_admin_user(email: str, password: str):
    """Create an admin user"""
    create_db_and_tables()
    
    with Session(engine) as session:
        # Check if user already exists
        statement = select(User).where(User.email == email)
        existing_user = session.exec(statement).first()
        
        if existing_user:
            print(f"User {email} already exists")
            return
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        print(f"Admin user {email} created successfully")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python -m app.cli <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    create_admin_user(email, password)
