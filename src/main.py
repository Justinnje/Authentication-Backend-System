import sqlalchemy
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from . import models, schemas, tokens
from src.models  import SessionLocal, engine

# Create the app
app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Set up OAuth2 security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Dependency to get a database session
def get_db():
    
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
        
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = tokens.decode_jwt(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user


def get_other_user(token, db):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        
        payload = tokens.decode_jwt(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user
        
   
@app.post("/register")
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Validate input
        if not user.email:
            raise HTTPException(status_code=400, detail="Email is required")
        if not user.password:
            raise HTTPException(status_code=400, detail="Password is required")
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        # Create the user
        db_user = models.User(**user.dict())
        db_user.password = tokens.hash_password(db_user.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(status_code=422, detail="role can only be 'ADMIN', 'MEMBER' or 'TECHNICIAN'")


@app.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate the user and return a JWT
    user = tokens.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = tokens.encode_jwt(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_user(current_user: models.User = Depends(get_current_user)):
    # Retrieve the user's own information
    return current_user


@app.put("/users/me")
async def update_user(user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:    
        # Validate input
        if user.email and db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        # Update the user's own information
        # Update the password hash
        if user.password is not None:
            current_user.password = tokens.hash_password(user.password);
            # delete attribute since already made changes
            user.__delattr__("password")
            
        for field, value in user:
            if value:
                setattr(current_user, field, value)
        db.commit()
        db.refresh(current_user)
        
        return current_user
    except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=422, detail="role can only be 'ADMIN', 'MEMBER' or 'TECHNICIAN'")


@app.delete("/users/me")
async def delete_user(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Delete the user's own account
    db.delete(current_user)
    db.commit()
    return {"detail": "User deleted"}


@app.get("/users/admin/view")
async def admin_view_other_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "ADMIN" :
        database = {}
        lst = db.query(models.User).all()
        for item in lst:
            database[item.email] = item.role
        
        return database
    else :
        raise HTTPException(status_code=400, detail="You are not an ADMIN user.")


@app.put("/users/admin/update")
async def admin_update_other_users(user: schemas.AdminUserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:    
        if current_user.role == "ADMIN" and db.query(models.User).filter(models.User.email == user.email).first():
            access_token = tokens.encode_jwt(data={"sub": user.email})
            
            other_user = get_other_user(access_token, db)
            
            other_user.role = user.role
                
            db.commit()
            db.refresh(other_user)
            
            return other_user
        else :
            raise HTTPException(status_code=400, detail="You can only change the role of an email that already exist. Use /users/admin/view url path to view valid email addresses")
    except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=422, detail="role can only be 'ADMIN', 'MEMBER' or 'TECHNICIAN'")


@app.delete("/users/admin/delete")
async def admin_delete_other_users(user: schemas.AdminUserDelete,db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "ADMIN" and db.query(models.User).filter(models.User.email == user.email).first():
        access_token = tokens.encode_jwt(data={"sub": user.email})
            
        other_user = get_other_user(access_token, db)
        db.delete(other_user)
        db.commit()
        return {"detail": "User deleted"}
        
    else :
        raise HTTPException(status_code=400, detail="You can only delete a user that already exist. Use /users/admin/view url path to view valid email addresses")

