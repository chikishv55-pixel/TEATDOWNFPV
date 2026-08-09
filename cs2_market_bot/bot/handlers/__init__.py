from .start import router as start_router
from .help import router as help_router
from .signals import router as signals_router
from .premium import router as premium_router

__all__ = [
    "start_router",
    "help_router",
    "signals_router",
    "premium_router",
]
