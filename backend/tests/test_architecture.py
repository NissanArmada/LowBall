import pytest
import asyncio
from models.schemas import NegotiationState, ListingMetadata, AnalyticalData, Message
from agents.unified import get_windowed_history
from services.resilience import CircuitBreaker, CircuitBreakerOpen
from core.config import settings

@pytest.mark.asyncio
async def test_memory_windowing_enforcement():
    """
    Architectural Mandate: Conversation history MUST use a sliding window.
    """
    # Create a state with 20 messages (exceeding the default window of 10)
    history = [Message(role="user", content=f"Msg {i}") for i in range(20)]
    state = NegotiationState(
        session_id="test_window",
        item_metadata=ListingMetadata(
            item_name="Test", original_listing_price=100, suggested_low_price=50, 
            suggested_high_price=80, condition="New", description="test"
        ),
        analytical_data=AnalyticalData(calculated_fair_market_avg=70, price_volatility=0.1, recommended_walk_away_price=90),
        history=history,
        current_lowball_price=50
    )
    
    # Act
    windowed_str = get_windowed_history(state, window_size=5)
    
    # Assert
    # Should only contain the last 5 messages
    lines = windowed_str.split("\n")
    assert len(lines) == 5
    assert "Msg 15" in lines[0]
    assert "Msg 19" in lines[-1]
    assert "Msg 0" not in windowed_str

@pytest.mark.asyncio
async def test_circuit_breaker_functionality():
    """
    Architectural Mandate: External calls MUST be wrapped in a Resilience Layer (Circuit Breaker).
    """
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    
    async def failing_func():
        raise Exception("API Down")

    # 1. First failure
    with pytest.raises(Exception):
        await breaker.call(failing_func)
    assert breaker.is_open is False

    # 2. Second failure - should open the breaker
    with pytest.raises(Exception):
        await breaker.call(failing_func)
    assert breaker.is_open is True

    # 3. Third call - should raise CircuitBreakerOpen immediately without calling func
    with pytest.raises(CircuitBreakerOpen):
        await breaker.call(failing_func)

@pytest.mark.asyncio
async def test_circuit_breaker_recovery():
    """Verify breaker eventually closes after timeout."""
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
    
    async def failing_func():
        raise Exception("API Down")
    
    async def success_func():
        return "Success"

    # Open breaker
    with pytest.raises(Exception):
        await breaker.call(failing_func)
    assert breaker.is_open is True

    # Wait for recovery timeout
    await asyncio.sleep(0.2)

    # Breaker should allow recovery
    res = await breaker.call(success_func)
    assert res == "Success"
    assert breaker.is_open is False

@pytest.mark.asyncio
async def test_async_persistence_integrity(test_store):
    """
    Architectural Mandate: Use non-blocking database drivers for all state management.
    """
    # This test verifies the store can handle async save/load without blocking the loop
    state = NegotiationState(
        session_id="test_async",
        item_metadata=ListingMetadata(
            item_name="Async Item", original_listing_price=100, suggested_low_price=50, 
            suggested_high_price=80, condition="Used", description="Testing async"
        ),
        analytical_data=AnalyticalData(calculated_fair_market_avg=70, price_volatility=0.1, recommended_walk_away_price=90),
        history=[],
        current_lowball_price=0
    )
    
    # Save
    await test_store.save_state(state)
    
    # Load
    loaded_state = await test_store.load_state("test_async")
    
    assert loaded_state is not None
    assert loaded_state.item_metadata.item_name == "Async Item"
    assert loaded_state.session_id == "test_async"
