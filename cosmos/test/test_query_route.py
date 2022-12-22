from app.schemas import SearchResponse
import pytest
import httpx

from app.main import app

@pytest.skip("Not finished, doesn't run end to end")
async def test_raw_lookup() -> None:
    """Test searching Alamo Square Park."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/osm/query?query=alamo+square+park")
        assert response.status_code == 200
        json = response.json()
        sr = SearchResponse(**json)
        assert sr.parse_result.geom
        assert sr.parse_result.geom.features[0].properties["name"] == "Alamo Square"  # type: ignore
        assert sr.parse_result.entities[0].lookup == "alamo square park"