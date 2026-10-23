#!/usr/bin/env python3
"""Add NULL checks to strlen and wcslen in Wine's msvcrt and ntdll.

Prevents crash-to-desktop when legacy or cracked DLLs (such as Razor1911's 1911.dll)
pass NULL pointers to string length functions.
"""
from pathlib import Path
import sys

def patch_file(path, old_func, new_func):
    p = Path(path)
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    if "if (!s) return 0;" in text or "if (!str) return 0;" in text:
        return
    if old_func in text:
        text = text.replace(old_func, new_func, 1)
        p.write_text(text, encoding="utf-8")
        print(f"Patched {path}")

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("wine")

    # msvcrt/string.c
    patch_file(
        root / "dlls/msvcrt/string.c",
        "size_t __cdecl strlen(const char *str)\n{\n    const char *s = str;\n    while (*s) s++;\n    return s - str;\n}",
        "size_t __cdecl strlen(const char *str)\n{\n    const char *s = str;\n    if (!s) return 0;\n    while (*s) s++;\n    return s - str;\n}"
    )

    # msvcrt/wcs.c
    patch_file(
        root / "dlls/msvcrt/wcs.c",
        "size_t CDECL wcslen(const wchar_t *str)\n{\n    const wchar_t *s = str;\n    while (*s) s++;\n    return s - str;\n}",
        "size_t CDECL wcslen(const wchar_t *str)\n{\n    const wchar_t *s = str;\n    if (!s) return 0;\n    while (*s) s++;\n    return s - str;\n}"
    )

    # ntdll/string.c
    patch_file(
        root / "dlls/ntdll/string.c",
        "size_t __cdecl strlen( const char *str )\n{\n    const char *s = str;\n    while (*s) s++;\n    return s - str;\n}",
        "size_t __cdecl strlen( const char *str )\n{\n    const char *s = str;\n    if (!s) return 0;\n    while (*s) s++;\n    return s - str;\n}"
    )

    # ntdll/wcstring.c
    patch_file(
        root / "dlls/ntdll/wcstring.c",
        "size_t __cdecl wcslen( LPCWSTR str )\n{\n    const WCHAR *s = str;\n    while (*s) s++;\n    return s - str;\n}",
        "size_t __cdecl wcslen( LPCWSTR str )\n{\n    const WCHAR *s = str;\n    if (!s) return 0;\n    while (*s) s++;\n    return s - str;\n}"
    )

if __name__ == "__main__":
    main()
