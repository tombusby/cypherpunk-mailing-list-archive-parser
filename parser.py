#!/usr/bin/env python
from email.parser import Parser
import re
import pprint
import sqlite3
import dateutil.parser


class EmailMessage(object):

    def __init__(self, file_year, raw_text):
        self._file_year = int(file_year)
        self._raw_text = raw_text
        parsed_message = Parser().parsestr(raw_text)
        self._raw_date = parsed_message['Date']
        self._parsed_date = self._parse_date_info(self._raw_date)
        self._unixtime = self._get_unixtime_from_parsed(self._parsed_date)
        self._message_id = parsed_message['Message-ID']
        self._from = parsed_message['From']
        self._to = parsed_message['To']
        self._subject = parsed_message['Subject']
        self._reply_to = parsed_message['In-Reply-To']

    def _parse_date_info(self, raw_date):
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

    def _get_unixtime_from_parsed(self, parsed_date):
        # Don't judge me
        try:
            tzoffset = parsed_date.utcoffset().total_seconds()
        except AttributeError:
            tzoffset = 0
        offset_1970 = parsed_date.strftime("%s")
        # Times are an hour out, don't know why, added an hour to compensate
        return (60 * 60) + int(offset_1970) - int(tzoffset)


def get_messages():
    stringbuffer = ""
    for n in range(1992, 1999):
        print n
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
            `file_year`,
            `date`,
            `raw_date`,
            `from`,
            `to`,
            `subject`,
            `reply_to`
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?
        )
    """
    conn.cursor().execute(sql, [
        message._message_id,
        message._file_year,
        message._unixtime,
        message._raw_date,
        message._from,
        message._to,
        unicode(message._subject.decode('utf-8')),
        message._reply_to
    ])
    conn.commit()


def main():
    conn = sqlite3.connect('database.db')
    for message in get_messages():
        insert_into_db(conn, message)
    conn.close()


if __name__ == "__main__":
    main()
