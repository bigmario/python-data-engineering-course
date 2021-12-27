import argparse
import logging

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="The path to de dirty data", type=str)
    args = parser.parse_args()
    df = main(args.filename)
    print(df)
