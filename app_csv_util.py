import csv
import typing

def write_to_csv(filepath: str, contents: typing.List[typing.List[str]]):
    with open(filepath, "w") as f:
        writer = csv.writer(f, delimiter=",", newline='')
        for content in contents:
            writer.writerow(content)
