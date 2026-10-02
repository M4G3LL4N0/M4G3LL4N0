# Security Policy

## Scope

This repository holds profile documentation only. There is no runtime to attack here.

The security-relevant software lives in the repositories linked from the
[system map](README.md). Each of those has its own `SECURITY.md` and its own
disclosure path.

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Use GitHub's private reporting on the affected repository:

> Repository → **Security** → **Advisories** → **Report a vulnerability**

If private advisories are unavailable on the target repository, open an issue
that contains only a one-line summary with no technical detail, and ask for a
private channel.

## What to include

- affected repository and version or commit
- what an attacker gains
- reproduction steps, in a private channel only
- whether any real credential, key or user data was exposed

## Response

Vulnerabilities are triaged in the order they arrive. Reports that demonstrate a
working exploit against current `main` are prioritised over theoretical findings.

## Non-goals

- Denial of service against hosted demo sites
- Findings that require an attacker to already hold a maintainer credential
- Missing hardening headers on static marketing pages
- Dependency advisories with no reachable code path
