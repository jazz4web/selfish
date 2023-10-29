CREATE TABLE captchas (
    picture bytea      NOT NULL,
    val     varchar(5) UNIQUE,
    suffix  varchar(7) UNIQUE
);

CREATE TABLE permissions (
    permission varchar(32) NOT NULL,
    name       varchar(32),
    init       boolean     NOT NULL
);

CREATE TABLE users (
    id             serial        PRIMARY KEY,
    username       varchar(16)   UNIQUE NOT NULL,
    registered     timestamp,
    last_visit     timestamp,
    password_hash  varchar(128),
    permissions    varchar(32)[],
    sessions       varchar(13)[],
    description    varchar(500)  DEFAULT NULL,
    last_published timestamp     DEFAULT NULL
);

CREATE TABLE accounts (
    id        serial       PRIMARY KEY,
    address   varchar(128) UNIQUE,
    swap      varchar(128),
    requested timestamp,
    user_id   integer      REFERENCES users(id) UNIQUE
);

CREATE TABLE avatars (
    picture bytea   NOT NULL,
    user_id integer REFERENCES users(id) UNIQUE
);

CREATE TABLE friends (
    author_id integer REFERENCES users(id),
    friend_id integer REFERENCES users(id),
    CONSTRAINT author_friend_uni UNIQUE (author_id, friend_id)
);

CREATE TABLE followers (
    author_id   integer REFERENCES users(id),
    follower_id integer REFERENCES users(id),
    CONSTRAINT author_follower_uni UNIQUE (author_id, follower_id)
);

CREATE TABLE blockers (
    target_id  integer REFERENCES users(id),
    blocker_id integer REFERENCES users(id),
    CONSTRAINT target_blocker_uni UNIQUE (target_id, blocker_id)
);
