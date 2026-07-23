from sqlalchemy.orm import Session
from app.domain.models.usuario import Usuario


def buscar_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()


def buscar_por_id(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def listar(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Usuario).offset(skip).limit(limit).all()


def criar(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def atualizar(db: Session, usuario: Usuario) -> Usuario:
    db.commit()
    db.refresh(usuario)
    return usuario
