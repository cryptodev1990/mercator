#!/usr/bin/env bash
# Check shell scripts.
# Requires [Shellcheck](https://www.shellcheck.net/)
# SC1090 (warning): ShellCheck can't follow non-constant source. Use a directive to specify location
shellcheck -e SC1090 -S warning -- *.sh bin/*.sh
