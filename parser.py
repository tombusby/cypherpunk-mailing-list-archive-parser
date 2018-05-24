#!/usr/bin/env python
from email.parser import Parser
import os
import glob
import re
import sqlite3
import dateutil.parser
import hashlib
import pprint


class EmailMessage(object):

    def __init__(self, file_year, raw_text):
        m = hashlib.sha256()
        m.update(raw_text)
        self._message_hash = m.hexdigest()
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


def clean_the_slate(conn):
    for f in glob.glob('raw_messages/199*/*'):
        os.remove(f)
    conn.cursor().execute("DELETE FROM messages;")
    conn.commit()


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
    def process_possible_unicode(text):
        try:
            return unicode(text.decode('utf-8', 'replace'))
        except UnicodeDecodeError:
            return str(text)

    sql = """
        INSERT INTO messages (
            `message_hash`,
            `message_id`,
            `file_year`,
            `date`,
            `raw_date`,
            `from`,
            `to`,
            `subject`,
            `reply_to`
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """
    params = [
        message._message_hash,
        message._message_id,
        message._file_year,
        message._unixtime,
        message._raw_date,
        process_possible_unicode(message._from),
        process_possible_unicode(message._to) if message._to else None,
        process_possible_unicode(message._subject),
        message._reply_to
    ]
    try:
        conn.cursor().execute(sql, params)
    except sqlite3.IntegrityError:
        pass
    except sqlite3.ProgrammingError:
        pprint.pprint(params)


def write_message_to_file(message):
    with open("raw_messages/{}/{}.txt".format(
        message._file_year, message._message_hash
    ), "w") as f:
        f.write(message._raw_text)


def mark_replies_with_no_parent(conn):
    sql = """
        UPDATE
            `messages`
        SET
            `no_parent` = 1
        WHERE
            `reply_to` IS NOT NULL
            AND `reply_to` NOT IN (
                SELECT `message_id` FROM `messages`
            );
    """
    conn.cursor().execute(sql)
    conn.commit()


def fix_weird_1999_dates_between_92_and_97(conn):
    sql = """
        UPDATE
            `messages`
        SET
            `raw_date` = NULL,
            `date` = NULL
        WHERE
            `file_year` < 1998
            AND `raw_date` LIKE "%1999%"
    """
    conn.cursor().execute(sql)
    conn.commit()


def fix_genuine_1999_dates(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `messages` WHERE `raw_date` LIKE '%1999%'")
    for row in cursor.fetchall():
        os.rename(
            "raw_messages/{}/{}.txt".format(row[2], row[0]),
            "raw_messages/1999/{}.txt".format(row[0])
        )
    sql = """
        UPDATE
            `messages`
        SET
            `file_year` = 1999
        WHERE
            `raw_date` LIKE '%1999%'
    """
    conn.cursor().execute(sql)
    conn.commit()


def main():
    conn = sqlite3.connect('database.db')
    clean_the_slate(conn)
    for message in get_messages():
        insert_into_db(conn, message)
        write_message_to_file(message)
    conn.commit()
    mark_replies_with_no_parent(conn)
    fix_weird_1999_dates_between_92_and_97(conn)
    fix_genuine_1999_dates(conn)
    conn.close()


if __name__ == "__main__":
    main()
