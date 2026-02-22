This is a really fun idea — murder mystery + SQL is a great hook for learning. Let me break down how I'd think about building this.
Core Concept
A detective noir SQL learning game where the student is the detective. They solve a murder mystery by querying a database of suspects, alibis, evidence logs, and witness statements. The story unfolds based on what they query — wrong or incomplete SQL means they miss clues.

The Agent Architecture
Agent 1 — The Storyteller
This agent holds the narrative state. It knows the full mystery plot, which clues exist, and what should be revealed at each step. It takes the student's SQL result and narrates what the detective "discovers" — keeping it immersive and dramatic. It also decides when the story should progress or stall based on what was found.
Agent 2 — The DB Architect
This agent designs the schema that fits the story. Think tables like suspects, alibis, evidence, locations, witness_statements, phone_logs. It ensures every table has a narrative purpose — no arbitrary schema. It also generates seed data that is internally consistent with the mystery.
Agent 3 — Your SQL Evaluator (already built)
This is the judge. It takes the student's query, runs it, compares the result against what the "correct" investigative path would have uncovered, and scores it. Since multiple queries can reach the same conclusion, this is where your AI evaluator shines — checking intent and result correctness rather than exact syntax.

The Story Scraping Pipeline
You scrape short mystery stories (Project Gutenberg, fan fiction sites, or mystery writing communities), then pass them to the DB Architect agent which:

Extracts entities — characters, locations, times, relationships
Designs a normalized schema from those entities
Seeds the database with facts from the story
Flags which facts are "hidden" (require a JOIN or subquery to uncover) vs surface-level

This way you get 10-15 distinct mysteries with minimal manual work.

The Game Loop (10 messages max)
Turn 1-2:  Scene setting — Storyteller introduces the crime, 
           the student gets the schema ERD

Turn 3-6:  Active investigation — student writes queries, 
           Storyteller narrates discoveries dramatically, 
           Evaluator silently scores and tracks progress

Turn 7-9:  Closing in — Storyteller drops hints if student 
           is stuck, student must write the "accusation query"

Turn 10:   Resolution — Evaluator confirms if they got the 
           right suspect, Storyteller delivers the final reveal
The 10-message constraint is actually great for pedagogy — it forces students to think before querying, like a real investigator.

SQL Concepts You Can Embed Naturally
Each mystery can be designed to require specific SQL skills to solve. A beginner mystery only needs WHERE and SELECT. Intermediate needs JOINs across alibi and suspect tables. Advanced needs window functions (finding the last person to call the victim), CTEs (tracing a chain of contacts), or subqueries (suspects who were at two locations). The DB Architect agent can tune this difficulty intentionally.

What to Build First
Start with a hardcoded single mystery to validate the loop. Get the Storyteller and Evaluator talking to each other with a fixed schema, then layer in the scraping pipeline once the core experience feels right. The scraper is the riskiest part — story-to-schema conversion will need a lot of prompt iteration.
The fact that you already have an AI SQL evaluator is a huge head start. That's honestly the hardest piece to build well. Sonnet 4.6Extended