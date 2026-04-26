from models import ProgramAnalysis

@router.get("/{program_id}/analysis")
async def get_program_analysis(
    program_id: int,
    db: DbSession,
    current_user: CurrentUser
):
    # Verify program belongs to user
    result = await db.execute(
        select(Program).where(
            Program.id == program_id,
            Program.user_id == current_user.id
        )
    )
    program = result.scalars().first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    result = await db.execute(
        select(ProgramAnalysis).where(ProgramAnalysis.program_id == program_id)
    )
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found for this program")

    return {
        "program_id":      program_id,
        "program_name":    program.name,
        "institution":     program.institution,
        "status":          analysis.status,
        "overall_score":   analysis.overall_score,
        "orientation":     analysis.orientation,
        "overall_summary": analysis.overall_summary,
        "strengths":       analysis.strengths,
        "weaknesses":      analysis.weaknesses,
        "improvements":    analysis.improvements,
        "score_breakdown": analysis.score_breakdown,
        "analyzed_at":     analysis.analyzed_at,
    }