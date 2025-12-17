from __future__ import annotations
from dataclasses import dataclass

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import pdfplumber
import re
@dataclass
class SolarSpec:
    solar_panel_cost: float
    solar_panel_count: int
    solar_panel_lifetime: int
    panel_surface: float
    annual_degredation: float
    panel_efficiency: float
    temperature_coefficient: float

    @property
    def total_solar_panel_cost(self) -> float:
        return self.solar_panel_cost * self.solar_panel_count

    @property
    def total_panel_surface(self) -> float:
        return self.panel_surface * self.solar_panel_count


@dataclass
class BatterySpec:
    battery_cost: float
    battery_count: int
    battery_lifetime: int
    battery_capacity: float

    @property
    def total_battery_cost(self) -> float:
        return self.battery_cost * self.battery_count


@dataclass
class InverterSpec:
    inverter_cost: float
    inverter_lifetime: int
    inverter_efficiency: float
    DC_battery: float
    DC_solar_panels: float
    AC_output: float


from dataclasses import dataclass
import os


@dataclass
class ElectricityContract:
    """
    Contains all contract-related cost parameters.

    All monetary values are in €cent/kWh or €/year unless stated otherwise.
    """

    # Contract type label used for GridCost tariff selection
    contract_type: str = "DynamicTariff"  # "DualTariff" or "DynamicTariff"

    # --- Dual tariff parameters (€cent/kWh) ---
    dual_cons_peak: float = 0.30          # €cent/kWh
    dual_cons_offpeak: float = 0.20       # €cent/kWh
    dual_inj_peak: float = -0.05    # €cent/kWh (negative = revenue)
    dual_inj_offpeak: float = 0.0          # €cent/kWh adder, if any
    dual_fix: float =100.7  # €/year

    # --- Capacity tariff (€/kW/year) ---
    capacity_tariff_rate: float = 40.0      # €/kW/year

    # --- Dynamic tariff formula parameters (Belpex in €/MWh) ---
    # Price model (€/MWh):
    #   consumption_price = multiplier * Belpex + adder_eur_per_mwh
    #   injection_price   = multiplier * Belpex + adder_eur_per_mwh
    #
    # GridCost will convert €/MWh -> €/kWh by /1000 internally.
    dynamic_cons_var_peak: float = 1.0            # €cent/kWh multiplier for consumption price
    dynamic_cons_var_offpeak: float = 1.0         # €cent/kWh multiplier for consumption price
    dynamic_cons_fix_peak: float = 0.0            # €cent/kWh adder for consumption price
    dynamic_cons_fix_offpeak: float = 0.0            # €cent/kWh adder for consumption price
    dynamic_inj_var_peak: float = 0.0             # €cent/kWh multiplier for injection price   
    dynamic_inj_var_offpeak: float = 0.0             # €cent/kWh multiplier for injection price   
    dynamic_inj_fix_peak: float = 0.0             # €cent/kWh adder for injection price
    dynamic_inj_fix_offpeak: float = 0.0             # €cent/kWh adder for injection price
    dynamic_fix: float = 31.8        # €/year

    # --- Other components (defaults can be overridden) ---
    data_management_cost: float = 13.95     # €/year
    purchase_rate_injection: float = 0.00414453    # €/kWh
    purchase_rate_consumption: float = 0.0538613   # €/kWh
    excise_duty: float = 0.0503288  # €/kWh
    energy_contribution: float = 0.0020417  # €/kWh
    green_power_fee: float = 0.0025        # €/kWh

    # TODO: allow to add other cost, both variable and fixed


    # --- Metadata (used for PDF import + caching; ignored by GridCost math) ---
    contract_id: str = ""          # stable ID used for pickle caching
    supplier: str = ""             # e.g., "MEGA", "EnergyVision", "Belvus"
    product_name: str = ""         # e.g., "Flow+ EL", "Stroom van ’t zeetje"
    meter_type: str = ""           # e.g., "mono", "bi"
    language: str = ""             # optional, e.g., "FR", "NL", "EN"
    valid_from: str = ""           # optional
    valid_to: str = ""             # optional
    source_pdf_path: str = ""      # optional
    source_pdf_sha256: str = ""    # optional
    parsed_at: str = ""            # optional (iso datetime)
    notes: str = ""                # optional

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_eu_number(value: str, *, factor: float = 1.0) -> float:
        """
        Parse a number written with European formatting from the PDF and
        apply an optional scaling factor (e.g. 0.01 to convert c€/kWh -> €/kWh).

        Handles both '.' and ',' as decimal/thousand separators.
        """
        s = re.sub(r"[^0-9,.\-]", "", str(value))
        if not s:
            raise ValueError(f"Could not parse number from {value!r}")

        if "," in s and "." in s:
            # assume last separator is decimal
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")  # 1.234,56 -> 1234.56
            else:
                s = s.replace(",", "")                    # 1,234.56 -> 1234.56
        else:
            if "," in s:
                s = s.replace(",", ".")

        return float(s) * factor

    def as_dict(self, *, include_metadata: bool = False) -> Dict[str, Any]:
        """Return a dict representation (optionally excluding metadata)."""
        d = asdict(self)
        if include_metadata:
            return d
        for k in (
            "contract_id",
            "supplier",
            "product_name",
            "meter_type",
            "valid_from",
            "valid_to",
            "source_pdf_path",
            "source_pdf_sha256",
            "parsed_at",
            "notes",
        ):
            d.pop(k, None)
        return d
    
    def _fingerprint_dict(self) -> Dict[str, Any]:
        """Stable dict used for cache comparison (round floats; ignore metadata)."""
        d = self.as_dict(include_metadata=False)
        for k, v in list(d.items()):
            if isinstance(v, float):
                d[k] = round(v, 12)
        return d
    # ------------------------------------------------------------------
    # PDF-based initialisers
    # ------------------------------------------------------------------
    @classmethod
    def from_mega_testachats_brussels_pdf(
        cls,
        pdf_path: str,
        *,
        contract_type: str = "DynamicTariff",
    ) -> "ElectricityContract":
        """
        Build an ElectricityContract from a Mega 'Offre spéciale Testachats'
        Brussels electricity contract PDF (e.g.
        'Mega-FR-EL-B2C-BX-102025-TA0525-Var.pdf').

        What is parsed (based on the price sheet layout of 10/2025):

        - Energy & injection prices from the first table:
            * 'Compteur mono-horaire  11.16  1.98'  (c€/kWh)
              -> dual_peak_tariff = dual_offpeak_tariff = 0.1116 €/kWh
              -> dual_injection_tariff = -0.0198 €/kWh (revenue) :contentReference[oaicite:2]{index=2}
        - Fixed annual fee 'Redevance fixe (€/an) 31.8'
              -> fixed_component_dynamic = 31.8 €/year (supplier part) :contentReference[oaicite:3]{index=3}
        - Excise + energy contribution from the tax table (band 0–3000 kWh):
              '5.03288  0.20417 c€/kWh'
              -> excise_duty_energy_contribution_rate = 0.0503288 + 0.0020417 €/kWh :contentReference[oaicite:4]{index=4}

        Other fields keep their default values and can be overridden manually.

        Requires the optional dependency `pdfplumber`:

            pip install pdfplumber
        """
        
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(pdf_path)

        pages_text: list[str] = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                pages_text.append(page.extract_text() or "")

        full_text = "\n".join(pages_text)
        lower = full_text.lower()

        # Basic sanity check that we have the expected document
        if "offre spéciale testachats" not in lower or "sibelga" not in lower:
            raise ValueError(
                "PDF does not look like a Mega 'Offre spéciale Testachats' "
                "Bruxelles electricity contract."
            )

        params: Dict[str, Any] = {"contract_type": contract_type}

        # --- 1) Energy & injection prices (c€/kWh) ------------------------
        # Row on page 1:
        #   'Compteur mono-horaire 11.16 1.98'
        m_mono = re.search(
            r"Compteur\s+mono-horaire\s+([0-9][0-9.,]*)\s+([0-9][0-9.,]*)",
            full_text,
            flags=re.IGNORECASE,
        )
        if m_mono:
            energy_eur_per_kwh = cls._parse_eu_number(m_mono.group(1), factor=0.01)
            injection_eur_per_kwh = cls._parse_eu_number(m_mono.group(2), factor=0.01)

            params["dual_peak_tariff"] = energy_eur_per_kwh
            params["dual_offpeak_tariff"] = energy_eur_per_kwh
            # Injection is revenue => negative cost in our convention
            params["dual_injection_tariff"] = -injection_eur_per_kwh

        # --- 2) Supplier fixed fee 'Redevance fixe (€/an)' ----------------
        m_fix = re.search(
            r"Redevance\s+fixe\s*\(€/an\)\s+([0-9][0-9.,]*)",
            full_text,
            flags=re.IGNORECASE,
        )
        if m_fix:
            fixed_fee = cls._parse_eu_number(m_fix.group(1), factor=1.0)
            params["fixed_component_dynamic"] = fixed_fee

        # --- 3) Excise + energy contribution (band 0–3000 kWh) -----------
        m_excise = re.search(
            r"Consommation\s+entre\s+0\s+et\s+3000\s+kWh\s+([0-9][0-9.,]*)\s+([0-9][0-9.,]*)",
            full_text,
            flags=re.IGNORECASE,
        )
        if m_excise:
            excise = cls._parse_eu_number(m_excise.group(1), factor=0.01)
            contribution = cls._parse_eu_number(m_excise.group(2), factor=0.01)
            params["excise_duty_energy_contribution_rate"] = excise + contribution

        return cls(**params)

    @classmethod
    def from_pdf(cls, pdf_path: str, **kwargs: any) -> "ElectricityContract":
        """
        Generic entry point.

        Currently implemented for:
        - Mega 'Offre spéciale Testachats' – Bruxelles (variable contract).

        You can later extend this method to dispatch on other providers/products.
        """
        return cls.from_mega_testachats_brussels_pdf(pdf_path, **kwargs)


