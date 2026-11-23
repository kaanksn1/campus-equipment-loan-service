#!/bin/sh
# Source this file from build.sh/run.sh. No permanent machine settings are changed.
select_project_java() {
    for candidate in "${JAVA_HOME:-}" \
        "$HOME"/Library/Caches/codex/software-verification/jdk17/*/Contents/Home; do
        if [ -n "$candidate" ] && [ -x "$candidate/bin/java" ]; then
            major=$("$candidate/bin/java" -version 2>&1 | sed -n '1s/.*version "\([0-9]*\).*/\1/p')
            if [ "${major:-0}" -ge 17 ] 2>/dev/null; then
                JAVA_HOME=$candidate
                export JAVA_HOME
                PATH="$JAVA_HOME/bin:$PATH"
                export PATH
                return 0
            fi
        fi
    done
    if [ -x /usr/libexec/java_home ]; then
        candidate=$(/usr/libexec/java_home -v 17 2>/dev/null) || candidate=
        if [ -n "$candidate" ] && [ -x "$candidate/bin/java" ]; then
            JAVA_HOME=$candidate
            export JAVA_HOME
            PATH="$JAVA_HOME/bin:$PATH"
            export PATH
            return 0
        fi
    fi
    if command -v java >/dev/null 2>&1; then
        major=$(java -version 2>&1 | sed -n '1s/.*version "\([0-9]*\).*/\1/p')
        if [ "${major:-0}" -ge 17 ] 2>/dev/null; then
            unset JAVA_HOME
            return 0
        fi
    fi
    printf '%s\n' 'Java 17 or later is required. Install JDK 17 and set JAVA_HOME to its directory.' >&2
    return 1
}
select_project_java
