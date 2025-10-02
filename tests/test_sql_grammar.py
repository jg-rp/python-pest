import pytest

from pest import Parser


@pytest.fixture(scope="module")
def grammar() -> str:
    with open("tests/grammars/sql.pest", encoding="utf-8") as fd:
        return fd.read()


def test_select(parser: Parser) -> None:
    pairs = parser.parse("Command", "select * from table")
    assert pairs.as_list() == [
        {
            "rule": "Query",
            "span": {"str": "select * from table", "start": 0, "end": 19},
            "inner": [
                {
                    "rule": "SelectWithOptionalContinuation",
                    "span": {"str": "select * from table", "start": 0, "end": 19},
                    "inner": [
                        {
                            "rule": "Select",
                            "span": {
                                "str": "select * from table",
                                "start": 0,
                                "end": 19,
                            },
                            "inner": [
                                {
                                    "rule": "Projection",
                                    "span": {"str": "* ", "start": 7, "end": 9},
                                    "inner": [
                                        {
                                            "rule": "Asterisk",
                                            "span": {"str": "*", "start": 7, "end": 8},
                                            "inner": [],
                                        }
                                    ],
                                },
                                {
                                    "rule": "Scan",
                                    "span": {"str": "table", "start": 14, "end": 19},
                                    "inner": [
                                        {
                                            "rule": "Identifier",
                                            "span": {
                                                "str": "table",
                                                "start": 14,
                                                "end": 19,
                                            },
                                            "inner": [],
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                }
            ],
        },
        {
            "rule": "EOF",
            "span": {"str": "", "start": 19, "end": 19},
            "inner": [
                {
                    "rule": "EOI",
                    "span": {"str": "", "start": 19, "end": 19},
                    "inner": [],
                },
            ],
        },
    ]


def test_create_user(parser: Parser) -> None:
    pairs = parser.parse(
        "Command", """create user "my_user" with password 'strong_password123'"""
    )
    assert pairs.as_list() == [
        {
            "rule": "CreateUser",
            "span": {
                "str": "create user \"my_user\" with password 'strong_password123'",
                "start": 0,
                "end": 56,
            },
            "inner": [
                {
                    "rule": "Identifier",
                    "span": {"str": '"my_user"', "start": 12, "end": 21},
                    "inner": [],
                },
                {
                    "rule": "SingleQuotedString",
                    "span": {"str": "'strong_password123'", "start": 36, "end": 56},
                    "inner": [],
                },
            ],
        },
        {
            "rule": "EOF",
            "span": {"str": "", "start": 56, "end": 56},
            "inner": [
                {
                    "rule": "EOI",
                    "span": {"str": "", "start": 56, "end": 56},
                    "inner": [],
                },
            ],
        },
    ]


def test_insert_from_select(parser: Parser) -> None:
    pairs = parser.parse(
        "Command",
        '''insert into "my_table" ("col_1", "col_2")
                  select "name", "class", avg("age")
                  from "students"
                  where "age" > 15
                  group by "age"''',
    )
    assert pairs.as_list() == [
        {
            "rule": "Query",
            "span": {
                "str": 'insert into "my_table" ("col_1", "col_2")\n                  select "name", "class", avg("age")\n                  from "students"\n                  where "age" > 15\n                  group by "age"',
                "start": 0,
                "end": 196,
            },
            "inner": [
                {
                    "rule": "Insert",
                    "span": {
                        "str": 'insert into "my_table" ("col_1", "col_2")\n                  select "name", "class", avg("age")\n                  from "students"\n                  where "age" > 15\n                  group by "age"',
                        "start": 0,
                        "end": 196,
                    },
                    "inner": [
                        {
                            "rule": "Identifier",
                            "span": {"str": '"my_table"', "start": 12, "end": 22},
                            "inner": [],
                        },
                        {
                            "rule": "TargetColumns",
                            "span": {"str": '"col_1", "col_2"', "start": 24, "end": 40},
                            "inner": [
                                {
                                    "rule": "Identifier",
                                    "span": {"str": '"col_1"', "start": 24, "end": 31},
                                    "inner": [],
                                },
                                {
                                    "rule": "Identifier",
                                    "span": {"str": '"col_2"', "start": 33, "end": 40},
                                    "inner": [],
                                },
                            ],
                        },
                        {
                            "rule": "Select",
                            "span": {
                                "str": 'select "name", "class", avg("age")\n                  from "students"\n                  where "age" > 15\n                  group by "age"',
                                "start": 60,
                                "end": 196,
                            },
                            "inner": [
                                {
                                    "rule": "Projection",
                                    "span": {
                                        "str": '"name", "class", avg("age")\n                  ',
                                        "start": 67,
                                        "end": 113,
                                    },
                                    "inner": [
                                        {
                                            "rule": "Column",
                                            "span": {
                                                "str": '"name"',
                                                "start": 67,
                                                "end": 73,
                                            },
                                            "inner": [
                                                {
                                                    "rule": "Expr",
                                                    "span": {
                                                        "str": '"name"',
                                                        "start": 67,
                                                        "end": 73,
                                                    },
                                                    "inner": [
                                                        {
                                                            "rule": "IdentifierWithOptionalContinuation",
                                                            "span": {
                                                                "str": '"name"',
                                                                "start": 67,
                                                                "end": 73,
                                                            },
                                                            "inner": [
                                                                {
                                                                    "rule": "Identifier",
                                                                    "span": {
                                                                        "str": '"name"',
                                                                        "start": 67,
                                                                        "end": 73,
                                                                    },
                                                                    "inner": [],
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                }
                                            ],
                                        },
                                        {
                                            "rule": "Column",
                                            "span": {
                                                "str": '"class"',
                                                "start": 75,
                                                "end": 82,
                                            },
                                            "inner": [
                                                {
                                                    "rule": "Expr",
                                                    "span": {
                                                        "str": '"class"',
                                                        "start": 75,
                                                        "end": 82,
                                                    },
                                                    "inner": [
                                                        {
                                                            "rule": "IdentifierWithOptionalContinuation",
                                                            "span": {
                                                                "str": '"class"',
                                                                "start": 75,
                                                                "end": 82,
                                                            },
                                                            "inner": [
                                                                {
                                                                    "rule": "Identifier",
                                                                    "span": {
                                                                        "str": '"class"',
                                                                        "start": 75,
                                                                        "end": 82,
                                                                    },
                                                                    "inner": [],
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                }
                                            ],
                                        },
                                        {
                                            "rule": "Column",
                                            "span": {
                                                "str": 'avg("age")\n                  ',
                                                "start": 84,
                                                "end": 113,
                                            },
                                            "inner": [
                                                {
                                                    "rule": "Expr",
                                                    "span": {
                                                        "str": 'avg("age")\n                  ',
                                                        "start": 84,
                                                        "end": 113,
                                                    },
                                                    "inner": [
                                                        {
                                                            "rule": "IdentifierWithOptionalContinuation",
                                                            "span": {
                                                                "str": 'avg("age")',
                                                                "start": 84,
                                                                "end": 94,
                                                            },
                                                            "inner": [
                                                                {
                                                                    "rule": "Identifier",
                                                                    "span": {
                                                                        "str": "avg",
                                                                        "start": 84,
                                                                        "end": 87,
                                                                    },
                                                                    "inner": [],
                                                                },
                                                                {
                                                                    "rule": "FunctionInvocationContinuation",
                                                                    "span": {
                                                                        "str": '("age")',
                                                                        "start": 87,
                                                                        "end": 94,
                                                                    },
                                                                    "inner": [
                                                                        {
                                                                            "rule": "FunctionArgs",
                                                                            "span": {
                                                                                "str": '"age"',
                                                                                "start": 88,
                                                                                "end": 93,
                                                                            },
                                                                            "inner": [
                                                                                {
                                                                                    "rule": "Expr",
                                                                                    "span": {
                                                                                        "str": '"age"',
                                                                                        "start": 88,
                                                                                        "end": 93,
                                                                                    },
                                                                                    "inner": [
                                                                                        {
                                                                                            "rule": "IdentifierWithOptionalContinuation",
                                                                                            "span": {
                                                                                                "str": '"age"',
                                                                                                "start": 88,
                                                                                                "end": 93,
                                                                                            },
                                                                                            "inner": [
                                                                                                {
                                                                                                    "rule": "Identifier",
                                                                                                    "span": {
                                                                                                        "str": '"age"',
                                                                                                        "start": 88,
                                                                                                        "end": 93,
                                                                                                    },
                                                                                                    "inner": [],
                                                                                                }
                                                                                            ],
                                                                                        }
                                                                                    ],
                                                                                }
                                                                            ],
                                                                        }
                                                                    ],
                                                                },
                                                            ],
                                                        }
                                                    ],
                                                }
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "rule": "Scan",
                                    "span": {
                                        "str": '"students"\n                  ',
                                        "start": 118,
                                        "end": 147,
                                    },
                                    "inner": [
                                        {
                                            "rule": "Identifier",
                                            "span": {
                                                "str": '"students"',
                                                "start": 118,
                                                "end": 128,
                                            },
                                            "inner": [],
                                        }
                                    ],
                                },
                                {
                                    "rule": "Selection",
                                    "span": {
                                        "str": '"age" > 15\n                  ',
                                        "start": 153,
                                        "end": 182,
                                    },
                                    "inner": [
                                        {
                                            "rule": "Expr",
                                            "span": {
                                                "str": '"age" > 15\n                  ',
                                                "start": 153,
                                                "end": 182,
                                            },
                                            "inner": [
                                                {
                                                    "rule": "IdentifierWithOptionalContinuation",
                                                    "span": {
                                                        "str": '"age" ',
                                                        "start": 153,
                                                        "end": 159,
                                                    },
                                                    "inner": [
                                                        {
                                                            "rule": "Identifier",
                                                            "span": {
                                                                "str": '"age"',
                                                                "start": 153,
                                                                "end": 158,
                                                            },
                                                            "inner": [],
                                                        }
                                                    ],
                                                },
                                                {
                                                    "rule": "Gt",
                                                    "span": {
                                                        "str": ">",
                                                        "start": 159,
                                                        "end": 160,
                                                    },
                                                    "inner": [],
                                                },
                                                {
                                                    "rule": "Unsigned",
                                                    "span": {
                                                        "str": "15",
                                                        "start": 161,
                                                        "end": 163,
                                                    },
                                                    "inner": [],
                                                },
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "rule": "GroupBy",
                                    "span": {"str": '"age"', "start": 191, "end": 196},
                                    "inner": [
                                        {
                                            "rule": "Expr",
                                            "span": {
                                                "str": '"age"',
                                                "start": 191,
                                                "end": 196,
                                            },
                                            "inner": [
                                                {
                                                    "rule": "IdentifierWithOptionalContinuation",
                                                    "span": {
                                                        "str": '"age"',
                                                        "start": 191,
                                                        "end": 196,
                                                    },
                                                    "inner": [
                                                        {
                                                            "rule": "Identifier",
                                                            "span": {
                                                                "str": '"age"',
                                                                "start": 191,
                                                                "end": 196,
                                                            },
                                                            "inner": [],
                                                        }
                                                    ],
                                                }
                                            ],
                                        }
                                    ],
                                },
                            ],
                        },
                    ],
                }
            ],
        },
        {
            "rule": "EOF",
            "span": {"str": "", "start": 196, "end": 196},
            "inner": [
                {
                    "rule": "EOI",
                    "span": {"str": "", "start": 196, "end": 196},
                    "inner": [],
                },
            ],
        },
    ]
