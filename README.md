# Tibiatools

A collection of simple tools for Tibia, a MMORPG by CipSoft.

Q: Is it legal?
A: Yes, it is. It does not interact with the game client or server in any way. - look at the code.
Q: Is it safe?
A: Yes, it is. It does not interact with the game client or server in any way. - look at the code.
Q: Can I get banned for using it?
A: No, you can't. It does not interact with the game client or server in any way. - look at the code.

## Tools

* Exercise weapon finish time calculator
* Detailed report from your serverlog
  * Total damage dealt per player
  * Total damage received per player
  * Total healing done per player
  * Total healing received per player

## Requirements

* Python 3.12
* uv

## Installation

```shell
git clone git@github.com:kodzonko/tibiatools.git
cd tibiatools
uv pip install -e .
```

## Technical Details

* Written in Python with pandas  and duckdb for data analysis
* No game client interaction
* Read-only operations on log files

## Contributing

* Issues and PRs welcome
* Follow coding standards with ruff
* Run tests with pytest
