
import sys
from types import ModuleType
from collections import OrderedDict

# Fix mode.utils.compat.OrderedDict
try:
    import mode.utils.compat
    mode.utils.compat.OrderedDict = OrderedDict
except ImportError:
    m = ModuleType("mode.utils.compat")
    sys.modules["mode.utils.compat"] = m
    m.OrderedDict = OrderedDict

# Fix mode.utils.typing.NoReturn and Deque and AsyncContextManager and Counter and AsyncGenerator
try:
    import mode.utils.typing
    from typing import NoReturn, Deque, AsyncContextManager, Counter, AsyncGenerator
    mode.utils.typing.NoReturn = NoReturn
    mode.utils.typing.Deque = Deque
    mode.utils.typing.AsyncContextManager = AsyncContextManager
    mode.utils.typing.Counter = Counter
    mode.utils.typing.AsyncGenerator = AsyncGenerator
except ImportError:
    m = ModuleType("mode.utils.typing")
    sys.modules["mode.utils.typing"] = m
    from typing import NoReturn, Deque, AsyncContextManager, Counter, AsyncGenerator
    m.NoReturn = NoReturn
    m.Deque = Deque
    m.AsyncContextManager = AsyncContextManager
    m.Counter = Counter
    m.AsyncGenerator = AsyncGenerator

# Fix mode.utils.contexts.AsyncContextManager and nullcontext and asynccontextmanager
try:
    import mode.utils.contexts
    from typing import AsyncContextManager
    from contextlib import nullcontext, asynccontextmanager
    mode.utils.contexts.AsyncContextManager = AsyncContextManager
    mode.utils.contexts.nullcontext = nullcontext
    mode.utils.contexts.asynccontextmanager = asynccontextmanager
except ImportError:
    m = ModuleType("mode.utils.contexts")
    sys.modules["mode.utils.contexts"] = m
    from typing import AsyncContextManager
    from contextlib import nullcontext, asynccontextmanager
    m.AsyncContextManager = AsyncContextManager
    m.nullcontext = nullcontext
    m.asynccontextmanager = asynccontextmanager
