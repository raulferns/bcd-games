#!/usr/bin/env python3
"""Refuse to compile host heap or code-buffer addresses as guest code.

When host PC leaks into State.rip during process detach (e.g. 0x7c-0x7f host heap band
or FEX code buffer), FEX previously logged [iOS-bogusrip] and continued compiling host
memory into x86, which entered infinite JIT spin loops.
Returning 0 immediately raises a fault and stops the spin.
"""
from pathlib import Path
import sys

MARKER = "madeira-bcd: refuse to compile host heap"
ANCHOR = '''        LogMan::Msg::EFmt("[callret-chain] depth_used={:#x} nonzero={} (sp={:#x} base={:#x})", CRBase + FEXCore::Core::InternalThreadState::CALLRET_DEFAULT_OFFSET - CRSp,
                          NonZero, CRSp, CRBase);
      }
    }
  }'''

REPLACEMENT = '''        LogMan::Msg::EFmt("[callret-chain] depth_used={:#x} nonzero={} (sp={:#x} base={:#x})", CRBase + FEXCore::Core::InternalThreadState::CALLRET_DEFAULT_OFFSET - CRSp,
                          NonZero, CRSp, CRBase);
      }
    }
    /* madeira-bcd: refuse to compile host heap or code-buffer addresses as guest code.
     * Prevents infinite JIT compile loops when host PC leaks into State.rip during process detach. */
    return 0;
  }'''


def patch(source):
    if MARKER in source:
        return source
    if source.count(ANCHOR) != 1:
        raise ValueError("Core.cpp bogusrip anchor changed or missing")
    return source.replace(ANCHOR, REPLACEMENT, 1)


if __name__ == "__main__":
    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")
    try:
        result = patch(source)
    except ValueError as error:
        sys.exit("patch-fex-ios-bogusrip-exit: " + str(error))
    if result != source:
        path.write_text(result, encoding="utf-8")
    print("FEX ARM64EC: refuse to compile bogus host RIPs; exits cleanly instead of spinning")
