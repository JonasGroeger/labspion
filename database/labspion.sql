CREATE TABLE labspion (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  mac      TEXT NOT NULL,
  ipv4     TEXT NOT NULL,
  seen     INT  NOT NULL,
  hostname TEXT NOT NULL
);
