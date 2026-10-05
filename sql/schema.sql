CREATE TABLE IF NOT EXISTS fact_inventory (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    month DATE NOT NULL,
    year INTEGER NOT NULL,
    part_id VARCHAR(20) NOT NULL,
    part_class VARCHAR(40),
    ata_chapter INTEGER,
    aircraft_type VARCHAR(20),
    location VARCHAR(40) NOT NULL,
    demand INTEGER NOT NULL CHECK (demand >= 0),
    issues INTEGER NOT NULL CHECK (issues >= 0),
    opening_inventory INTEGER NOT NULL CHECK (opening_inventory >= 0),
    inventory INTEGER NOT NULL CHECK (inventory >= 0),
    stockout INTEGER NOT NULL CHECK (stockout IN (0, 1)),
    flight_cycle INTEGER NOT NULL CHECK (flight_cycle >= 0),
    lead_time INTEGER NOT NULL CHECK (lead_time >= 0),
    UNIQUE (date, part_id, location)
);

CREATE INDEX IF NOT EXISTS idx_fact_inventory_date ON fact_inventory (date);
CREATE INDEX IF NOT EXISTS idx_fact_inventory_part ON fact_inventory (part_id);
CREATE INDEX IF NOT EXISTS idx_fact_inventory_location ON fact_inventory (location);
CREATE INDEX IF NOT EXISTS idx_fact_inventory_stockout ON fact_inventory (stockout);
