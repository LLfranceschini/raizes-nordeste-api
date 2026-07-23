from passlib.context import CryptContext

# Contexto bcrypt para hash e verificacao de senhas
# bcrypt e o algoritmo recomendado: lento por design, resistente a brute-force
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha. Nunca armazene senha em texto puro."""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara a senha em texto puro com o hash armazenado."""
    return pwd_context.verify(senha, senha_hash)
