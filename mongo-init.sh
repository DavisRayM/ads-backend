#!/bin/sh
set -e

mongosh -- "$MONGO_INITDB_DATABASE" <<EOF
db.createUser(
  {
    user: "$DB_USERNAME",
    pwd: "$DB_PASSWORD",
    roles: [ { role: "readWrite", db: "ads" } ]
  }
)
EOF
