"""
Soil intelligence service.

This service is responsible for obtaining soil information based on
farm latitude and longitude.
"""

from typing import Any


async def get_soil_information(
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """
    Get location-based soil information.

    External soil data providers will be integrated here.
    """

    # Validate coordinates
    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not -180 <= longitude <= 180:
        raise ValueError("Invalid longitude")

    return {
        "ph": None,
        "nitrogen": None,
        "phosphorus": None,
        "potassium": None,
        "moisture": None,
        "soil_type": None,
        "source": "Location-based soil intelligence provider pending",
    }