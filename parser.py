#!/usr/bin/env python
from email.parser import Parser
import re
import pprint
import sqlite3
import dateutil.parser
import warnings
warnings.filterwarnings("error")


timezone_info = {
    'EST': -18000,
    'EDT': -14400,
    'CST': -21600,
    'CDT': -18000,
    'MST': -25200,
    'MDT': -21600,
    'PST': -28800,
    'PDT': -25200,
    'PPE': -25200,
}


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
    errors = []
    warnings = []
    timezones = []
    for message in get_messages():
        # pprint.pprint(message.items())
        # insert_into_db(conn, message)
        try:
            parsed_date = dateutil.parser.parse(message['Date'], tzinfos=timezone_info)
            if not parsed_date.tzinfo:
                pprint.pprint((message['Date'], parsed_date))
        except ValueError:
            errors.append(message['Date'])
        except dateutil.parser.UnknownTimezoneWarning as e:
            timezone = re.match("tzname (\w+) identified", str(e)).group(1)
            if timezone not in timezones:
                timezones.append(timezone)
            warnings.append(message['Date'])
            # pprint.pprint((message['Date'], parsed_date))
    print warnings
    print errors
    print timezones
    # conn.close()


if __name__ == "__main__":
    main()
