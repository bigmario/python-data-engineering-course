import argparse
import hashlib
import logging

import nltk
from nltk.corpus import stopwords

from urllib.parse import urlparse

import pandas as pd

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def main(filename):
    logger.info("Starting cleanup process")

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    df = _fill_missing_titles(df)
    df = _generate_uids_for_rows(df)
    df = _remove_new_lines_from_body(df)
    df = tokenize_column(df, "title")
    df = tokenize_column(df, "body")
    df = _remove_duplicate_entries(df, "title")

    return df


def _read_data(filename):
    logger.info(f"Reading file {filename}")

    return pd.read_csv(filename)


def _extract_newspaper_uid(filename):
    logger.info(f"Extracting newspaper uid {filename}")
    newspaper_uid = filename.split("_")[0]

    logger.info(f"Newspaper uid detected{newspaper_uid}")

    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info(f"Filling newspaper uid column with {newspaper_uid}")
    df["newspaper_uid"] = newspaper_uid

    return df


def _extract_host(df):
    logger.info(f"Extracting host from url")
    df["host"] = df["url"].apply(lambda url: urlparse(url).netloc)

    return df


def _fill_missing_titles(df):
    logger.info(f"Filling missing titles")
    missing_title_mask = df["title"].isna()

    missing_titles = (
        df[missing_title_mask]["url"]
        .str.extract(r"(?P<missing_titles>[^/]+)$")
        .applymap(lambda title: title.split("-"))
        .applymap(lambda title_word_list: " ".join(title_word_list))
    )

    df.loc[missing_title_mask, "title"] = missing_titles.loc[:, "missing_titles"]

    return df


def _generate_uids_for_rows(df):
    logger.info(f"Generating uids for each row")

    uids = df.apply(lambda row: hashlib.md5(bytes(row["url"].encode())), axis=1).apply(
        lambda hash_object: hash_object.hexdigest()
    )

    df["uid"] = uids

    return df.set_index("uid")


def _remove_new_lines_from_body(df):
    logger.info(f"Removing newlines from body")

    stripped_body = (
        df.apply(lambda row: row["body"], axis=1)
        .apply(lambda body: list(body))
        .apply(
            lambda letters: list(map(lambda letter: letter.replace("\n", ""), letters))
        )
        .apply(lambda letters: "".join(letters))
    )

    df["body"] = stripped_body

    return df


def tokenize_column(df, column_name):
    logger.info(f"Calculating the number of unique tokens in {column_name}")
    stop_words = set(stopwords.words("spanish"))

    n_tokens = (
        df.dropna()
        .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
        .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
        .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
        .apply(
            lambda word_list: list(
                filter(lambda word: word not in stop_words, word_list)
            )
        )
        .apply(lambda valid_word_list: len(valid_word_list))
    )

    df[f"ntokens_{column_name}"] = n_tokens

    return df


def _remove_duplicate_entries(df):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="The path to de dirty data", type=str)
    args = parser.parse_args()
    df = main(args.filename)
    print(df)
