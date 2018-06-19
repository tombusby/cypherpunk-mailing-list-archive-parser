#!/usr/bin/env python
import json
from datetime import datetime


file_header = """\
---
layout: default
---

# {} {}

_Dates are calculated as the UTC date. The "raw date" from the email dump is included in brackets. The date may be inconsistent with the raw date because of the time difference with UTC time._

_Ordering by UTC time ensures true chronological ordering._

# Threads

"""


month_name_map = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
]


def make_thread_list_item(message, offset, show_link=True):
    def make_link(subject, parsed_date, message_hash):
        return "[{}](/years/{}/{}/{})".format(
            subject,
            parsed_date.year,
            str(parsed_date.month).zfill(2),
            message_hash
        )
    parsed_date = datetime.utcfromtimestamp(message['date'])
    if show_link:
        subject = make_link(
            message['subject'],
            parsed_date,
            message['message_hash']
        )
    else:
        subject = message['subject']
    return "{}+ {}-{}-{} ({}) - {} - _{}_\n".format(
        "  " * offset,
        parsed_date.year,
        str(parsed_date.month).zfill(2),
        str(parsed_date.day).zfill(2),
        message['raw_date'],
        subject,
        message['from'].replace('<', '\\<').replace('>', '\\>')
    )


def make_markdown_thread_tree(message, message_hash=None, offset=0):
    show_link = message_hash != message['message_hash']
    text = make_thread_list_item(message, offset, show_link)
    for child in message['children']:
        text += make_markdown_thread_tree(child, message_hash, offset + 1)
    return text


def make_markdown_thread(thread):
    return "## {}\n{}".format(
        thread['subject'],
        make_markdown_thread_tree(thread)
    )


def main():
    with open('json_months/1992/9.json') as f:
        threads = json.loads(f.read())
    with open('markdown_tests/09.md', 'w') as o:
        parsed_date = datetime.utcfromtimestamp(threads[0]['date'])
        o.write(file_header.format(
            month_name_map[parsed_date.month - 1],
            parsed_date.year
        ))
        for thread in threads:
            o.write(make_markdown_thread(thread))
            o.write("\n")


if __name__ == "__main__":
    main()
