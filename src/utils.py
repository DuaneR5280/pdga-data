import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List
import pandas as pd
from pandas import DataFrame
import httpx
from schemas import DiscBase

# Settings
BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / "data"
LOG_FILE = DATA_PATH / "logs" / "pdga-utils.log"
PDGA_BASE_URL = "https://www.pdga.com/technical-standards/"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)


class Downloader:
    """Handles downloading and saving CSV files."""

    def __init__(self, filepath: Path, filename: str, url: str) -> None:
        self.filepath = filepath
        self.filename = filename
        self.url = url
        self.client = httpx.Client()

    def download_csv_data(self) -> List[List[str]]:
        """Downloads CSV data from a URL."""
        try:
            logging.info("Downloading CSV data...")
            response = self.client.get(self.url)
            response.raise_for_status()
            decoded_content = response.content.decode("utf-8")
            csv_data = list(csv.reader(decoded_content.splitlines(), delimiter=","))
            logging.info("CSV data downloaded successfully.")
            return csv_data
        except Exception as e:
            logging.error(f"Failed to download CSV data: {e}")
            raise
        finally:
            self.client.close()

    def save_csv(self, csv_data: List[List[str]]) -> None:
        """Saves CSV data to a file."""
        self.filepath.mkdir(parents=True, exist_ok=True)
        csv_file = self.filepath / self.filename
        with open(csv_file, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(csv_data)
        logging.info(f"CSV file saved: {csv_file}")


class DiscsDF:
    """Handles transformation and schema validation for disc data."""

    def __init__(self, df: DataFrame) -> None:
        self.df = df
        self.schema_data = None
        self.transform()

    def transform(self) -> None:
        """Applies transformations and validates schema."""
        self.rename_columns()
        self.clean_company_names()
        self.clean_data_types()
        self.validate_schema()

    def rename_columns(self) -> None:
        """Renames and removes unnecessary columns."""
        fieldnames = [
            "manufacturer", "name", "weight_max", "diameter", "height", "rim_depth",
            "rim_diameter_inside", "rim_thickness", "rim_ratio", "rim_config",
            "flex", "cert", "approved",
        ]
        remove_columns = ["Class", "Max Weight Vint (gr)", "Last Year Production"]
        self.df.drop(columns=remove_columns, inplace=True, errors="ignore")
        self.df.columns = fieldnames

    def clean_company_names(self) -> None:
        """Fixes and standardizes company names."""
        replacements = {
            "Destiny/Dynamic Discs": "Destiny-Dynamic Discs",
            "RPM Discs/Disc Golf Aotearoa": "RPM Discs-Disc Golf Aotearoa",
            "Innova-Champion Discs": "Innova Champion Discs",
            "Westside Golf Discs": "Westside Discs",
        }
        self.df.replace(replacements, inplace=True)

    def clean_data_types(self) -> None:
        """Cleans data types for database compatibility."""
        self.df["approved"] = pd.to_datetime(self.df["approved"], errors="coerce").dt.date
        self.df.fillna(0.0, inplace=True)

    def validate_schema(self) -> None:
        """Validates data against the schema."""
        records = self.df.to_dict("records")
        data, errors = [], []
        for record in records:
            try:
                record["approved"] = datetime.combine(record["approved"], datetime.min.time())
                data.append(DiscBase(**record))
            except Exception as e:
                errors.append((record, e))
        self.schema_data = data
        logging.info(
            f"Schema validation complete. Records: {len(data)}, Errors: {len(errors)}"
        )


class PDGADataHandler:
    """Handles downloading, transforming, and saving data for discs and manufacturers."""

    def __init__(self, base_url: str, csv_url: str, filepath: Path, filename: str) -> None:
        self.base_url = base_url
        self.csv_url = csv_url
        self.filepath = filepath
        self.filename = filename
        self.downloader = Downloader(filepath, filename, csv_url)

    def download_and_save_csv(self) -> None:
        """Downloads and saves CSV data if not already saved."""
        csv_file = self.filepath / self.filename
        if csv_file.exists():
            logging.info(f"File already exists: {csv_file}")
            return
        csv_data = self.downloader.download_csv_data()
        self.downloader.save_csv(csv_data)

    def load_dataframe(self) -> DataFrame:
        """Loads the CSV file into a DataFrame."""
        csv_file = self.filepath / self.filename
        return pd.read_csv(csv_file)


def main() -> None:
    # Discs Data
    discs_handler = PDGADataHandler(
        base_url=PDGA_BASE_URL + "equipment-certification/discs/",
        csv_url=PDGA_BASE_URL + "equipment-certification/discs/export",
        filepath=DATA_PATH,  #/ "discs",
        filename=f"pdga-approved-disc-golf-discs_{datetime.now().date()}.csv",
    )
    discs_handler.download_and_save_csv()
    raw_df = discs_handler.load_dataframe()
    DiscsDF(raw_df)

    # Manufacturers Data
    manufacturers_handler = PDGADataHandler(
        base_url=PDGA_BASE_URL + "manufacturers",
        csv_url=PDGA_BASE_URL + "manufacturers/csv?attach=page",
        filepath=DATA_PATH,  #/ "manufacturers",
        filename=f"pdga-manufacturers_{datetime.now().date()}.csv",
    )
    manufacturers_handler.download_and_save_csv()


if __name__ == "__main__":
    main()
