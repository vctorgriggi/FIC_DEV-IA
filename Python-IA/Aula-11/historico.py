# historico.py

from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Session

# ─── Configuração ────────────────────────────────────────────
engine = create_engine("sqlite:///pipeline.db", echo=False)


class Base(DeclarativeBase):
    pass


# ─── Modelo ──────────────────────────────────────────────────
class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    origem = Column(String(50), nullable=False)
    tipo = Column(String(20), nullable=False)  # pdf, docx, txt
    status = Column(String(20), nullable=False, default="pendente")
    num_tokens = Column(Integer, nullable=True)
    score_ia = Column(Float, nullable=True)
    observacao = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.now)
    processado_em = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Documento id={self.id} nome={self.nome!r} status={self.status!r}>"


# Resetar banco para evitar esquema antigo da aula em execuções anteriores
if os.path.exists("pipeline.db"):
    os.remove("pipeline.db")

# Criar tabela (idempotente)
Base.metadata.create_all(engine)


# ─── Funções de domínio ──────────────────────────────────────
def cadastrar(
    nome: str, origem: str, tipo: str, num_tokens: int | None = None
) -> Documento:
    """Cadastra um novo documento com status 'pendente'."""
    with Session(engine) as session:
        doc = Documento(
            nome=nome,
            origem=origem,
            tipo=tipo,
            num_tokens=num_tokens,
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc


def processar(doc_id: int, score: float, obs: str | None = None) -> bool:
    """Marca documento como processado e registra score e timestamp."""
    with Session(engine) as session:
        doc = session.get(Documento, doc_id)
        if not doc:
            return False

        doc.status = "processado"
        doc.score_ia = score
        doc.observacao = obs
        doc.processado_em = datetime.now()
        session.commit()
        return True


def marcar_erro(doc_id: int, motivo: str) -> bool:
    """Marca documento como 'erro' e registra o motivo."""
    with Session(engine) as session:
        doc = session.get(Documento, doc_id)
        if not doc:
            return False

        doc.status = "erro"
        doc.observacao = motivo
        session.commit()
        return True


def buscar_por_status(status: str) -> list[Documento]:
    """Retorna todos os documentos com o status informado."""
    with Session(engine) as session:
        return (
            session.query(Documento)
            .filter(Documento.status == status)
            .order_by(Documento.criado_em.desc())
            .all()
        )


def historico_completo() -> list[Documento]:
    """Retorna todos os documentos em ordem cronológica inversa."""
    with Session(engine) as session:
        return session.query(Documento).order_by(Documento.criado_em.desc()).all()


def resumo_por_status() -> dict[str, int]:
    """Retorna contagem de documentos agrupados por status."""
    with Session(engine) as session:
        resultados = (
            session.query(Documento.status, func.count(Documento.id))
            .group_by(Documento.status)
            .all()
        )
    return dict(resultados)


def top_por_score(n: int = 3) -> list[Documento]:
    """Retorna os N documentos com maior score_ia."""
    with Session(engine) as session:
        return (
            session.query(Documento)
            .filter(Documento.score_ia.isnot(None))
            .order_by(Documento.score_ia.desc())
            .limit(n)
            .all()
        )


# ─── Simulação do pipeline ───────────────────────────────────
def main() -> None:
    sep = "=" * 55

    print(f"\n{sep}")
    print(" PIPELINE DE DOCUMENTOS — SIMULAÇÃO")
    print(sep)

    # 1. Cadastrar documentos
    print("\n[1] Cadastrando documentos...")
    lote = [
        ("relatorio_q1.pdf", "upload", "pdf", 1842),
        ("contrato_2024.pdf", "email", "pdf", 950),
        ("ata_reuniao.docx", "drive", "docx", 420),
        ("proposta_tecnica.pdf", "upload", "pdf", 2100),
        ("resumo_exec.txt", "api", "txt", 310),
        ("laudo_medico.pdf", "upload", "pdf", 3200),
        ("newsletter.txt", "email", "txt", 180),
        ("manual_usuario.pdf", "drive", "pdf", 5500),
    ]
    ids: list[int] = []
    for nome, origem, tipo, tokens in lote:
        doc = cadastrar(nome, origem, tipo, tokens)
        ids.append(doc.id)
        print(f" + #{doc.id:02d} {doc.nome}")

    # 2. Processar alguns documentos
    print("\n[2] Processando...")
    scores = [
        (ids[0], 0.92),
        (ids[1], 0.78),
        (ids[2], 0.85),
        (ids[4], 0.67),
        (ids[5], 0.95),
        (ids[6], 0.41),
    ]
    for doc_id, score in scores:
        processar(doc_id, score)
        print(f" ✓ #{doc_id:02d} processado — score: {score}")

    # 3. Marcar erros
    print("\n[3] Registrando erros...")
    marcar_erro(ids[3], "Arquivo corrompido — não foi possível extrair texto")
    print(f" ✗ #{ids[3]:02d} marcado como erro")

    # ── Consultas analíticas ──────────────────────────────────
    print(f"\n{sep}")
    print(" HISTÓRICO E CONSULTAS")
    print(sep)

    # 4. Resumo por status
    print("\n[4] Resumo por status:")
    for status, total in sorted(resumo_por_status().items()):
        print(f" {status:<12}: {total} documento(s)")

    # 5. Documentos pendentes
    pendentes = buscar_por_status("pendente")
    print(f"\n[5] Pendentes ({len(pendentes)}):")
    for doc in pendentes:
        print(f" #{doc.id:02d} {doc.nome:<30} {doc.num_tokens:>5} tokens")

    # 6. Top 3 por score
    print("\n[6] Top 3 por score IA:")
    for i, doc in enumerate(top_por_score(3), 1):
        print(f" {i}. {doc.nome:<30} score: {doc.score_ia:.2f}")

    # 7. Documentos com erro
    erros = buscar_por_status("erro")
    print(f"\n[7] Erros ({len(erros)}):")
    for doc in erros:
        print(f" #{doc.id:02d} {doc.nome}")
        print(f" Motivo: {doc.observacao}")

    # 8. Histórico completo com SQL direto
    print("\n[8] Histórico completo (SQL direto):")
    with engine.connect() as conn:
        resultado = conn.execute(
            text(
                "SELECT id, nome, status, score_ia, num_tokens FROM documentos ORDER BY id"
            )
        )

        print(f" {'ID':<4} {'NOME':<30} {'STATUS':<12} {'SCORE':>6} {'TOKENS':>7}")
        print(f" {'-' * 4} {'-' * 30} {'-' * 12} {'-' * 6} {'-' * 7}")
        for row in resultado:
            score = f"{row.score_ia:.2f}" if row.score_ia is not None else " — "
            print(
                f" {row.id:<4} {row.nome:<30} {row.status:<12} {score:>6} {row.num_tokens or 0:>7}"
            )

    print(f"\n{sep}")
    print(" Banco salvo em: pipeline.db")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
