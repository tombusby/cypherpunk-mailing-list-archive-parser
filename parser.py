#!/usr/bin/env python
from email.parser import Parser
import re
import pprint
import sqlite3
import dateutil.parser


def get_messages():
    stringbuffer = ""
    for n in range(2, 9):
        with open("cryptome/cyp-199{}.txt".format(n)) as f:
            i = 0
            for line in f:
                if re.match("From cypherpunks\@MHonArc.venona", line):
                    if stringbuffer:
                        yield Parser().parsestr(stringbuffer)
                    stringbuffer = ""
                    i += 1
                else:
                    stringbuffer += line


def insert_into_db(conn, message):
    sql = """
        INSERT INTO messages (
            `message_id`,
            `date`,
            `from`,
            `to`,
            `subject`,
            `reply_to`
        ) VALUES (
            ?, ?, ?, ?, ?, ?
        )
    """
    conn.cursor().execute(sql, (
        message['Message-ID'],
        1526932747,
        message['From'],
        message['To'],
        message['Subject'],
        message['In-Reply-To']
    ))
    conn.commit()


def main():
    # conn = sqlite3.connect('database.db')
    for message in get_messages():
        # pprint.pprint(message.items())
        # insert_into_db(conn, message)
        parsed_date = dateutil.parser.parse(message['Date'])
        pprint.pprint(parsed_date.tzname())
    # conn.close()


if __name__ == "__main__":
    main()
