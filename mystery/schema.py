"""
Murder mystery database schema and seed data.
Mystery: "The Last Supper at Rosetti's"
"""

DDL_STATEMENTS = [
    """
    CREATE TABLE persons (
        person_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        occupation TEXT,
        relationship_to_victim TEXT,
        has_criminal_record INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE locations (
        location_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT,
        address TEXT
    )
    """,
    """
    CREATE TABLE events (
        event_id INTEGER PRIMARY KEY,
        person_id INTEGER REFERENCES persons(person_id),
        location_id INTEGER REFERENCES locations(location_id),
        event_time TEXT NOT NULL,
        description TEXT
    )
    """,
    """
    CREATE TABLE evidence (
        evidence_id INTEGER PRIMARY KEY,
        location_id INTEGER REFERENCES locations(location_id),
        type TEXT,
        description TEXT,
        found_at TEXT
    )
    """,
    """
    CREATE TABLE phone_records (
        record_id INTEGER PRIMARY KEY,
        caller_id INTEGER REFERENCES persons(person_id),
        receiver_id INTEGER REFERENCES persons(person_id),
        call_time TEXT NOT NULL,
        duration_minutes INTEGER,
        call_type TEXT
    )
    """,
    """
    CREATE TABLE financial_records (
        transaction_id INTEGER PRIMARY KEY,
        person_id INTEGER REFERENCES persons(person_id),
        amount REAL,
        transaction_type TEXT,
        description TEXT,
        transaction_date TEXT
    )
    """,
]

