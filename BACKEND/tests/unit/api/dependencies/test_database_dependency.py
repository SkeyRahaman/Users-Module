import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.database import get_db

@pytest.mark.asyncio
async def test_get_db_yields_session():
    # Create async generator from your dependency
    gen = get_db()

    # Get the yielded value (the db session)
    db = await gen.__anext__()
    
    # Assert db is an instance of SessionLocal or compatible (you can adjust depending on your ORM)
    assert isinstance(db, AsyncSession) or hasattr(db, "execute")

    # Advance generator to completion and confirm it closes properly
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()