import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, List, Any

import pdfplumber


# -----------------------------
# Helpers
# -----------------------------

_MONTHS_NL = {
    "januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "augustus": 8, "september": 9, "oktober": 10, "november": 11, "december": 12
}

def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _read_pdf_text(pdf_path: str) -> str:
    """
    Extract selectable text from a PDF.
    If your PDFs are scanned images, pass text_override to from_pdf (OCR output).
    """
    parts: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t.strip():
                parts.append(t)
    return "\n".join(parts)

def _normalize(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def _parse_number(s: str) -> float:
    """
    Parse European-style numbers:
      - "5,0329" -> 5.0329
      - "1.234,56" -> 1234.56
    """
    s = s.strip().replace("\u202f", " ").replace("\xa0", " ")
    s = s.replace("€", "").replace("c€", "").replace("€c", "")
    s = re.sub(r"[^\d,.\-+]", "", s)
    if s.count(",") and s.count("."):
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    return float(s)

def _cents_to_eur_per_kwh(cents: float) -> float:
    return cents / 100.0

def _detect_language(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["tariefkaart", "abonnement", "bijdrage", "leveringsovereenkomst"]):
        return "NL"
    if any(w in t for w in ["contrat", "abonnement", "contribution"]):
        return "FR"
    return ""

def _detect_supplier(text: str) -> str:
    t = text.lower()
    if "belvus" in t:
        return "Belvus"
    if "bolt" in t or "boltenergie" in t:
        return "Bolt"
    if "energyvision" in t:
        return "EnergyVision"
    return ""

def _detect_product_name(text: str, supplier: str = "") -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:60]:
        if re.search(r"\bFLOW\+?\s*EL\b", ln, flags=re.I):
            return "FLOW+ EL"
        if "Plenty Variabel Online" in ln:
            return "Plenty Variabel Online"
    # fallback: first short-ish line that is not supplier
    if supplier:
        for ln in lines[:80]:
            if supplier.lower() in ln.lower():
                continue
            if 3 < len(ln) < 80 and any(ch.isalpha() for ch in ln):
                return ln
    return ""

