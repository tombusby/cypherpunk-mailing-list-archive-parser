#!/usr/bin/env python
import sqlite3
import json


def get_authors(conn):
    cursor = conn.cursor()
    sql = """
        SELECT
            `sender_id`,
            `from`,
            count(*) AS `messages`
        FROM
            `messages`
        GROUP BY
            `sender_id`
        ORDER BY
            `messages` DESC;
    """
    for row in cursor.execute(sql):
        yield row[0], row[1].encode('utf-8'), row[2]


def make_thread(conn, thread_root):
    def make_dict(row):
        return {
            'message_hash': row[0],
            'message_id': row[2],
            'file_year': row[3],
            'date': row[4],
            'raw_date': row[5],
            'from': row[7],
            'to': row[8],
            'subject': row[9],
            'reply_to': row[10],
            'no_parent': row[11],
            'children': build_tree(make_dict, conn, row[2])
        }
    sql = "SELECT * FROM `messages` WHERE `message_hash` = ?;"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, [thread_root])
        row = cursor.fetchone()
        return make_dict(row)
    except sqlite3.IntegrityError:
        print "sqlite3.IntegrityError", thread_root
        return None
    except sqlite3.ProgrammingError:
        print "sqlite3.ProgrammingError", thread_root
        return None


def build_tree(make_dict, conn, message_id):
    sql = "SELECT * FROM `messages` WHERE `reply_to` = ? ORDER BY `date` ASC;"
    children = []
    for row in conn.cursor().execute(sql, [message_id]):
        children.append(make_dict(row))
    return children


def make_threads(conn, sender_id):
    sql = """
        SELECT DISTINCT
            `thread_root`
        FROM
            `messages`
        WHERE
            `sender_id` = ?
        ORDER BY
            `date` ASC
    """
    threads = []
    for row in conn.cursor().execute(sql, [sender_id]):
        threads.append(make_thread(conn, row[0]))
    return threads


def main():
    conn = sqlite3.connect('database.db')
    for sender_id, from_email, count in get_authors(conn):
        with open('json_authors/{}.json'.format(sender_id), 'w') as o:
            print sender_id, count
            o.write(json.dumps({
                'sender_id': sender_id,
                'from': from_email,
                'count': count,
                'threads': make_threads(conn, sender_id)
            }))


if __name__ == "__main__":
    main()
