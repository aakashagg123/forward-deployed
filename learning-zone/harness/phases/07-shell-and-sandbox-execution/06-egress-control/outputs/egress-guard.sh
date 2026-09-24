#!/usr/bin/env bash
# PreToolUse hook: block curl/wget/etc egress to hosts not on the allowlist.
# Reads the tool-call JSON on stdin. Exit 2 = deny (message on stderr).
# This is a cheap belt; enforce the real policy at the network layer too.
ALLOW="registry.npmjs.org pypi.org github.com api.anthropic.com"
cmd="$(cat)"
urls="$(printf '%s' "$cmd" | grep -oE 'https?://[a-zA-Z0-9.-]+' | sed -E 's#https?://##')"
for host in $urls; do
  case " $ALLOW " in
    *" $host "*) ;;                                    # allowed
    *) echo "BLOCKED egress to $host (not on allowlist)" >&2; exit 2 ;;
  esac
done
exit 0
