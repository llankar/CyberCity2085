"""Small persistent base and deployment-vehicle upgrade catalogue."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BaseUpgrade:
    id: str; name: str; cost: int; description: str; effect: str


BASE_UPGRADES = (
    BaseUpgrade("hangar", "Hangar Expansion", 0, "Increase operative capacity through the four Hangar levels.", "SQUAD CAPACITY +1"),
    BaseUpgrade("trauma_center", "Trauma Stabilization Center", 12_000, "Reduces recovery time after missions.", "RECOVERY -1 DAY"),
    BaseUpgrade("rapid_fabricator", "Rapid Fabricator", 18_000, "Reduces ordinary equipment purchase prices.", "EQUIPMENT COST -10%"),
    BaseUpgrade("signal_array", "Strategic Signal Array", 25_000, "Improves mission intelligence before deployment.", "MISSION INTEL +1"),
)

VEHICLE_UPGRADES = (
    BaseUpgrade("vector_engines", "Vector Engines", 9_000, "Faster insertion shortens mission duration and improves opening tempo.", "MISSION DURATION -1 / INIT +1"),
    BaseUpgrade("field_medevac", "Field Medevac Suite", 16_000, "Once per mission, stabilizes the first operative who would otherwise die.", "1 EMERGENCY SAVE"),
    BaseUpgrade("heavy_strike", "Heavy Strike Hardpoint", 22_000, "Provides one high-damage support strike per mission.", "1 HEAVY STRIKE"),
    BaseUpgrade("armored_cradle", "Armored Deployment Cradle", 14_000, "Protects the squad during a hostile insertion.", "DEPLOYMENT DEFENSE +2"),
)
