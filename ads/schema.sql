CREATE TABLE IF NOT EXISTS AppUser (
    id SERIAL,
    username VARCHAR(40) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS Prediction (
    id SERIAL,
    file_path TEXT,
    uploaded_on TIMESTAMP,
    status VARCHAR(60),
    user_session TEXT,
    result TEXT,
    result_confidence INT DEFAULT 0,
    PRIMARY KEY(id)
);
