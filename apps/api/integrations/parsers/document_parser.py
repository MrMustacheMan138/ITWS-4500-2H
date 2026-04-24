import {'LLM OF CHOICE'}

async def parse_and_structure(raw_text: str) -> dict:
   client = {'LLM METHOD'}
    
   prompt = f"""
You are analyzing a university program document.
Extract and organize the content into these sections (only include sections present):
- course_schedule: list of courses, credits, requirements
- rigor_indicators: workload signals, prerequisites, capstone requirements
- specialization_paths: tracks, concentrations, elective clusters
- learning_outcomes: stated skills and competencies
- faculty_research: research areas if mentioned
- accreditation: accrediting bodies, standards

Return ONLY valid JSON. If a section has insufficient content to analyze, 
set its value to null. If the document has less than 200 words of 
substantive content, return {{"insufficient": true, "reason": "..."}}.

Document:
{raw_text}
"""
   message = await client.messages.create(
      model="claude-opus-4-5",
      max_tokens=4096,
      messages=[{"role": "user", "content": prompt}]
   )
   return json.loads(message.content[0].text)