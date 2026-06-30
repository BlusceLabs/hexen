import asyncio


def get_event_loop():
    """Get or create an event loop safely.
    
    This function tries to get the current running loop first,
    then falls back to getting the event loop for the current thread,
    and finally creates a new one if necessary.
    """
    try:
        # Try to get the running loop (works in async context)
        return asyncio.get_running_loop()
    except RuntimeError:
        # Not in async context, get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
            return loop
        except RuntimeError:
            # Create new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
