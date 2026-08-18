import hashlib
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.domain.models.usuario import Usuario
from app.domain.models.refresh_token import RefreshToken
from app.domain.models.log_auditoria import LogAuditoria
from app.domain.models.consentimento_lgpd import ConsentimentoLGPD
from app.infrastructure.repositories import usuario_repository
from app.infrastructure.security.password_handler import hash_senha, verificar_senha
from app.infrastructure.security.jwt_handler import (
    criar_access_token, criar_refresh_token, decodificar_token
)
from app.application.schemas.auth_schema import LoginRequest, TokenResponse
from app.application.schemas.usuario_schema import UsuarioCreate
from datetime import datetime, timezone


def registrar_usuario(db: Session, dados: UsuarioCreate) -> Usuario:
    """Cria novo usuario com senha hasheada e registra consentimento LGPD."""
    if usuario_repository.buscar_por_email(db, dados.email):
        raise HTTPException(status_code=409, detail="E-mail ja cadastrado.")

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        perfil=dados.perfil,
        telefone=dados.telefone,
        cpf=dados.cpf,
        data_nascimento=dados.data_nascimento,
        unidade_id=dados.unidade_id,
    )
    db.add(usuario)
    db.flush()

    # Registra consentimento LGPD basico obrigatorio
    db.add(ConsentimentoLGPD(
        usuario_id=usuario.id,
        tipo_consentimento="DADOS_CADASTRO",
        consentiu=True,
    ))
    db.commit()
    db.refresh(usuario)
    _log(db, usuario.id, "USUARIO_CRIADO", "usuario", usuario.id)
    return usuario


def login(db: Session, dados: LoginRequest, ip: str = None) -> TokenResponse:
    """Autentica usuario e retorna access + refresh tokens."""
    usuario = usuario_repository.buscar_por_email(db, dados.email)
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha invalidos.")
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Conta desativada.")

    payload = {"sub": str(usuario.id), "perfil": usuario.perfil}
    access_token = criar_access_token(payload)
    refresh_token_str = criar_refresh_token(payload)

    # Armazena hash do refresh token para controle de revogacao
    token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()

    decoded = decodificar_token(refresh_token_str)
    exp_unix = decoded.get("exp")
    exp_datetime = datetime.fromtimestamp(exp_unix, tz=timezone.utc) if exp_unix else None

    db.add(RefreshToken(
        usuario_id=usuario.id,
        token_hash=token_hash,
        expires_at=exp_datetime,
        revogado=False,
    ))
    db.commit()
    _log(db, usuario.id, "LOGIN", "usuario", usuario.id, ip_origem=ip)

    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=1800,
        refresh_token=refresh_token_str,
        perfil=usuario.perfil,
    )


def logout(db: Session, refresh_token_str: str, usuario_id: int):
    """Revoga o refresh token, invalidando a sessao."""
    token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
    rt = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.usuario_id == usuario_id,
    ).first()
    if rt:
        rt.revogado = True
        db.commit()
    _log(db, usuario_id, "LOGOUT", "usuario", usuario_id)


def _log(db, usuario_id, acao, entidade, entidade_id, ip_origem=None):
    db.add(LogAuditoria(
        usuario_id=usuario_id, acao=acao,
        entidade=entidade, entidade_id=entidade_id,
        ip_origem=ip_origem,
    ))
    db.commit()

def refresh_access_token(db: Session, refresh_token_str: str) -> TokenResponse:
    """Valida o refresh token e emite um novo access token sem novo login."""
    import hashlib

    # Decodifica e valida o token
    payload = decodificar_token(refresh_token_str)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Refresh token invalido ou expirado."
        )

    # Verifica no banco se nao foi revogado
    token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
    rt = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revogado == False
    ).first()

    if not rt:
        raise HTTPException(
            status_code=401,
            detail="Refresh token invalido ou ja revogado."
        )

    # Busca o usuario
    usuario_id = payload.get("sub")
    usuario = usuario_repository.buscar_por_id(db, int(usuario_id))
    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=401,
            detail="Usuario nao encontrado ou desativado."
        )

    # Gera novo access token (mantem o mesmo refresh token)
    novo_access_token = criar_access_token({
        "sub": str(usuario.id),
        "perfil": usuario.perfil
    })

    _log(db, usuario.id, "TOKEN_RENOVADO", "usuario", usuario.id)

    return TokenResponse(
        access_token=novo_access_token,
        token_type="Bearer",
        expires_in=1800,
        refresh_token=refresh_token_str,
        perfil=usuario.perfil,
    )
