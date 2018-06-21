#!/usr/bin/env python
import sqlite3
import re


def get_authors(cursor):
    sql = "SELECT `message_hash`, `from` FROM `messages`;"
    for row in cursor.execute(sql):
        yield row[0], row[1].encode('utf-8')


def set_sender_id(conn, message_hash, sender_id):
    cursor = conn.cursor()
    sql = "UPDATE `messages` SET `sender_id` = ? WHERE `message_hash` = ?;"
    cursor.execute(sql, [sender_id, message_hash])


def make_id_from_email(email):
    email = email.replace('@', '_at_')
    email = re.sub('[<>\(\)\.\s]+', '_', email)
    email = re.sub('\W+', '', email)
    return email.lower()


def main():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    for message_hash, email in get_authors(cursor):
        set_sender_id(conn, message_hash, make_id_from_email(email))
    conn.commit()


if __name__ == "__main__":
    main()