def _detect_validity(text: str) -> Tuple[str, str]:
    """
    Detect month+year like 'December 2025' and map to 'YYYY-MM-01'.
    valid_to intentionally left empty because tariff cards differ in validity rules.
    """
    m = re.search(r"\b(" + "|".join(_MONTHS_NL.keys()) + r")\s+(\d{4})\b", text, flags=re.I)
    if not m:
        return "", ""
    month_name = m.group(1).lower()
    year = int(m.group(2))
    month = _MONTHS_NL.get(month_name)
    if not month:
        return "", ""
    return f"{year:04d}-{month:02d}-01", ""


# -----------------------------
# Belpex formula extraction (DynamicTariff)
# -----------------------------

# Matches e.g.:
#  - "Belpex * 1,1192 + 13,94"
#  - "Belpex * 0,94 - 11,33"
#  - "Belpex_RLP x 1,1180) + €13,30/MWh"
#  - "Belpex_SPP x 1) + €-20/MWh"
_FORMULA_RE = re.compile(
    r"Belpex(?:_[A-Za-z]+)?\s*(?:\*|x)\s*(?P<mult>[0-9]+(?:[.,][0-9]+)?)\s*\)?\s*(?P<op>[+-])\s*€?\s*(?P<add>[+-]?[0-9]+(?:[.,][0-9]+)?)",
    flags=re.I,
)

