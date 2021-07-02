import csv
import os
from typing import List

import discord

CSV_LOG_FIELDNAMES = [
    "email_addr",
    "id",
    "display_name",
    "name",
    "discriminator",
    "nick",
]


def save_email_info(email_addr: str, member: discord.Member):
    current_log_file = []

    if os.path.exists("email_log.csv"):
        with open("email_log.csv", newline="") as csvfile:
            current_log_file = csv.DictReader(csvfile)

    with open("email_log.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_LOG_FIELDNAMES)

        writer.writeheader()

        for existing_log in current_log_file:
            writer.writerow(existing_log)

        writer.writerow(
            {
                "email_addr": email_addr,
                "id": member.id,
                "display_name": member.display_name,
                "name": member.name,
                "discriminator": member.discriminator,
                "nick": member.nick,
            }
        )


def search_email_info(search_param: str):
    results = []

    with open("email_log.csv", newline="") as csvfile:
        current_log_file = csv.DictReader(csvfile)

        for line in current_log_file:
            for field, item in enumerate(line):
                if item.contains(search_param):
                    results.append(line)

    return results


def format_results(results: List[dict]):
    return_string = ""

    return_string += ",\t".join(CSV_LOG_FIELDNAMES)
    return_string += "\n"

    for line in results:
        for field in CSV_LOG_FIELDNAMES:
            return_string += line[field] + ",\t"
        return_string += "\n"

    return return_string