SEED_STATEMENTS = [
    # === PERSONS ===
    "INSERT INTO persons VALUES (1, 'Marco Rosetti', 'Restaurant Owner', 'victim', 0)",
    "INSERT INTO persons VALUES (2, 'Elena Rosetti', 'Art Dealer', 'wife', 0)",
    "INSERT INTO persons VALUES (3, 'Vincent Morrow', 'Business Partner', 'partner', 1)",
    "INSERT INTO persons VALUES (4, 'Sofia Chen', 'Head Chef', 'employee', 0)",
    "INSERT INTO persons VALUES (5, 'James Whitfield', 'Lawyer', 'friend', 0)",
    "INSERT INTO persons VALUES (6, 'Daniela Voss', 'Waitress', 'employee', 0)",

    # === LOCATIONS ===
    "INSERT INTO locations VALUES (1, 'Rosetti''s Restaurant', 'restaurant', '42 Vine Street')",
    "INSERT INTO locations VALUES (2, 'Private Dining Room', 'dining_room', '42 Vine Street (upstairs)')",
    "INSERT INTO locations VALUES (3, 'Kitchen', 'kitchen', '42 Vine Street (back)')",
    "INSERT INTO locations VALUES (4, 'Elena''s Gallery', 'gallery', '118 Park Avenue')",
    "INSERT INTO locations VALUES (5, 'Morrow''s Office', 'office', '55 Commerce Blvd')",
    "INSERT INTO locations VALUES (6, 'City Park', 'park', 'Central District')",

    # === EVENTS (timeline of the evening, March 15, 2024) ===
    # Early evening setup
    "INSERT INTO events VALUES (1, 1, 1, '2024-03-15 19:00', 'Marco arrives at the restaurant and opens up for the evening')",
    "INSERT INTO events VALUES (2, 4, 3, '2024-03-15 19:15', 'Sofia begins dinner preparations in the kitchen')",
    "INSERT INTO events VALUES (3, 6, 1, '2024-03-15 19:30', 'Daniela arrives for her shift and starts setting up tables')",

    # Guests arrive
    "INSERT INTO events VALUES (4, 2, 1, '2024-03-15 20:00', 'Elena arrives at the restaurant')",
    "INSERT INTO events VALUES (5, 3, 1, '2024-03-15 20:15', 'Vincent arrives looking agitated')",
    "INSERT INTO events VALUES (6, 5, 1, '2024-03-15 20:30', 'James Whitfield arrives with a briefcase')",

    # Dinner service
    "INSERT INTO events VALUES (7, 6, 1, '2024-03-15 20:45', 'Daniela serves drinks to the guests in the main dining area')",
    "INSERT INTO events VALUES (8, 1, 2, '2024-03-15 21:00', 'Marco leads the group to the private dining room')",
    "INSERT INTO events VALUES (9, 2, 2, '2024-03-15 21:00', 'Elena follows Marco to the private dining room')",
    "INSERT INTO events VALUES (10, 3, 2, '2024-03-15 21:00', 'Vincent moves to the private dining room')",
    "INSERT INTO events VALUES (11, 5, 2, '2024-03-15 21:00', 'James joins the group in the private dining room')",

    # Sofia enters private dining room
    "INSERT INTO events VALUES (12, 4, 2, '2024-03-15 21:15', 'Sofia brings the first course to the private dining room')",
    "INSERT INTO events VALUES (13, 4, 3, '2024-03-15 21:25', 'Sofia returns to the kitchen')",

    # The poisoned wine
    "INSERT INTO events VALUES (14, 4, 2, '2024-03-15 21:45', 'Sofia brings a special bottle of wine to the private dining room')",
    "INSERT INTO events VALUES (15, 4, 3, '2024-03-15 21:55', 'Sofia returns to the kitchen after serving wine')",

    # Elena leaves
    "INSERT INTO events VALUES (16, 2, 1, '2024-03-15 22:00', 'Elena leaves the restaurant claiming she needs to check on a gallery delivery')",

    # The last call
    "INSERT INTO events VALUES (17, 1, 2, '2024-03-15 22:15', 'Marco steps out briefly to make a phone call')",
    "INSERT INTO events VALUES (18, 4, 3, '2024-03-15 22:20', 'Sofia is seen in the kitchen looking visibly upset after a phone call')",

    # The gap - Sofia unaccounted for
    "INSERT INTO events VALUES (19, 6, 1, '2024-03-15 22:30', 'Daniela notices Sofia is not in the kitchen and wonders where she went')",

    # The collapse
    "INSERT INTO events VALUES (20, 1, 2, '2024-03-15 22:45', 'Marco collapses at the table in the private dining room')",
    "INSERT INTO events VALUES (21, 3, 2, '2024-03-15 22:46', 'Vincent rushes to Marco''s side and calls for help')",
    "INSERT INTO events VALUES (22, 5, 2, '2024-03-15 22:47', 'James calls emergency services from the private dining room')",
    "INSERT INTO events VALUES (23, 4, 3, '2024-03-15 22:50', 'Sofia reappears in the kitchen claiming she was in the storage room')",
    "INSERT INTO events VALUES (24, 6, 1, '2024-03-15 23:00', 'Daniela lets the paramedics into the restaurant')",

    # === EVIDENCE ===
    "INSERT INTO evidence VALUES (1, 3, 'physical', 'Small glass vial with chemical residue found in kitchen trash', '2024-03-15 23:30')",
    "INSERT INTO evidence VALUES (2, 2, 'physical', 'Fingerprints on the wine bottle match Sofia Chen', '2024-03-16 02:00')",
    "INSERT INTO evidence VALUES (3, 2, 'digital', 'Security camera shows Sofia entering private dining room at 21:45 carrying a wine bottle', '2024-03-16 01:00')",
    "INSERT INTO evidence VALUES (4, 1, 'testimonial', 'Daniela states Sofia appeared extremely upset and distracted after 22:15', '2024-03-16 00:30')",
    "INSERT INTO evidence VALUES (5, 2, 'physical', 'Chemical analysis of remaining wine shows traces of potassium cyanide', '2024-03-16 10:00')",
    "INSERT INTO evidence VALUES (6, 2, 'physical', 'Marco''s notebook found on table with notes reading: Rebrand plan - close kitchen, bring in catering partner', '2024-03-16 00:15')",

    # === PHONE RECORDS ===
    "INSERT INTO phone_records VALUES (1, 3, 1, '2024-03-15 14:00', 15, 'incoming')",
    "INSERT INTO phone_records VALUES (2, 1, 3, '2024-03-15 16:30', 8, 'outgoing')",
    "INSERT INTO phone_records VALUES (3, 2, 5, '2024-03-15 18:00', 5, 'outgoing')",
    "INSERT INTO phone_records VALUES (4, 1, 4, '2024-03-15 22:15', 8, 'outgoing')",
    "INSERT INTO phone_records VALUES (5, 2, 5, '2024-03-15 22:05', 3, 'outgoing')",
    "INSERT INTO phone_records VALUES (6, 4, 1, '2024-03-15 22:25', 2, 'incoming')",
    "INSERT INTO phone_records VALUES (7, 3, 1, '2024-03-15 17:00', 12, 'incoming')",
    "INSERT INTO phone_records VALUES (8, 4, NULL, '2024-03-15 23:30', 6, 'outgoing')",

    # === FINANCIAL RECORDS ===
    "INSERT INTO financial_records VALUES (1, 4, 487.50, 'withdrawal', 'Kitchen supplies - ChemDirect Inc.', '2024-03-10')",
    "INSERT INTO financial_records VALUES (2, 3, 50000.00, 'transfer', 'Investment payment to Rosetti restaurant fund', '2024-03-01')",
    "INSERT INTO financial_records VALUES (3, 2, 12000.00, 'deposit', 'Gallery commission - Sinclair collection sale', '2024-03-05')",
    "INSERT INTO financial_records VALUES (4, 1, 8500.00, 'withdrawal', 'Restaurant equipment upgrade', '2024-03-08')",
    "INSERT INTO financial_records VALUES (5, 4, 3200.00, 'deposit', 'Monthly salary deposit', '2024-03-01')",
    "INSERT INTO financial_records VALUES (6, 6, 1800.00, 'deposit', 'Monthly salary deposit', '2024-03-01')",
    "INSERT INTO financial_records VALUES (7, 2, 4500.00, 'withdrawal', 'Art acquisition - private collection', '2024-03-12')",
    "INSERT INTO financial_records VALUES (8, 1, 15000.00, 'deposit', 'Restaurant revenue deposit', '2024-03-14')",
    "INSERT INTO financial_records VALUES (9, 3, 2200.00, 'withdrawal', 'Office lease payment', '2024-03-01')",
    "INSERT INTO financial_records VALUES (10, 5, 5000.00, 'deposit', 'Legal consultation fee from Rosetti', '2024-03-13')",
]