def _extract_belpex_formulas(text: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns:
      {'cons': [{'period': 'peak'|'offpeak'|None, 'mult': float, 'add': float}, ...],
       'inj':  [...]}

    mult is unitless, add is in €/MWh.
    """
    cons: List[Dict[str, Any]] = []
    inj: List[Dict[str, Any]] = []

    for m in _FORMULA_RE.finditer(text):
        mult = _parse_number(m.group("mult"))
        add_raw = _parse_number(m.group("add"))
        op = m.group("op")
        add = add_raw if op == "+" else -add_raw

        start = m.start()
        ctx = text[max(0, start - 180):start].lower()
        snippet = text[m.start():m.end()].lower()

        # category
        is_inj = False
        if "spp" in snippet or "spp" in ctx:
            is_inj = True
        elif "rlp" in snippet or "rlp" in ctx:
            is_inj = False
        elif any(k in ctx for k in ["inject", "teruglever", "teruglevering", "injectiet"]):
            is_inj = True
        elif any(k in ctx for k in ["energiekost", "verkoopsprijs", "afname", "consumpt"]):
            is_inj = False

        # period (best-effort)
        period = None
        ctx2 = text[max(0, start - 80):m.end() + 40].lower()
        if "nacht" in ctx2 and "dag" not in ctx2:
            period = "offpeak"
        elif "dag" in ctx2 and "nacht" not in ctx2:
            period = "peak"

        rec = {"period": period, "mult": mult, "add": add}
        (inj if is_inj else cons).append(rec)

    return {"cons": cons, "inj": inj}

def _pick_peak_off(records: List[Dict[str, Any]]) -> Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]:
    """
    Choose (mult, add) for peak and offpeak.
    If only period-less records exist, apply the same formula to both.
    """
    peak = next(((r["mult"], r["add"]) for r in records if r["period"] == "peak"), None)
    off = next(((r["mult"], r["add"]) for r in records if r["period"] == "offpeak"), None)

    if peak is None and off is None:
        if not records:
            return None, None
        val = (records[0]["mult"], records[0]["add"])
        return val, val

    if peak is None:
        peak = off
    if off is None:
        off = peak
    return peak, off


# -----------------------------
# Other fee extraction
# -----------------------------

def _extract_subscription_annual_eur(text: str) -> Optional[float]:
    """
    Extract subscription/abonnement cost and return €/year.
    Handles both €/year and €/month (converted).
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # annual-ish lines
    for ln in lines:
        l = ln.lower()
        if "abonn" in l and "maand" not in l and ("jaar" in l or "jaarlijk" in l or "/jaar" in l):
            m = re.search(r"€\s*([0-9]+[.,]?[0-9]*)", ln)
            if m:
                return _parse_number(m.group(1))

    # monthly lines
    for ln in lines:
        l = ln.lower()
        if "abonn" in l and "maand" in l:
            m = re.search(r"€\s*([0-9]+[.,]?[0-9]*)", ln)
            if m:
                return round(_parse_number(m.group(1)) * 12, 6)

    # fallback regex (multi-line)
    m = re.search(r"Abonnement(?:s)?kost.{0,80}?€\s*([0-9]+[.,]?[0-9]*).{0,20}?(?:/maand|maand)", text, flags=re.I | re.S)
    if m:
        return round(_parse_number(m.group(1)) * 12, 6)

    m = re.search(r"(?:Jaarlijkse\s+)?abonnements(?:vergoeding|kost).{0,60}?€\s*([0-9]+[.,]?[0-9]*)", text, flags=re.I | re.S)
    if m and re.search(r"jaar", m.group(0), flags=re.I):
        return _parse_number(m.group(1))

    return None

def _extract_cents_per_kwh(text: str, label_patterns: List[str]) -> Optional[float]:
    """
    Find a 'c€/kWh' number near one of the labels. Returns €/kWh.
    """
    for lab in label_patterns:
        # examples: "€c5,0329/kWh", "c€/kWh 0,2042"
        m = re.search(lab + r".{0,100}?(?:€c|c€|c€/)\s*([0-9]+[.,][0-9]+)", text, flags=re.I | re.S)
        if m:
            return _cents_to_eur_per_kwh(_parse_number(m.group(1)))
        m = re.search(lab + r".{0,100}?([0-9]+[.,][0-9]+)\s*c€/?kWh", text, flags=re.I | re.S)
        if m:
            return _cents_to_eur_per_kwh(_parse_number(m.group(1)))
    return None

def _extract_green_fees(text: str, region: str = "VL") -> Tuple[Optional[float], Optional[float]]:
    """
    Returns (gsc_eur_per_kwh, wkk_eur_per_kwh) in €/kWh.
    - Flow-style: "GSC €c 1,18" and "WKK €c 0,42"
    - Plenty-style: region table "Groene certificaten ... 1,17 3,00 2,91" + "WKK (c€/kWh) 0,42 ..."
    """
    region = region.upper()

    # explicit labels (most robust)
    m = re.search(r"\bGSC\b\s*€c\s*([0-9]+[.,][0-9]+)", text, flags=re.I)
    gsc = _cents_to_eur_per_kwh(_parse_number(m.group(1))) if m else None
    m = re.search(r"\bWKK\b\s*€c\s*([0-9]+[.,][0-9]+)", text, flags=re.I)
    wkk = _cents_to_eur_per_kwh(_parse_number(m.group(1))) if m else None
    if gsc is not None or wkk is not None:
        return gsc, wkk

    # region table (Groene certificaten)
    gsc = None
    m = re.search(
        r"Groene certificaten.*?([0-9]+[.,][0-9]+)\s+([0-9]+[.,][0-9]+)\s+([0-9]+[.,][0-9]+)",
        text,
        flags=re.I | re.S,
    )
    if m:
        vals = [_parse_number(m.group(i)) for i in (1, 2, 3)]
        idx = {"VL": 0, "WAL": 1, "BRU": 2}.get(region, 0)
        gsc = _cents_to_eur_per_kwh(vals[idx])

    # WKK table label
    wkk = None
    m = re.search(r"WKK\s*\(c.?/?kWh\).*?([0-9]+[.,][0-9]+)", text, flags=re.I | re.S)
    if m:
        wkk = _cents_to_eur_per_kwh(_parse_number(m.group(1)))

    return gsc, wkk


# -----------------------------
# Add this method to your ElectricityContract class
# -----------------------------
def _build_notes(contract, formulas: Dict[str, Any], region: str) -> str:
    parts = []
    if formulas["cons"] or formulas["inj"]:
        parts.append("Parsed Belpex formulas")
        parts.append(f"cons: {contract.dynamic_cons_var_peak}*Belpex + {contract.dynamic_cons_fix_peak} €/MWh")
        parts.append(f"inj: {contract.dynamic_inj_var_peak}*Belpex + {contract.dynamic_inj_fix_peak} €/MWh")
    parts.append(f"region={region}")
    return " | ".join(parts)


# Paste the following inside class ElectricityContract:
#
# @classmethod
# def from_pdf(cls, ...): ...
#
# (or copy/paste the function body into your classmethod)

def electricity_contract_from_pdf(
    cls,
    pdf_path: str,
    *,
    region: str = "VL",
    meter_type: str = "",
    text_override: Optional[str] = None,
):
    """
    Create an ElectricityContract from a tariff card/contract PDF.

    What it fills (when found in the PDF):
      - contract_type = "DynamicTariff" if a Belpex formula is detected
      - dynamic_* multipliers/adders (€/MWh)
      - dynamic_fix / dual_fix (subscription, converted to €/year)
      - excise_duty, energy_contribution (€/kWh)
      - green_power_fee = GSC+WKK (€/kWh)
      - metadata fields: supplier/product/valid_from/sha/parsed_at/contract_id

    Everything not found stays at the class default values.
    """
    path = Path(pdf_path)
    sha = _sha256_file(path)

    text = text_override if text_override is not None else _read_pdf_text(str(path))
    text = _normalize(text)

    contract = cls()  # start from defaults

    # --- metadata ---
    contract.source_pdf_path = str(path)
    contract.source_pdf_sha256 = sha
    contract.parsed_at = datetime.now().isoformat(timespec="seconds")
    contract.language = _detect_language(text)
    if meter_type:
        contract.meter_type = meter_type

    contract.supplier = _detect_supplier(text)
    contract.product_name = _detect_product_name(text, supplier=contract.supplier)
    vf, vt = _detect_validity(text)
    contract.valid_from, contract.valid_to = vf, vt
    base = "|".join([contract.supplier, contract.product_name, contract.valid_from, sha[:12]])
    contract.contract_id = hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]

    # --- tariff type + formulas ---
    formulas = _extract_belpex_formulas(text)
    if formulas["cons"] or formulas["inj"]:
        contract.contract_type = "DynamicTariff"

        cons_peak, cons_off = _pick_peak_off(formulas["cons"])
        if cons_peak:
            contract.dynamic_cons_var_peak, contract.dynamic_cons_fix_peak = cons_peak
        if cons_off:
            contract.dynamic_cons_var_offpeak, contract.dynamic_cons_fix_offpeak = cons_off

        inj_peak, inj_off = _pick_peak_off(formulas["inj"])
        if inj_peak:
            contract.dynamic_inj_var_peak, contract.dynamic_inj_fix_peak = inj_peak
        if inj_off:
            contract.dynamic_inj_var_offpeak, contract.dynamic_inj_fix_offpeak = inj_off
    else:
        contract.contract_type = "DualTariff"
        # Extend here if you need fixed day/night parsing for suppliers that do not give a Belpex formula.

    # --- subscription cost ---
    sub = _extract_subscription_annual_eur(text)
    if sub is not None:
        if contract.contract_type == "DynamicTariff":
            contract.dynamic_fix = sub
        else:
            contract.dual_fix = sub

    # --- taxes/fees (optional overrides) ---
    exc = _extract_cents_per_kwh(text, [r"Bijzondere accijns", r"accijns op Energie"])
    if exc is not None:
        contract.excise_duty = exc

    eco = _extract_cents_per_kwh(text, [r"Bijdrage op Energie", r"Bijdrage op de energie"])
    if eco is not None:
        contract.energy_contribution = eco

    gsc, wkk = _extract_green_fees(text, region=region)
    if gsc is not None or wkk is not None:
        contract.green_power_fee = (gsc or 0.0) + (wkk or 0.0)

    contract.notes = _build_notes(contract, formulas, region=region)
    return contract


# If you want this without copy/pasting into the class body:
# ElectricityContract.from_pdf = classmethod(electricity_contract_from_pdf)
