"""The tests for the demo stt component."""
from http import HTTPStatus

import pytest

from homeassistant.components import stt
from homeassistant.components.demo import DOMAIN as DEMO_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry
from tests.typing import ClientSessionGenerator


@pytest.fixture
async def setup_legacy_platform(hass: HomeAssistant) -> None:
    """Set up legacy demo platform."""
    assert await async_setup_component(hass, stt.DOMAIN, {"stt": {"platform": "demo"}})
    await hass.async_block_till_done()


@pytest.fixture
async def setup_config_entry(hass: HomeAssistant) -> None:
    """Set up demo component from config entry."""
    config_entry = MockConfigEntry(domain=DEMO_DOMAIN)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


@pytest.mark.usefixtures("setup_legacy_platform")
async def test_demo_settings(hass_client: ClientSessionGenerator) -> None:
    """Test retrieve settings from demo provider."""
    client = await hass_client()

    response = await client.get("/api/stt/demo")
    response_data = await response.json()

    assert response.status == HTTPStatus.OK
    assert response_data == {
        "languages": ["en", "de"],
        "bit_rates": [16],
        "sample_rates": [16000, 44100],
        "formats": ["wav"],
        "codecs": ["pcm"],
        "channels": [2],
    }


@pytest.mark.usefixtures("setup_legacy_platform")
async def test_demo_speech_no_metadata(hass_client: ClientSessionGenerator) -> None:
    """Test retrieve settings from demo provider."""
    client = await hass_client()

    response = await client.post("/api/stt/demo", data=b"Test")
    assert response.status == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures("setup_legacy_platform")
async def test_demo_speech_wrong_metadata(hass_client: ClientSessionGenerator) -> None:
    """Test retrieve settings from demo provider."""
    client = await hass_client()

    response = await client.post(
        "/api/stt/demo",
        headers={
            "X-Speech-Content": (
                "format=wav; codec=pcm; sample_rate=8000; bit_rate=16; channel=1;"
                " language=de"
            )
        },
        data=b"Test",
    )
    assert response.status == HTTPStatus.UNSUPPORTED_MEDIA_TYPE


@pytest.mark.usefixtures("setup_legacy_platform")
async def test_demo_speech(hass_client: ClientSessionGenerator) -> None:
    """Test retrieve settings from demo provider."""
    client = await hass_client()

    response = await client.post(
        "/api/stt/demo",
        headers={
            "X-Speech-Content": (
                "format=wav; codec=pcm; sample_rate=16000; bit_rate=16; channel=2;"
                " language=de"
            )
        },
        data=b"Test",
    )
    response_data = await response.json()

    assert response.status == HTTPStatus.OK
    assert response_data == {"text": "Turn the Kitchen Lights on", "result": "success"}


@pytest.mark.usefixtures("setup_config_entry")
async def test_config_entry_demo_speech(
    hass_client: ClientSessionGenerator, hass: HomeAssistant
) -> None:
    """Test retrieve settings from demo provider from config entry."""
    client = await hass_client()

    response = await client.post(
        "/api/stt/demo",
        headers={
            "X-Speech-Content": (
                "format=wav; codec=pcm; sample_rate=16000; bit_rate=16; channel=2;"
                " language=de"
            )
        },
        data=b"Test",
    )
    response_data = await response.json()

    assert response.status == HTTPStatus.OK
    assert response_data == {"text": "Turn the Kitchen Lights on", "result": "success"}
