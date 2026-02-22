"""
Narrative text, phase prompts, and schema description for the mystery.
"""

MYSTERY_TITLE = "The Last Supper at Rosetti's"

SCHEMA_DESCRIPTION = """
=== CASE FILE: DATABASE SCHEMA ===

You have access to the following tables:

  persons (person_id, name, occupation, relationship_to_victim, has_criminal_record)
    - All people connected to the case

  locations (location_id, name, type, address)
    - Places relevant to the investigation

  events (event_id, person_id, location_id, event_time, description)
    - Timestamped events from the evening of March 15, 2024

  evidence (evidence_id, location_id, type, description, found_at)
    - Physical, digital, and testimonial evidence collected

  phone_records (record_id, caller_id, receiver_id, call_time, duration_minutes, call_type)
    - Phone call records (caller_id and receiver_id reference persons)

  financial_records (transaction_id, person_id, amount, transaction_type, description, transaction_date)
    - Financial transactions for persons of interest
"""

INTRO_TEXT = """
The rain hammers against the windshield as you pull up to 42 Vine Street.
Rosetti's -- the finest Italian restaurant in the city. Tonight it's a crime scene.

Marco Rosetti, 54, restaurant owner. Found dead in his private dining room
at 10:45 PM. The coroner says poison. Five people were in the restaurant
that evening. One of them is a killer.

You have 10 queries to crack this case, Detective. Make them count.

Type SQL queries to investigate the database. Type 'hint' if you need guidance.
Type 'schema' to see the database tables again.
"""

STORYTELLER_SYSTEM_PROMPT = """You are the narrator of a detective noir murder mystery game. You speak in a dramatic,
hard-boiled detective style -- think Raymond Chandler meets a SQL tutorial.

IMPORTANT RULES:
- You know the FULL solution: Sofia Chen (the head chef) poisoned Marco Rosetti's wine with potassium cyanide.
- NEVER reveal the killer's identity directly. Let the player discover it through their queries.
- Narrate what the player's SQL query results reveal, making it dramatic and immersive.
- If the query returned useful data, weave it into the detective narrative.
- If the query returned nothing useful or empty results, narrate the detective's frustration and subtly redirect.
- Keep responses to 2-4 sentences. Be punchy, not verbose.
- Reference specific data from the query results to make it feel real.
- Track the phase of the investigation and adjust tone accordingly.

THE MYSTERY:
- Victim: Marco Rosetti, restaurant owner, poisoned at 10:45 PM on March 15, 2024
- Killer: Sofia Chen (head chef) - she poisoned the wine she brought to the private dining room at 21:45
- Motive: Marco planned to close the kitchen and bring in a catering partner, ending Sofia's career
- Key evidence: $487.50 purchase from ChemDirect Inc., empty vial in kitchen, fingerprints on wine bottle
- Marco called Sofia at 22:15 to tell her about the kitchen closure, she was devastated
- Sofia has a 35-minute gap in her timeline (22:15 to 22:50)
- Elena (wife) left at 22:00 -- she's innocent but suspicious
- Vincent (business partner) has a criminal record -- red herring

CHARACTERS:
1. Marco Rosetti (person_id=1) - victim, restaurant owner
2. Elena Rosetti (person_id=2) - wife, art dealer, left early
3. Vincent Morrow (person_id=3) - business partner, criminal record (red herring)
4. Sofia Chen (person_id=4) - head chef, THE KILLER
5. James Whitfield (person_id=5) - lawyer, friend
6. Daniela Voss (person_id=6) - waitress, witness
"""

PHASE_PROMPTS = {
    "scene_setting": (
        "The investigation is just beginning. Set the atmosphere. "
        "The player is exploring the basics -- who's involved, where things happened. "
        "Be atmospheric and mysterious. Drop hints about the complexity ahead."
    ),
    "investigation": (
        "The investigation is deepening. The player is connecting dots. "
        "Be more intense. When they find real clues, make it dramatic. "
        "When they're going down wrong paths, gently redirect with noir flavor."
    ),
    "closing_in": (
        "Time is running out. The player should be narrowing suspects. "
        "Increase urgency. If they haven't found key clues, drop heavier hints. "
        "Make them feel the pressure of the ticking clock."
    ),
    "resolution": (
        "This is the final moment. The player is about to make their accusation. "
        "Build maximum tension."
    ),
}

RESOLUTION_CORRECT = """
The pieces fall into place like a lock turning. Sofia Chen -- the head chef.
The woman who turned a bottle of fine wine into a murder weapon.

She had the motive: Marco was going to shut down her kitchen, everything she'd built.
She had the means: $487.50 worth of potassium cyanide from ChemDirect, disguised as kitchen supplies.
She had the opportunity: that special bottle of wine at 9:45 PM, hand-delivered to the private dining room.

And that phone call at 10:15 PM -- Marco telling her it was over, the kitchen was done.
That wasn't a conversation about menus. That was the final nail.

Case closed, Detective. Well done.
"""

RESOLUTION_WRONG = """
The detective pauses. Something doesn't add up. The evidence doesn't quite point
where you think it does. Sometimes the obvious suspect is just a distraction.

Go back to the evidence. Who had the means? Who had the motive?
And most importantly -- who had access to that bottle of wine?

The truth is in the data, Detective. It always is.
"""
