CREATE TABLE IF NOT EXISTS AppUser (
    id SERIAL,
    username VARCHAR(40) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS Result (
    id SERIAL,
    start_time TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    content TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS Prediction (
    id SERIAL,
    file_path TEXT,
    uploaded_on TIMESTAMP,
    status VARCHAR(60),
    result_id INT,
    user_id INT,
    PRIMARY KEY(id),
    FOREIGN KEY (user_id) REFERENCES AppUser(id),
    FOREIGN KEY (result_id) REFERENCES Result(id)
);
