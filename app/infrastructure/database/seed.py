"""
Popula o banco com dados iniciais para testar a API.
Execute: python -m app.infrastructure.database.seed
"""
from app.infrastructure.database.connection import SessionLocal
from app.domain.models.unidade import Unidade
from app.domain.models.produto import Produto
from app.domain.models.usuario import Usuario
from app.domain.models.cardapio_unidade import CardapioUnidade
from app.domain.models.estoque import Estoque
from app.infrastructure.security.password_handler import hash_senha


def seed():
    db = SessionLocal()
    try:
        if db.query(Usuario).first():
            print("Banco ja populado. Abortando.")
            return

        print("Populando banco de dados...")

        # Unidades
        u1 = Unidade(nome="Raizes Recife Centro", logradouro="Rua do Bom Jesus",
                     numero="100", bairro="Recife Antigo", cidade="Recife",
                     estado="PE", cep="50030170", tipo="COMPLETA")
        u2 = Unidade(nome="Raizes Fortaleza", logradouro="Av. Beira Mar",
                     numero="200", bairro="Meireles", cidade="Fortaleza",
                     estado="CE", cep="60165121", tipo="COMPLETA")
        db.add_all([u1, u2])
        db.flush()

        # Usuarios
        admin = Usuario(nome="Admin Sistema", email="admin@raizesnordeste.com.br",
                        senha_hash=hash_senha("Admin@123"), perfil="ADMIN")
        gerente = Usuario(nome="Gerente Recife", email="gerente@raizesnordeste.com.br",
                          senha_hash=hash_senha("Gerente@123"), perfil="GERENTE",
                          unidade_id=u1.id)
        cliente = Usuario(nome="Maria Silva", email="maria@email.com",
                          senha_hash=hash_senha("Cliente@123"), perfil="CLIENTE",
                          cpf="12345678901")
        db.add_all([admin, gerente, cliente])
        db.flush()

        # Produtos
        produtos = [
            Produto(nome="Tapioca Nordestina", preco_base=12.90, categoria="Salgado"),
            Produto(nome="Cuscuz Recheado",    preco_base=9.90,  categoria="Salgado"),
            Produto(nome="Bolo de Macaxeira",  preco_base=7.90,  categoria="Doce"),
            Produto(nome="Suco de Caja",       preco_base=6.90,  categoria="Bebida"),
            Produto(nome="Cafe Passado",        preco_base=4.90,  categoria="Bebida"),
        ]
        db.add_all(produtos)
        db.flush()

        # Cardapio e estoque - unidade 1 (todos os produtos)
        for p in produtos:
            db.add(CardapioUnidade(unidade_id=u1.id, produto_id=p.id, disponivel=True))
            db.add(Estoque(unidade_id=u1.id, produto_id=p.id, quantidade=50, qtd_minima=5))

        # Cardapio e estoque - unidade 2 (sem bolo de macaxeira)
        for p in [produtos[0], produtos[1], produtos[3], produtos[4]]:
            db.add(CardapioUnidade(unidade_id=u2.id, produto_id=p.id, disponivel=True))
            db.add(Estoque(unidade_id=u2.id, produto_id=p.id, quantidade=30, qtd_minima=5))

        db.commit()
        print("\nSeed concluido! Usuarios criados:")
        print("  admin@raizesnordeste.com.br   / Admin@123    (ADMIN)")
        print("  gerente@raizesnordeste.com.br / Gerente@123  (GERENTE)")
        print("  maria@email.com               / Cliente@123  (CLIENTE)")

    except Exception as e:
        db.rollback()
        print(f"Erro no seed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
