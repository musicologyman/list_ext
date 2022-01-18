#!/usr/bin/env python3

import argparse
import itertools
import os

from collections.abc import Iterable
from pathlib import Path, PosixPath
from typing import MutableSequence, TypeVar

import toolz.curried as curried
import toolz.functoolz as functoolz
import toolz.itertoolz as itertoolz

T = TypeVar('T')

COLUMN_RIGHT_PADDING = 5

def get_file_paths(parent_path:Path) -> Iterable[PosixPath]:
    return (p for p in parent_path.iterdir() if p.is_file())

def get_unique_suffixes(paths: Iterable[PosixPath]) -> Iterable[str]:
    return functoolz.pipe((p.suffix for p in paths),
                           curried.sorted(key=str.lower),
                           itertoolz.unique)

def get_max_item_length(items: Iterable[T]) -> int:
    return functoolz.pipe((len(item) for item in items),
                          max)

def get_column_width(max_item_length: int, padding: int=COLUMN_RIGHT_PADDING) \
        -> int:
    return max_item_length + padding

def get_columns_per_row(terminal_column_count: int, column_width: int) -> int:
    return terminal_column_count // column_width

def get_cmd_line_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', 
        default='.',
        required=False)
    return parser.parse_args()

def main():

    args = get_cmd_line_args() 

    root_path: Path  = Path(args.directory).expanduser()

#     if args.directory:
#         root_path = Path(args.directory).expanduser()
#     else:
#         root_path = Path('.')

    suffixes = functoolz.pipe(root_path,
                              get_file_paths,
                              get_unique_suffixes,
                              list)

    column_width = functoolz.pipe(suffixes,
                                  get_max_item_length,
                                  get_column_width)

    columns_per_row = \
        get_columns_per_row(os.get_terminal_size().columns, column_width)

    suffixes_by_row = \
        sorted(((i % columns_per_row, suffix) 
                for i, suffix in enumerate(suffixes)), 
                key=itertoolz.first)

    suffixes_grouped_by_row = itertools.groupby(suffixes_by_row,
                                                key=itertoolz.first)

    suffixes_grouped_for_printing: MutableSequence[tuple[int, Iterable[str]]] = \
            [(key, [suffix for _, suffix in values]) 
             for key, values in suffixes_grouped_by_row]
            
    for _, items in suffixes_grouped_for_printing:
        for item in items:
            if item == '':
                item = '(none)'
            print(f'{item:<15}', end='')
        print()

if __name__ == '__main__':
    main()
