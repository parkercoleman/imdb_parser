CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE IF NOT EXISTS performances
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    title text,
    release_year date,
    performance_type integer,
    suspended boolean,
    "raw" text,
    CONSTRAINT performances_pkey PRIMARY KEY (id)
);

CREATE INDEX ON performances (title);
CREATE INDEX ON performances (release_year);
CREATE INDEX ON performances (performance_type);

CREATE TABLE IF NOT EXISTS tv_episodes
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    episode_name text,
    episode_date timestamp without time zone,
    episode_season integer,
    episode_number integer,
    episode_id_raw text,
    tv_show_id uuid,
    "raw" text,
    CONSTRAINT tv_episodes_pkey PRIMARY KEY (id)
);

CREATE INDEX ON tv_episodes (episode_number);
CREATE INDEX ON tv_episodes (episode_season);
CREATE INDEX ON tv_episodes (tv_show_id);

CREATE TABLE IF NOT EXISTS actors
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    first_name text,
    last_name text,
    gender varchar(6),
    CONSTRAINT actors_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS roles
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    performers_id uuid,
    performance_id uuid,
    character_name text,
    billing_position text,
    episode_id uuid,
    CONSTRAINT roles_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS directors
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    first_name text,
    last_name text,
    CONSTRAINT directors_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS director_to_performance
(
    director_uuid uuid NOT NULL,
    performance_uuid uuid,
    tv_show_uuid uuid
);

CREATE TABLE IF NOT EXISTS genres
(
  entity_id uuid NOT NULL, -- Can either be a performance or tv_episode uuid, since individual episodes can have genre information
  genre text NOT NULL,
  CONSTRAINT genres_pkey PRIMARY KEY (entity_id, genre)
);

CREATE TABLE IF NOT EXISTS ratings
(
  entity_id uuid NOT NULL,
  votes integer,
  rating double precision,
  CONSTRAINT ratings_pkey PRIMARY KEY (entity_id)
)


CREATE INDEX ON director_to_performance (director_uuid);
CREATE INDEX ON director_to_performance (performance_uuid);
CREATE INDEX ON director_to_performance (tv_show_uuid);
CREATE INDEX ON tv_episodes (raw);
CREATE INDEX ON performances (raw);