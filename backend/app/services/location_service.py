import httpx


async def reverse_geocode(latitude: float, longitude: float) -> dict:
    """
    Convert latitude and longitude into location details.
    """

    url = "https://nominatim.openstreetmap.org/reverse"

    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "jsonv2",
        "addressdetails": 1,
    }

    headers = {
        "User-Agent": "Farmer-Advisory-System/1.0"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            url,
            params=params,
            headers=headers,
        )

        response.raise_for_status()

        data = response.json()

    address = data.get("address", {})

    state = address.get("state")

    district = (
        address.get("state_district")
        or address.get("county")
        or address.get("district")
    )

    village = (
        address.get("village")
        or address.get("town")
        or address.get("city")
        or address.get("municipality")
    )

    return {
        "state": state,
        "district": district,
        "village": village,
        "display_name": data.get("display_name"),
    }