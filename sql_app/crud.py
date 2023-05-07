import hashlib
from typing import Annotated
import random, string
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, token: str):
    token_digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    db_user = models.User(email=user.email, hashed_password=token_digest)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def get_user_items(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first().items

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def deactivate_user(db: Session, user_id: int):
    #指定されたユーザーのis_activeフラグを更新する。
    db.query(models.User).filter(models.User.id == user_id).update({models.User.is_active: False})
    #ユーザーIDが有効なユーザーの内、IDが最初のユーザーを取得する。
    db_user_delegate = db.query(models.User).filter(models.User.is_active == True).order_by(models.User.id).first()
    #指定されたユーザーが所持するアイテムのowner_idを先に取得したユーザーのIDに更新する
    db.query(models.Item).filter(models.Item.owner_id == user_id).update({models.Item.owner_id: db_user_delegate.id})
    #ここまでの更新をDBに反映
    db.commit()
    db.refresh(db_user_delegate)
    #アイテムを譲渡したユーザーの情報を返す
    return db.query(models.User).filter(models.User.id == db_user_delegate.id).first()
