import sqlite3
import main
from typing import List
import os

conn: sqlite3.Connection = sqlite3.connect('db.sqlite')

lang_weighted = {"ABAP": 1,
                 "Ada": 1,
                 "APL": 1,
                 "ASM": 1,
                 "Beef": 1,
                 "C": 1,
                 "C#": 1,
                 "C++": 1,
                 "Cobol": 1,
                 "D": 1,
                 "Dart": 1,
                 "Delphi": 1,
                 "Elixir": 1,
                 "Elm": 1,
                 "F#": 1,
                 "FORTH": 1,
                 "Fortran": 1,
                 "GDScript": 1,
                 "Go": 1,
                 "Haskell": 1,
                 "HolyC": 1,
                 "Idris": 1,
                 "Java": 1,
                 "Javascript": 1,
                 "Kotlin": 1,
                 "Lisp": 1,
                 "Lua": 1,
                 "Nim": 1,
                 "NodeJs": 1,
                 "Objective-C": 1,
                 "OCaml": 1,
                 "Perl": 1,
                 "PHP": 1,
                 "Prolog": 1,
                 "Python": 1,
                 "R": 1,
                 "Ruby": 1,
                 "Rust": 1,
                 "Scala": 1,
                 "Shell": 1,
                 "Smalltalk": 1,
                 "Solidity": 1,
                 "SQL": 1,
                 "Swift": 1,
                 "Typescript": 1,
                 "V": 1,
                 "Verilog": 1,
                 "VHDL": 1,
                 "Visual Basic": 1
                 }


# Initialization of database
def init() -> None:
    # Create table for storing usage of images
    conn.executescript('''
    create table if not exists language_image_usage
    (
        id       integer
            constraint language_image_usage_pk
                primary key autoincrement,
        language text not null,
        image    text not null,
        weight   integer default 100 not null,
        used     integer default 0 not null
    );

    create unique index if not exists language_image_usage_id_uindex
    on language_image_usage (id);
    ''')

    print("Table language_image_usage created")

    # Create table with date of last change
    conn.execute('''
    create table if not exists banner_change_time
    (
        change_date text
    );
    ''')

    print("Table banner_change_time created")

    conn.executescript('''
    create table if not exists user_votes
    (
        username       text not null
            constraint user_votes_pk
                primary key,
        voted_language text not null,
        vote_date      text
    );
    
    create unique index if not exists user_votes_username_uindex
        on user_votes (username);
    ''')

    print("Table user_votes created")

    # If language_image_usage is empty
    if conn.execute('SELECT count(*) FROM language_image_usage;').fetchone()[0] == 0:
        language_image = []
        for lang in lang_weighted.keys():
            images: List = next(os.walk(f'Anime-Girls-Holding-Programming-Books-master/{lang}'), (None, None, []))[2]
            for img in images:
                language_image.append((lang, img))
        print(language_image)
        # Add every image to database
        conn.executemany('''
        INSERT INTO language_image_usage (language, image) VALUES (? , ?);
        ''', language_image)
        conn.commit()
        print("Images added")
