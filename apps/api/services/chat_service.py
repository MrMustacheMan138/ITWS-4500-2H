from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from integrations.ai.client import chat_reply
from models import Chunk, Comparison, Program, Source
from services.ingestion import search_chunks

MAX_CONTEXT_CHARS = 12_000


async def load_context(
    db: AsyncSession,
    user_id: int,
    comparison_id: int | None = None,
    message: str = "",
) -> str:
    if comparison_id:
        result = await db.execute(
            select(Comparison).where(
                Comparison.id == comparison_id,
                Comparison.user_id == user_id,
            )
        )
        comparison = result.scalars().first()

        if comparison:
            program_ids = [
                pid
                for pid in [comparison.program_a_id, comparison.program_b_id]
                if pid is not None
            ]

            print("DEBUG comparison_id:", comparison_id)
            print("DEBUG program_ids:", program_ids)

            if program_ids:
                programs_result = await db.execute(
                    select(Program).where(
                        Program.user_id == user_id,
                        Program.id.in_(program_ids),
                    )
                )
                programs = {p.id: p for p in programs_result.scalars().all()}

                blocks: list[str] = []

                for idx, program_id in enumerate(program_ids):
                    program = programs.get(program_id)
                    label = "Program A" if idx == 0 else "Program B"
                    name = program.name if program else f"program_id={program_id}"
                    inst = (program.institution or "").strip() if program else ""
                    header = f"=== {label}: {name}{f' ({inst})' if inst else ''} ==="

                    if message:
                        # semantic search — find most relevant chunks for this query
                        chunks = await search_chunks(
                            query=message,
                            program_id=program_id,
                            db=db,
                            top_k=10,
                        )
                        print(f"DEBUG {label} program_id={program_id} semantic chunks:", len(chunks))
                    else:
                        # no message to embed — fall back to ordered load
                        chunk_result = await db.execute(
                            select(Chunk)
                            .join(Source, Chunk.source_id == Source.id)
                            .where(Source.user_id == user_id)
                            .where(Source.program_id == program_id)
                            .where(Source.status == "processed")
                            .order_by(Source.id, Chunk.chunk_index)
                        )
                        chunks = chunk_result.scalars().all()
                        print(f"DEBUG {label} program_id={program_id} ordered chunks:", len(chunks))

                    body = "\n\n".join(
                        f"[{chunk.section or 'unknown'}]\n{chunk.text}"
                        for chunk in chunks
                    )

                    blocks.append(f"{header}\n{body}")

                return "\n\n".join(blocks)[:MAX_CONTEXT_CHARS]

    # fallback — no comparison, load all user chunks
    result = await db.execute(
        select(Chunk)
        .join(Source, Chunk.source_id == Source.id)
        .where(Source.user_id == user_id)
        .where(Source.status == "processed")
        .order_by(Source.program_id, Source.id, Chunk.chunk_index)
    )
    chunks = result.scalars().all()

    print("DEBUG fallback chunks:", len(chunks))

    return "\n\n".join(
        f"[{chunk.section or 'unknown'}]\n{chunk.text}"
        for chunk in chunks
    )[:MAX_CONTEXT_CHARS]


async def chatbot(
    message: str,
    history: List[Dict[str, str]] | None = None,
    db: AsyncSession | None = None,
    user_id: int | None = None,
    comparison_id: int | None = None,
) -> str:
    context = ""

    if db is not None and user_id is not None:
        context = await load_context(
            db,
            user_id,
            comparison_id,
            message=message,
        )

    if not context.strip():
        context = "No curriculum context has been ingested yet."

    prompt = f"""
    You are an AI curriculum assistant.

    Use the curriculum context below to answer the user's question.
    If the user asks about schools not in the context say what schools you were given.
    Feel free to use existing knowledge to compare the 2 universities in the comparison but try your best to stick to the given data.

    Curriculum context:
    {context}

    User question:
    {message}
    """

    return await chat_reply(message=prompt, history=history)