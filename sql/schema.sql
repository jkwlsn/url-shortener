DROP TABLE IF EXISTS links CASCADE;

-- Links table
CREATE TABLE IF NOT EXISTS links (
    link_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    slug text UNIQUE NOT NULL,
    long_url text UNIQUE NOT NULL
);
