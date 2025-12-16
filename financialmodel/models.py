from dataclasses import dataclass
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

    All monetary values are in €/kWh or €/year unless stated otherwise.
    """

    # Contract type label used for GridCost tariff selection
    contract_type: str = "DynamicTariff"  # "DualTariff" or "DynamicTariff"

    # --- Dual tariff parameters (€/kWh) ---
    dual_peak_tariff: float = 0.30          # example
    dual_offpeak_tariff: float = 0.20       # example
    dual_injection_tariff: float = -0.05    # €/kWh (negative = revenue)
    dual_fixed_tariff: float = 0.0          # €/kWh adder, if any

    # --- Capacity tariff (€/kW/year) ---
    capacity_tariff_rate: float = 40.0      # example

    # --- Other components (defaults can be overridden) ---
    data_management_cost: float = 13.95     # €/year
    purchase_rate_injection: float = 0.00414453    # €/kWh
    purchase_rate_consumption: float = 0.0538613   # €/kWh
    excise_duty_energy_contribution_rate: float = (0.0503288 + 0.0020417)  # €/kWh
    fixed_component_dual: float = 111.3     # €/year
    fixed_component_dynamic: float = 100.7  # €/year

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

    def as_dict(self) -> dict[str, any]:
        """
        Convenience method used by some cost functions to convert the contract
        into kwargs for GridCost.
        """
        return {
            "contract_type": self.contract_type,
            "dual_peak_tariff": self.dual_peak_tariff,
            "dual_offpeak_tariff": self.dual_offpeak_tariff,
            "dual_injection_tariff": self.dual_injection_tariff,
            "dual_fixed_tariff": self.dual_fixed_tariff,
            "capacity_tariff_rate": self.capacity_tariff_rate,
            "data_management_cost": self.data_management_cost,
            "purchase_rate_injection": self.purchase_rate_injection,
            "purchase_rate_consumption": self.purchase_rate_consumption,
            "excise_duty_energy_contribution_rate": self.excise_duty_energy_contribution_rate,
            "fixed_component_dual": self.fixed_component_dual,
            "fixed_component_dynamic": self.fixed_component_dynamic,
        }

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


