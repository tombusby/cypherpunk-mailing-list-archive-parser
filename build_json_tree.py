#!/usr/bin/env python
import sqlite3
from datetime import datetime
import json


def get_message_rows(cursor):
    sql = "SELECT * FROM `messages` ORDER BY `date` ASC;"
    for row in cursor.execute(sql):
        yield row[1], row[3], row[4]


def populate_months(rows):
    months = {}
    for thread_root, file_year, date_timestamp in rows:
        if date_timestamp:
            date_obj = datetime.utcfromtimestamp(date_timestamp)
            year, month = date_obj.year, date_obj.month
        else:
            year, month = file_year, "unknown"
        if year not in months:
            months[year] = {}
        if month not in months[year]:
            months[year][month] = []
        if thread_root not in months[year][month]:
            months[year][month].append(thread_root)
    return months


def build_threads(conn, months):
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
    for year in months.keys():
        for month in months[year].keys():
            threads_in_month = []
            for thread_root in months[year][month]:
                sql = "SELECT * FROM `messages` WHERE `message_hash` = ?;"
                try:
                    cursor = conn.cursor()
                    cursor.execute(sql, [thread_root])
                    row = cursor.fetchone()
                    threads_in_month.append(make_dict(row))
                except sqlite3.IntegrityError:
                    print "sqlite3.IntegrityError", thread_root
                except sqlite3.ProgrammingError:
                    print "sqlite3.ProgrammingError", thread_root
            with open('json_months/{}/{}.json'.format(year, month), 'w') as f:
                f.write(json.dumps(threads_in_month))


def build_tree(make_dict, conn, message_id):
    sql = "SELECT * FROM `messages` WHERE `reply_to` = ? ORDER BY `date` ASC;"
    children = []
    cursor = conn.cursor()
    for row in cursor.execute(sql, [message_id]):
        children.append(make_dict(row))
    return children


def main():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    months = populate_months(get_message_rows(cursor))
    build_threads(conn, months)
    conn.close()


if __name__ == "__main__":
    main()
