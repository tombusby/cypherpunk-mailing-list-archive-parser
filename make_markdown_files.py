#!/usr/bin/env python
import json
from datetime import datetime
from pprint import pprint


def make_thread_list_item(message, offset, show_link=True):
    def make_link(subject, parsed_date, message_hash):
        return "[{}](/years/{}/{}/{})".format(
            subject,
            parsed_date.year,
            parsed_date.month,
            message_hash
        )
    parsed_date = datetime.utcfromtimestamp(message['date'])
    if show_link:
        subject = make_link(message['subject'], parsed_date, message['message_hash'])
    else:
        subject = message['subject']
    return "{}+ {}-{}-{} ({}) - {} - _{}_\n".format(
        "  " * offset,
        parsed_date.year,
        parsed_date.month,
        parsed_date.day,
        message['raw_date'],
        subject,
        message['from'].replace('<', '\\<').replace('>', '\\>')
    )


def make_markdown_thread_tree(thread, message_hash, offset=0):
    show_link = message_hash != thread['message_hash']
    text = make_thread_list_item(thread, offset, show_link)
    for child in thread['children']:
        text += make_markdown_thread_tree(child, message_hash, offset + 1)
    return text


def main():
    with open('json_months/1992/9.json') as f:
        threads = json.loads(f.read())
        thread = threads[3]
        print make_markdown_thread_tree(thread, "17a09f8ed3e4c3e98e902c889e53518adfcf481d9d8ac1c147fbf572113bebf2")


if __name__ == "__main__":
    main()
