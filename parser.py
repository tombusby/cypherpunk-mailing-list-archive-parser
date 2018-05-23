#!/usr/bin/env python
from email.parser import Parser
import re
import pprint
import sqlite3
import dateutil.parser


class EmailMessage(object):

    def __init__(self, file_year, raw_text):
        self.file_year = file_year
        self.raw_text = raw_text
        parsed_message = Parser().parsestr(raw_text)
        self.raw_date = parsed_message['Date']
        self.parsed_date = self.parse_date_info(self.raw_date)
        self.message_id = parsed_message['Message-ID'],
        self.date = parsed_message['From'],
        self.to = parsed_message['To'],
        self.subject = parsed_message['Subject'],
        self.reply_to = parsed_message['In-Reply-To']

    def parse_date_info(self, raw_date):
        tzinfos = {
            'EST': -18000,
            'EDT': -14400,
            'CST': -21600,
            'CDT': -18000,
            'MST': -25200,
            'MDT': -21600,
            'PST': -28800,
            'PPE': -28800,
            'PDT': -25200,
        }
        try:
            return dateutil.parser.parse(raw_date, tzinfos=tzinfos)
        except ValueError:
            found = re.search("SMTPSun, (.*) for karn", raw_date)
            if found is not None:
                return dateutil.parser.parse(found.group(1), tzinfos=tzinfos)
            else:
                return dateutil.parser.parse(raw_date.upper(), tzinfos=tzinfos)


def get_messages():
    stringbuffer = ""
    for n in range(1992, 1999):
        with open("cryptome/cyp-{}.txt".format(n)) as f:
            for line in f:
                if re.match("From cypherpunks\@MHonArc.venona", line):
                    if stringbuffer:
                        yield EmailMessage(n, stringbuffer)
                    stringbuffer = ""
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
        # insert_into_db(conn, message)
        pass
    # conn.close()


if __name__ == "__main__":
    main()
