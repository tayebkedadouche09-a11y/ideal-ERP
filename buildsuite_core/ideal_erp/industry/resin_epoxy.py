"""Generic resin/epoxy technical estimation.

This is an IDEAIL-native layer. It does not duplicate BOQ, Item, Stock or
Accounting documents; it only calculates a technical quantity/cost draft that
can be confirmed into the canonical ERPNext/BuildSuite workflow.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EpoxyEstimateInput:
    area_m2: float
    thickness_mm: float
    density_kg_per_l: float
    volume_solids: float = 1.0
    waste_pct: float = 5.0
    primer_kg_per_m2: float = 0.0
    resin_share: float = 0.70
    hardener_share: float = 0.30
    material_cost_per_kg: float = 0.0
    primer_cost_per_kg: float = 0.0
    labor_hours_per_10m2: float = 0.0
    labor_rate_per_hour: float = 0.0
    equipment_cost: float = 0.0

    def validate(self) -> None:
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than zero")
        if self.thickness_mm < 0:
            raise ValueError("thickness_mm cannot be negative")
        if self.density_kg_per_l <= 0:
            raise ValueError("density_kg_per_l must be greater than zero")
        if not 0 < self.volume_solids <= 1:
            raise ValueError("volume_solids must be in (0, 1]")
        if self.waste_pct < 0:
            raise ValueError("waste_pct cannot be negative")
        if abs((self.resin_share + self.hardener_share) - 1.0) > 1e-9:
            raise ValueError("resin_share + hardener_share must equal 1")


@dataclass(frozen=True, slots=True)
class EpoxyEstimate:
    coating_mix_kg: float
    resin_kg: float
    hardener_kg: float
    primer_kg: float
    labor_hours: float
    material_cost: float
    labor_cost: float
    equipment_cost: float
    total_cost: float


def estimate_epoxy_job(inp: EpoxyEstimateInput) -> EpoxyEstimate:
    inp.validate()

    # For a 1 mm layer, 1 m² contains 1 litre of geometric volume.
    base_mix_kg = (
        inp.area_m2
        * inp.thickness_mm
        * inp.density_kg_per_l
        / inp.volume_solids
    )
    coating_mix_kg = base_mix_kg * (1 + inp.waste_pct / 100)
    resin_kg = coating_mix_kg * inp.resin_share
    hardener_kg = coating_mix_kg * inp.hardener_share

    primer_kg = inp.area_m2 * inp.primer_kg_per_m2 * (1 + inp.waste_pct / 100)
    labor_hours = inp.area_m2 / 10 * inp.labor_hours_per_10m2

    material_cost = (
        coating_mix_kg * inp.material_cost_per_kg
        + primer_kg * inp.primer_cost_per_kg
    )
    labor_cost = labor_hours * inp.labor_rate_per_hour
    total_cost = material_cost + labor_cost + inp.equipment_cost

    return EpoxyEstimate(
        coating_mix_kg=coating_mix_kg,
        resin_kg=resin_kg,
        hardener_kg=hardener_kg,
        primer_kg=primer_kg,
        labor_hours=labor_hours,
        material_cost=material_cost,
        labor_cost=labor_cost,
        equipment_cost=inp.equipment_cost,
        total_cost=total_cost,
    )
