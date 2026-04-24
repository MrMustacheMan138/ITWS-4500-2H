SECTION_PROMPTS = {
    "course_schedule": """
Analyze this course schedule for academic rigor. Consider:
- Total credit load and distribution
- Balance between theory and applied courses  
- Sequencing and prerequisite depth
- Presence of capstone, thesis, or research requirements

Return JSON: {
  "summary": "2-3 sentence overview",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "score": 0-10,
  "confidence": "high|medium|low",
  "missing_signals": ["what would improve this score if present"]
}
""",
    "rigor_indicators": """
Analyze these rigor signals. Consider:
- Prerequisite depth chains
- Presence of qualifying exams or milestones
- Research or thesis requirements
- Industry certifications or accreditation standards mentioned
...
"""
   # one per section type
}

async def analyze_section(section_label: str, chunks: list[str]) -> dict:
   combined_text = "\n\n".join(chunks)
    
   # Bail early if too sparse
   if len(combined_text.split()) < 50:
      return {
         "section": section_label,
         "insufficient": True,
         "reason": "Not enough content in this section to evaluate rigor."
      }
    
   prompt = SECTION_PROMPTS.get(section_label, DEFAULT_PROMPT)
   client = anthropic.AsyncAnthropic()
    
   message = await client.messages.create(
      model="claude-opus-4-5",
      max_tokens=1024,
      system="You are an academic program evaluator. Return only valid JSON.",
      messages=[{
         "role": "user", 
         "content": f"{prompt}\n\nContent:\n{combined_text}"
      }]
   )
   result = json.loads(message.content[0].text)
   result["section"] = section_label
   return result