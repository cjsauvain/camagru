CREATE TABLE IF NOT EXISTS users (
    id                  INTEGER PRIMARY KEY,
    username            TEXT    NOT NULL    UNIQUE,
    email               TEXT    NOT NULL    UNIQUE,
    password            TEXT    NOT NULL,
    is_confirmed        INTEGER NOT NULL    DEFAULT 0,
    confirm_token       TEXT,
    reset_token         TEXT,
    reset_expires_at    TEXT,
    notify_on_comment   INTEGER NOT NULL    DEFAULT 1,
    created_at          TEXT    NOT NULL    DEFAULT CURRENT_TIMESTAMP
) STRICT;

CREATE TABLE IF NOT EXISTS images (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename    TEXT    NOT NULL UNIQUE,
    created_at  TEXT    NOT NULL    DEFAULT CURRENT_TIMESTAMP
) STRICT;

CREATE TABLE IF NOT EXISTS comments (
    id          INTEGER PRIMARY KEY,
    image_id    INTEGER NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body        TEXT    NOT NULL,
    created_at  TEXT    NOT NULL    DEFAULT CURRENT_TIMESTAMP
) STRICT;

CREATE TABLE IF NOT EXISTS likes (
    image_id    INTEGER NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TEXT    NOT NULL    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (image_id, user_id)
) STRICT;

CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT    PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TEXT    NOT NULL    DEFAULT CURRENT_TIMESTAMP,
    expires_at  TEXT    NOT NULL
) STRICT;

CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at);
CREATE INDEX IF NOT EXISTS idx_comments_image_id ON comments(image_id);