#!/usr/bin/env python
import json
import glob
import os
import re
from datetime import datetime
import sqlite3


month_file_header = """\
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


author_file_header = """\
---
layout: default
sender_id: {}
post_count: {}
---

# {} ({} {})

_Be aware that many list participants used multiple email addresses \
over their time active on the list. As such this page may not contain \
all threads available._

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


author_index_template = """\
---
layout: default
permalink: /authors/
---

# Authors by Number of Posts (Highest First)

_Be aware that many list participants used multiple email addresses over \
their time active on the list. As such an email address page may not contain \
all threads available for that person._

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


def make_id_from_email(email):
    email = email.replace('@', '_at_')
    email = re.sub('[<>\(\)\.\s]+', '_', email)
    email = re.sub('\W+', '', email)
    return email.lower()


def escape_chevrons(text):
    if text:
        return text.encode('utf-8').replace('<', '\\<').replace('>', '\\>')
    else:
        return "_N/A_"


def make_back_to_links(thread):
    def get_months(months, message):
        if not message['date']:
            return []
        parsed_date = datetime.utcfromtimestamp(message['date'])
        months.add((parsed_date.year, parsed_date.month))
        for child in message['children']:
            get_months(months, child)
        return months
    def get_authors(authors, message):
        sender_id = make_id_from_email(message['from'])
        authors.add((sender_id, message['from']))
        for child in message['children']:
            get_authors(authors, child)
        return authors
    months = get_months(set(), thread)
    authors = get_authors(set(), thread)
    link_text = ""
    for year, month in sorted(months):
        link_text += "+ Return to [{} {}](/archive/{}/{})\n".format(
            month_name_map[month - 1],
            year,
            year,
            str(month).zfill(2)
        )
    link_text += "\n"
    for sender_id, email_from in sorted(authors):
        link_text += "+ Return to \"[{}](/authors/{})\"\n".format(
            email_from.encode('utf-8').replace('@', '<span>@</span>'),
            sender_id
        )
    return link_text


def create_message_pages(thread, message=None):
    if not message:
        message = thread
    if message['date']:
        parsed_date = datetime.utcfromtimestamp(message['date'])
        path = "emails_test/{}/".format(parsed_date.strftime('%Y/%m'))
        iso_date = parsed_date.date().isoformat()
        utc_formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S UTC')
        raw_date = message["raw_date"].encode('utf-8')
    else:
        path = "emails_test/{}/unknown/".format(message['file_year'])
        iso_date = "(Unknown Date)"
        utc_formatted_date = "(Unknown Date)"
        raw_date = "_N/A_"
    if not os.path.exists(path):
        os.makedirs(path)
    thread_tree = make_markdown_thread_tree(thread, message["message_hash"])
    with open("raw_messages/{}/{}.txt".format(
        message['file_year'], message["message_hash"]
    )) as f:
        raw_message = "{% raw  %}" + f.read() + "{% endraw %}"
    with open("{}/{}.md".format(path, message["message_hash"]), "w") as o:
        o.write(message_page_template.format(
            iso_date,
            message["subject"].encode('utf-8'),
            escape_chevrons(message["from"]).replace('@', '<span>@</span>'),
            escape_chevrons(message["to"]),
            message["message_hash"],
            escape_chevrons(message["message_id"]),
            escape_chevrons(message["reply_to"]),
            utc_formatted_date,
            raw_date,
            raw_message,
            make_back_to_links(thread),
            thread_tree
        ))
    for child in message["children"]:
        create_message_pages(thread, child)


def make_thread_list_item(message, offset, show_link=True):
    def make_link(subject, formatted_date, message_hash):
        return "[{}](/archive/{}/{})".format(
            subject,
            formatted_date,
            message_hash
        )
    if message['date']:
        parsed_date = datetime.utcfromtimestamp(message['date'])
        path = parsed_date.strftime('%Y/%m')
        iso_date = parsed_date.date().isoformat()
    else:
        path = str(message['file_year']) + "/unknown"
        iso_date = "(Unknown Date)"
    if show_link:
        subject = make_link(
            message['subject'].encode('utf-8'),
            path,
            message['message_hash']
        )
    else:
        subject = message['subject'].encode('utf-8')
    return "{}+ {} ({}) - {} - _{}_\n".format(
        "  " * offset,
        iso_date,
        message['raw_date'],
        subject,
        message['from'].encode('utf-8').replace('<', '\\<').replace('>', '\\>')
    )


def make_markdown_thread_tree(message, message_hash=None, offset=0):
    show_link = message_hash != message['message_hash']
    if message['no_parent']:
        text = "+ _Unknown thread root_\n"
        offset += 1
    else:
        text = ""
    text += make_thread_list_item(message, offset, show_link)
    for child in message['children']:
        text += make_markdown_thread_tree(child, message_hash, offset + 1)
    return text


def make_markdown_thread(thread):
    return "### {}\n{}".format(
        thread['subject'].encode('utf-8'),
        make_markdown_thread_tree(thread)
    )


def build_threads_by_month():
    for filename in glob.glob('json_months/199*/*.json'):
        print filename
        with open(filename) as f:
            threads = json.loads(f.read())
        regex = "json_months/([0-9]+)/([0-9]+|unknown).json"
        matches = re.match(regex, filename)
        year, month = matches.group(1), matches.group(2)
        if not os.path.exists("threads_test/{}/".format(year)):
            os.makedirs("threads_test/{}/".format(year))
        with open('threads_test/{}/{}.md'.format(
            year,
            month.zfill(2)
        ), 'w') as o:
            if month != "unknown":
                month_name = month_name_map[int(month) - 1]
            else:
                month_name = "(unknown month)"
            o.write(month_file_header.format(
                month_name,
                year
            ))
            for thread in threads:
                create_message_pages(thread)
                o.write(make_markdown_thread(thread))
                o.write("\n")


def build_author_indices():
    if not os.path.exists("authors_test/"):
        os.makedirs("authors_test/")
    for filename in glob.glob('json_authors/*.json'):
        print filename
        with open(filename) as f:
            author = json.loads(f.read())
        with open('authors_test/{}.md'.format(author['sender_id']), 'w') as o:
            o.write(author_file_header.format(
                author['sender_id'],
                author['count'],
                author['from'].encode('utf-8').replace('@', '<span>@</span>'),
                author['count'],
                "posts" if author['count'] > 1 else "post"
            ))
            for thread in author['threads']:
                o.write(make_markdown_thread(thread))
                o.write("\n")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    sql = """
        SELECT
            `from`,
            `sender_id`,
            count(*) AS `messages`
        FROM
            `messages`
        GROUP BY
            `sender_id`
        ORDER BY
            `messages` DESC;
    """
    with open('author_index/authors.md', 'w') as o:
        o.write(author_index_template)
        for row in cursor.execute(sql):
            o.write("+ [{}](/authors/{}/) - _{} posts_\n".format(
                row[0].encode('utf-8').replace('@', '<span>@</span>'),
                row[1],
                row[2],
            ))


def main():
    build_threads_by_month()
    build_author_indices()


if __name__ == "__main__":
    main()
