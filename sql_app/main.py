import hashlib

from typing import List
from typing import Annotated
import random, string
from fastapi.responses import JSONResponse, Response

from fastapi import Depends, FastAPI, HTTPException, Header
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_session = Depends(get_db)


@app.get("/health-check")
def health_check(db: Session = db_session):
    return {"status": "ok"}

@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = db_session) -> Response:
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    #トークンを作成する。
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    new_user = crud.create_user(db=db, user=user, token=token)
    return JSONResponse(content={"email":new_user.email, "id":new_user.id, "is_active":new_user.is_active, "items":new_user.items, "password":token})

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = db_session):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, x_api_token: Annotated[str | None, Header()], db: Session = db_session):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user.hashed_password != hashlib.sha256(x_api_token.encode("utf-8")).hexdigest():
        raise HTTPException(status_code=401, detail="Invalid user token")
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, x_api_token: Annotated[str | None, Header()], db: Session = db_session
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user.hashed_password != hashlib.sha256(x_api_token.encode("utf-8")).hexdigest():
        raise HTTPException(status_code=401, detail="Invalid user token")
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = db_session):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/me/items/{user_id}", response_model=List[schemas.Item])
def read_items_for_user(user_id: int, x_api_token: Annotated[str | None, Header()], db: Session = db_session):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user.hashed_password != hashlib.sha256(x_api_token.encode("utf-8")).hexdigest():
        raise HTTPException(status_code=401, detail="Invalid user token")
    items = crud.get_user_items(db=db, user_id=user_id)
    return items

@app.post("/users/delete/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, x_api_token: Annotated[str | None, Header()], db: Session = db_session):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user.hashed_password != hashlib.sha256(x_api_token.encode("utf-8")).hexdigest():
        raise HTTPException(status_code=401, detail="Invalid user token")
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.deactivate_user(db=db, user_id=user_id)
