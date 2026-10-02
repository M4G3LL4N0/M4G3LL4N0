# Contributing

This repository is the GitHub profile for [M4G3LL4N0](https://github.com/M4G3LL4N0),
so contributions here are mostly about accuracy and clarity.

## What belongs here

- Corrections to the system map, descriptions, or links
- Better one-line explanations of the linked systems
- New systems that genuinely earn a place in the six

## What does not belong here

- Badge walls, contribution-graph widgets, or stat dashboards
- Feature claims that cannot be pointed at a test
- Marketing language where a measurement would do
- Anything that inflates a number without a source

## The rule this repository follows

> No component reports a number it did not measure.

Every figure on the profile comes from the GitHub API through
`.github/workflows/sync-profile.yml`, which only rewrites content between the
`<!-- githubos:start -->` and `<!-- githubos:end -->` markers. If a number is
missing, the honest fix is to fix the source, not to type the number in.

## Process

```sh
git clone https://github.com/M4G3LL4N0/M4G3LL4N0.git
cd M4G3LL4N0
git checkout -b fix/short-description
# edit, then:
git commit -m "docs(profile): correct grokmax test count"
git push origin fix/short-description
```

Then open a pull request. Commits follow
[Conventional Commits](https://www.conventionalcommits.org/).

Do not edit inside the generated markers by hand — the next sync will overwrite
your change. Change the generator instead.

## Larger contributions

For changes to the actual systems, see the `CONTRIBUTING.md` in the repository
you want to change. The most useful place to start is
[opencode-watchdog](https://github.com/M4G3LL4N0/opencode-watchdog), which has
open `good first issue` labels.
