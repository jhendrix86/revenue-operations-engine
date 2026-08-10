"""
Revenue Operations Engine smoke tests
"""
import pytest


@pytest.mark.asyncio
async def test_app_instantiation():
    """Verify FastAPI app instantiates without error"""
    from app.main import app
    assert app is not None
    assert app.title == "Revenue Operations Engine"


@pytest.mark.asyncio
async def test_models_import():
    """Verify core models import without error"""
    from app.models import Subscription, Payment, Refund
    assert Subscription is not None
    assert Payment is not None
    assert Refund is not None
