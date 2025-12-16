import logging
from io import StringIO
from pathlib import Path
from typing import Union, Optional

import pandas as pd
import requests
from requests.exceptions import SSLError, RequestException

logger = logging.getLogger(__name__)

BELPEX_QUARTER_HOURLY_URL = (
    "https://www.elexys.be/en/insights/quarter-hourly-belpex-day-ahead-spot-be"
)


def _fetch_belpex_html(url: str) -> Optional[str]:
    """
    Fetch raw HTML from the Belpex URL.

    - First try with normal certificate verification.
    - If that fails with an SSL error, retry once with verify=False (INSECURE).
      This is a pragmatic workaround for corporate / broken CA setups.
    """
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except SSLError as e:
        logger.warning(
            "SSL verification failed for %s (%s). Retrying with verify=False (INSECURE).",
            url,
            e,
        )
        try:
            resp = requests.get(url, timeout=15, verify=False)
            resp.raise_for_status()
            return resp.text
        except RequestException as exc2:
            logger.error(
                "Failed to fetch Belpex page %s even with verify=False: %s",
                url,
                exc2,
            )
            return None
    except RequestException as exc:
        logger.error("Failed to fetch Belpex page %s: %s", url, exc)
        return None


def _normalise_belpex_table(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Take a raw table from Elexys (HTML or Excel) and return a DataFrame with
    DateTime + BelpexFilter columns.

    Expected columns:
      - 'Date'
      - 'Time'
      - 'Euro' (price)
    """
    if df_raw.empty:
        return pd.DataFrame(columns=["DateTime", "BelpexFilter"])

    df = df_raw.copy()

    # Normalize column names by stripping spaces and making them lowercase
    rename_map: dict[str, str] = {}
    for col in df.columns:
        name = str(col).strip().lower()
        if name in ("datum", "date"):
            rename_map[col] = "date"
        elif "time" in name:
            rename_map[col] = "time"
        elif "euro" in name or "eur" in name:
            rename_map[col] = "euro"

    df = df.rename(columns=rename_map)

    if not {"date", "time", "euro"}.issubset(df.columns):
        return pd.DataFrame(columns=["DateTime", "BelpexFilter"])

    df = df[["date", "time", "euro"]].dropna()

    # Clean strings and convert time formats
    df["date"] = df["date"].astype(str).str.strip()
    df["time"] = df["time"].astype(str).str.strip()
    df["euro"] = df["euro"].astype(str).str.strip()

    # Convert "23u45" -> "23:45"
    time_clean = (
        df["time"]
        .str.replace("u", ":", regex=False)
        .str.replace("U", ":", regex=False)
    )

    # Build DateTime (Belgian-style dd/mm/YYYY)
    df["DateTime"] = pd.to_datetime(
        df["date"] + " " + time_clean,
        format="%d/%m/%Y %H:%M",
        errors="coerce",
    )

    # Parse Euro values like "67.04" (or "67,04" if ever present)
    price_str = (
        df["euro"]
        .str.replace("€", "", regex=False)
        .str.replace("\u00a0", "", regex=False)  # non-breaking space
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)      # support "67,04" -> "67.04"
        # NOTE: we do NOT remove '.' anymore – it is the decimal separator here.
    )

    df["BelpexFilter"] = pd.to_numeric(price_str, errors="coerce")

    df = df.dropna(subset=["DateTime", "BelpexFilter"]).copy()

    return df[["DateTime", "BelpexFilter"]]


def _scrape_belpex_page(url: str) -> pd.DataFrame:
    """
    Scrape a single Elexys page and return a normalised Belpex DataFrame.
    Fetch HTML via requests (with SSL fallback) and pass it to read_html.
    """
    logger.info("Fetching Belpex quarter-hourly data from %s", url)

    html = _fetch_belpex_html(url)
    if html is None:
        logger.warning("Could not fetch HTML for Belpex page %s", url)
        return pd.DataFrame(columns=["DateTime", "BelpexFilter"])

    try:
        # Wrap literal HTML string to avoid FutureWarning
        tables = pd.read_html(StringIO(html))
    except ValueError as exc:  # no tables found in the HTML
        logger.warning("No HTML tables found in Belpex page HTML (%s)", exc)
        return pd.DataFrame(columns=["DateTime", "BelpexFilter"])
    except Exception as exc:  # noqa: BLE001
        logger.warning("Error parsing Belpex HTML with read_html: %s", exc)
        return pd.DataFrame(columns=["DateTime", "BelpexFilter"])

    if not tables:
        logger.warning("No tables returned from read_html for Belpex HTML")
        return pd.DataFrame(columns=["DateTime", "BelpexFilter"])

    # Try each table until we find one that normalises correctly
    for t in tables:
        df = _normalise_belpex_table(t)
        if not df.empty:
            return df

    logger.warning("Could not normalise any table from Belpex HTML")
    return pd.DataFrame(columns=["DateTime", "BelpexFilter"])


def update_belpex_quarter_hourly(
    *,
    base_url: str = BELPEX_QUARTER_HOURLY_URL,
    output_path: Union[str, Path] = Path("data") / "belpex_quarter_hourly.csv",
    max_pages: int = 32,
    initial_excel: Optional[Union[str, Path]] = None,
) -> pd.DataFrame:
    """
    Fetch quarter-hourly Belpex (day-ahead spot BE) data from Elexys and store it
    under `data/` in a CSV file.

    Behaviour
    ---------
    - Existing CSV (`output_path`):
        * If it exists, load it (expects columns ['DateTime', 'BelpexFilter']).
    - Excel initialiser (`initial_excel`):
        * If provided, load the Excel file in the format:
              Date | Time | Euro
          normalise it, and union it with any existing CSV data
          (de-duping on DateTime).
    - Web scraping:
        * Scrape up to `max_pages` pages from the Belpex site.
        * Only keep rows with DateTime strictly greater than the maximum
          DateTime already present in the combined dataset.
        * Append new rows, remove duplicates on DateTime and save.

    Returns
    -------
    pd.DataFrame
        Full DataFrame with columns ['DateTime', 'BelpexFilter'] after update.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1) Start from existing CSV data (if any)
    # ------------------------------------------------------------------
    if output_path.exists():
        logger.info("Loading existing Belpex data from %s", output_path)
        try:
            existing = pd.read_csv(output_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to read existing Belpex CSV at %s (%s); ignoring it.",
                output_path,
                exc,
            )
            existing = pd.DataFrame(columns=["DateTime", "BelpexFilter"])
        else:
            if "DateTime" in existing.columns:
                existing["DateTime"] = pd.to_datetime(existing["DateTime"])
            else:
                logger.warning(
                    "Existing Belpex CSV at %s has no 'DateTime' column; ignoring it.",
                    output_path,
                )
                existing = pd.DataFrame(columns=["DateTime", "BelpexFilter"])
    else:
        logger.info("No existing Belpex file found at %s; starting fresh", output_path)
        existing = pd.DataFrame(columns=["DateTime", "BelpexFilter"])

    # ------------------------------------------------------------------
    # 2) Optional Excel initialiser (full historical Belpex data)
    # ------------------------------------------------------------------
    if initial_excel is not None:
        init_path = Path(initial_excel)
        if not init_path.exists():
            logger.warning(
                "Initial Belpex Excel file %s not found; skipping initialiser.",
                init_path,
            )
        else:
            logger.info("Loading initial Belpex data from Excel %s", init_path)
            try:
                raw_init = pd.read_excel(init_path)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to read initial Belpex Excel file %s (%s); skipping.",
                    init_path,
                    exc,
                )
            else:
                init_df = _normalise_belpex_table(raw_init)
                if init_df.empty:
                    logger.warning(
                        "Initial Belpex Excel file %s normalised to an empty "
                        "dataframe (check 'Date', 'Time', 'Euro' columns).",
                        init_path,
                    )
                else:
                    if existing.empty:
                        existing = init_df
                    else:
                        existing = (
                            pd.concat([existing, init_df], ignore_index=True)
                            .drop_duplicates(subset=["DateTime"])
                            .sort_values("DateTime")
                            .reset_index(drop=True)
                        )
                    logger.info(
                        "Initial Excel added %d unique Belpex rows (total now %d).",
                        len(init_df),
                        len(existing),
                    )

    # ------------------------------------------------------------------
    # 3) Scrape new pages and append only newer rows
    # ------------------------------------------------------------------
    latest_dt = existing["DateTime"].max() if not existing.empty else None

    all_new: list[pd.DataFrame] = []
    base_url = base_url.rstrip("/")

    for page in range(max_pages):
        url = base_url if page == 0 else f"{base_url}?page={page}"
        page_df = _scrape_belpex_page(url)

        if page_df.empty:
            # Either no data or we hit the end of pagination
            break

        page_df = page_df.sort_values("DateTime")

        if latest_dt is not None:
            # If the whole page is older or equal to what we already have, we can stop
            if page_df["DateTime"].max() <= latest_dt:
                break

            # Keep only newer rows
            page_df = page_df[page_df["DateTime"] > latest_dt]

        if page_df.empty:
            # Nothing new on this page
            continue

        all_new.append(page_df)

    if not all_new:
        logger.info("Belpex data is already up to date.")
        combined = existing.copy()
    else:
        new_data = pd.concat(all_new, ignore_index=True)
        frames = [df for df in [existing, new_data] if not df.empty]
        combined = (
            pd.concat(frames, ignore_index=True)
            .drop_duplicates(subset=["DateTime"])
            .sort_values("DateTime")
            .reset_index(drop=True)
        )
        logger.info(
            "Appending %d new Belpex rows (total now %d) to %s",
            len(new_data),
            len(combined),
            output_path,
        )

    # Save as CSV
    combined.to_csv(output_path, index=False)

    return combined
