# CLAUDE.md — miros

This file provides guidance to AI coding agents (such as Claude Code) when working with code in this repository.

`miros` is a statechart (hierarchical state machine) library for Python — an implementation of Miro Samek's event-processing algorithm. You write states as plain functions and the library handles entry/exit/init choreography, transitions, and (optionally) threading and publish/subscribe.

## This is a maintained fork

This repository is a fork of [`aleph2c/miros`](https://github.com/aleph2c/miros) (author: Scott Volk). Treat upstream as the source of truth for design and style:

- **Keep every change minimal and surgical.** Prefer the smallest diff that solves the problem; avoid refactors, reformatting, or churn that increases divergence from upstream.
- **Match the existing code style** rather than imposing new conventions — changes should read as if they could be contributed back to upstream.
- Keep the public API (`miros/__init__.py`) stable; adding to it is a deliberate decision, not a side effect.
- Do not introduce dependencies on, or references to, any external/downstream project. This library stands on its own.

## Setup & tests

```bash
pip install -e .            # editable install for local work
pytest                      # run the suite from the repo root
```

- Test config lives in `pytest.ini`; it sets `-p no:logging` and `--ignore=examples` (the examples dir contains runnable demos, not tests, and pytest would otherwise recurse into it).
- Tests are in `test/` as `*_test.py`. `examples/` holds standalone, runnable demonstrations — keep them working when you touch public behavior; they double as documentation.

## Branch workflow

- AI-agent changes happen on dedicated `claude/*` branches, never directly on `master`.
- `master` tracks the fork's mainline; keep it clean so it stays easy to compare against upstream.

## Architecture

The library is small — four source files do the real work, under `miros/`:

### `event.py` — the event vocabulary
- `Event(signal=...)` — the messages a chart processes (may carry a `payload`).
- `signals` — an auto-enumerating signal registry; referencing `signals.SOME_NAME` defines it on first use. The framework reserves `ENTRY_SIGNAL`, `EXIT_SIGNAL`, `INIT_SIGNAL`.
- `return_status` — the enum a state function returns (`HANDLED`, `IGNORED`, `TRAN`, `SUPER`, …).

### `hsm.py` — the event processor (no threads)
The core algorithm and the queue-based, manually-pumped chart:
- `HsmEventProcessor` — `start_at(state)`, `dispatch(event)`, `trans(state)` (transition), and `top` (the implicit root state).
- `InstrumentedHsmEventProcessor` — adds **spy** (full internal trace: every signal, entry/exit, hook) and **trace** (one line per state-to-state transition). Toggle live printing with `chart.live_spy`/`chart.live_trace`; retrieve buffers with `chart.spy()` / `chart.trace()`. `scribble(...)` injects a note into the spy stream.
- `HsmWithQueues` — adds fifo/lifo event queues; you advance it yourself with `next_rtc()` / `complete_circuit()`. Use this when you want full control of the run-to-completion loop and no background thread.
- Helpers: `spy_on` (the decorator every state function wears), `pp` (pretty-print spy output), `stripped` (context manager to temporarily drop instrumentation).

### `activeobject.py` — threaded charts + pub/sub
- `ActiveObject` (extends `HsmWithQueues`) — runs its own thread with an event queue. `start_at(state)` launches it; `post_fifo`/`post_lifo` enqueue events (with optional `period`/`times` for repeats); `subscribe`/`publish` connect charts over a shared "active fabric"; `defer`/`recall` park and replay events.
- `Factory` — build a chart programmatically (register states and signal handlers) instead of hand-writing decorated state functions.
- `ActiveObjectWithAttributes` / `FactoryWithAttributes` / `ThreadSafeAttributes` — mix in lock-guarded attributes for safe cross-thread access.

### `thread_safe_attributes.py`
- `MetaThreadSafeAttributes` — the metaclass implementing the descriptor-based, lock-guarded attributes used above.

(`singleton.py`, `foreign.py` are small supporting utilities.)

## Writing a state

A state is a function decorated with `@spy_on`, taking `(chart, e)` and returning a `return_status`:

```python
from miros import spy_on, signals, return_status, Event

@spy_on
def some_state(chart, e):
    if e.signal == signals.ENTRY_SIGNAL:
        # set up on entry
        return return_status.HANDLED
    elif e.signal == signals.SOME_EVENT:
        return chart.trans(other_state)          # transition
    elif e.signal == signals.EXIT_SIGNAL:
        # tear down on exit
        return return_status.HANDLED
    # not handled here -> bubble up to the parent state
    chart.temp.fun = parent_state
    return return_status.SUPER
```

Key rules:
- Return `return_status.HANDLED` when you consume an event, `chart.trans(target)` to transition, or set `chart.temp.fun = <parent>` and return `return_status.SUPER` to delegate to the superstate (`top` is the ultimate parent).
- Handle `ENTRY_SIGNAL` / `EXIT_SIGNAL` for setup/teardown and `INIT_SIGNAL` for a state's default substate transition.
- The spy/trace instrumentation is the primary debugging tool — when behavior is surprising, print `chart.spy()` to see the exact event-processing path.

## Conventions

- Don't swallow exceptions silently; if a handler must catch, leave a comment justifying why dropping the error is safe.
- When changing event-processing semantics, add or update a `test/*_test.py` case and keep the relevant `examples/` demo runnable — those are how upstream documents behavior.
