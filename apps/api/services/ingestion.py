

async def process_document(source_id: str, raw_text: str, db) -> dict:
    
   # Step 1: Parse & structure
   structured = await parse_and_structure(raw_text)
    
   if structured.get("insufficient"):
      return {"status": "insufficient", "reason": structured["reason"]}
    
   # Step 2: Chunk, embed, store — per section
   all_section_results = []
    
   for section_label, section_text in structured.items():
      if not section_text:
         continue
        
      chunks = list(chunk_text(section_text))
      embeddings = await embed_chunks(chunks)
        
      # Store chunks + embeddings to vector DB
      await store_chunks(db, source_id, section_label, chunks, embeddings)
        
      # Step 3: Analyze section
      result = await analyze_section(section_label, chunks)
      all_section_results.append(result)
    
   # Step 4: Aggregate score
   score_report = compute_overall_score(all_section_results)
    
   # Persist the full analysis
   await store_analysis(db, source_id, all_section_results, score_report)
    
   return {
      "status": "complete",
      "section_analyses": all_section_results,
      "score_report": score_report
   }