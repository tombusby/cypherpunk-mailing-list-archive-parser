#!/usr/bin/env python
import sqlite3
import time
import json


def get_thread_roots(conn):
    pass


def main():
    conn = sqlite3.connect('database.db')
    print conn
    conn.close()


if __name__ == "__main__":
    main()
