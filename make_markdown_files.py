#!/usr/bin/env python
import json
import glob
import os
from datetime import datetime


file_header = """\
---
layout: default
---

# {} {}

_Dates are calculated as the UTC date. The "raw date" from \
the email dump is included in brackets. The date may be inconsistent \
with the raw date because of the time difference with UTC time._

_Ordering by UTC time ensures true chronological ordering._

## Threads

"""


message_page_template = """\
---
layout: default
---

# {} - {}

## Header Data

From: {}<br>
To: {}<br>
Message Hash: {}<br>
Message ID: {}<br>
Reply To: {}<br>
UTC Datetime: {}<br>
Raw Date: {}<br>

## Raw message

```
{}
```

## Thread

{}

{}
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


def escape_chevrons(text):
    if text:
        return text.replace('<', '\\<').replace('>', '\\>')
    else:
        return "_N/A_"


def create_message_pages(thread, message=None):
    if not message:
        message = thread
    parsed_date = datetime.utcfromtimestamp(message['date'])
    path = "emails_test/{}/".format(parsed_date.strftime('%Y/%m'))
    if not os.path.exists(path):
        os.makedirs(path)
    thread_tree = make_markdown_thread_tree(thread, message["message_hash"])
    with open("raw_messages/{}/{}.txt".format(
        message['file_year'], message["message_hash"]
    )) as f:
        raw_message = "{% raw  %}" + f.read() + "{% endraw %}"
    with open("{}/{}.md".format(path, message["message_hash"]), "w") as o:
        o.write(message_page_template.format(
            parsed_date.date().isoformat(),
            message["subject"].encode('utf-8'),
            message["from"].encode('utf-8'),
            escape_chevrons(message["to"]),
            message["message_hash"],
            escape_chevrons(message["message_id"]),
            escape_chevrons(message["reply_to"]),
            parsed_date.strftime('%Y-%m-%d %H:%M:%S UTC'),
            message["raw_date"],
            raw_message,
            "_BACK TO TODO_",
            thread_tree
        ))
    for child in message["children"]:
        create_message_pages(thread, child)


def make_thread_list_item(message, offset, show_link=True):
    def make_link(subject, parsed_date, message_hash):
        return "[{}](/years/{}/{})".format(
            subject.encode('utf-8'),
            parsed_date.strftime('%Y/%m'),
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
    return "{}+ {} ({}) - {} - _{}_\n".format(
        "  " * offset,
        parsed_date.date().isoformat(),
        message['raw_date'],
        subject,
        message['from'].encode('utf-8').replace('<', '\\<').replace('>', '\\>')
    )


def make_markdown_thread_tree(message, message_hash=None, offset=0):
    show_link = message_hash != message['message_hash']
    text = make_thread_list_item(message, offset, show_link)
    for child in message['children']:
        text += make_markdown_thread_tree(child, message_hash, offset + 1)
    return text


def make_markdown_thread(thread):
    create_message_pages(thread)
    return "### {}\n{}".format(
        thread['subject'].encode('utf-8'),
        make_markdown_thread_tree(thread)
    )


def main():
    # for filename in glob.glob('json_months/199*/*.json'):
    for filename in glob.glob('json_months/1992/*.json'):
        if "unknown" in filename:
            continue  # ############### HANDLE THIS LATER
        with open(filename) as f:
            threads = json.loads(f.read())
        parsed_date = datetime.utcfromtimestamp(threads[0]['date'])
        if not os.path.exists("threads_test/{}/".format(parsed_date.year)):
            os.makedirs("threads_test/{}/".format(parsed_date.year))
        with open('threads_test/{}.md'.format(
            parsed_date.strftime('%Y/%m')
        ), 'w') as o:
            o.write(file_header.format(
                month_name_map[parsed_date.month - 1],
                parsed_date.year
            ))
            for thread in threads:
                o.write(make_markdown_thread(thread))
                o.write("\n")


if __name__ == "__main__":
    main()
