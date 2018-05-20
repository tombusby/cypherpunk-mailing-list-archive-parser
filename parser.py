#!/usr/bin/env python
from email.parser import Parser
from glob import glob
import re
import pprint


def main():
    stringbuffer = ""
    emails = []
    for n in range(2, 9):
        with open("cryptome/cyp-199{}.txt".format(n)) as f:
            i = 0
            for line in f:
                if re.match("From cypherpunks\@MHonArc.venona", line):
                    emails.append(Parser().parsestr(stringbuffer))
                    stringbuffer = ""
                    i += 1
                else:
                    stringbuffer += line
    for message in emails:
        pprint.pprint(message.items())


if __name__ == "__main__":
    main()
