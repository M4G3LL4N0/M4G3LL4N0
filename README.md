<p align="center">
  <img src="assets/hero.svg" alt="M4G3LL4N0 — Noaerth" width="100%">
</p>

<p align="center">
  <a href="https://www.noaerth.com"><img alt="Noaerth" src="https://img.shields.io/badge/noaerth.com-0A0C10?style=flat&labelColor=0A0C10&color=5EE7D0&logo=github&logoColor=5EE7D0"></a>
  <a href="https://github.com/M4G3LL4N0?tab=repositories&sort=stargazers"><img alt="Repositories" src="https://img.shields.io/github/repo-count/M4G3LL4N0?style=flat&labelColor=0A0C10&color=9AA1AB"></a>
  <a href="https://github.com/why-are-you-here"><img alt="why are you here" src="https://img.shields.io/badge/why_are_you_here%3F-0A0C10?style=flat&labelColor=0A0C10&color=4A5058"></a>
</p>

<h1 align="center">Build systems. Prove them. Compound what works.</h1>

<p align="center">
  Autonomous systems &#183; developer infrastructure &#183; research tooling &#183; experimental technology
</p>

---

## What I'm building

I build the layer <em>underneath</em> the products: execution engines, control planes,
deterministic tooling and research harnesses that stay honest when the model gets expensive,
slow, or wrong.

Six systems carry most of the weight right now. Each one has tests, an architecture, and a
failure story — that is the bar, not the feature list.

| System | What it actually does |
| --- | --- |
| **[Portfolio OS](https://github.com/M4G3LL4N0/noaerth-portfolio-os)** | Venture-studio control plane. SQLite source of truth, work queue, locks, reviewer separation, allowlist-based public snapshots. |
| **[AgentOS](https://github.com/M4G3LL4N0/agentos)** | Provider-neutral agent execution engine. Objective in, verified outcome out, at the lowest responsible cost. |
| **[GrokInstall](https://github.com/M4G3LL4N0/grokinstall)** | Go CLI that inspects a repository and installs the smallest useful capability into it. "Do not install" is a first-class answer. |
| **[GrokMax](https://github.com/M4G3LL4N0/grokmax)** | Deterministic-first routing. Zero-cost executors before paid ones, a five-layer cache, and telemetry that labels every number measured / estimated / proxy. |
| **[gh0st](https://github.com/M4G3LL4N0/gh0st)** | Local-first encrypted AI client. Your prompts never leave the machine by default. |
| **[OpenCode Watchdog](https://github.com/M4G3LL4N0/opencode-watchdog)** | Circuit breaker for runaway coding-agent sessions. Detects degeneration, aborts the affected session, leaves your files alone. |

Supporting systems — workforce configuration, persistent-agent runtime, and the sites that
document them — live in the [repository list](https://github.com/M4G3LL4N0?tab=repositories).

---

## System map

```mermaid
flowchart TB
    subgraph Intent
        U[Human or agent intent]
    end

    subgraph Control["Control plane"]
        POS["Portfolio OS<br/>queue · locks · review · publish"]
    end

    subgraph Execute["Execution"]
        AOS["AgentOS<br/>inspect → plan → execute → verify"]
    end

    subgraph Determinism["Deterministic layer"]
        GI["GrokInstall<br/>capability contracts"]
        GM["GrokMax<br/>route · cache · ledger"]
    end

    subgraph Surfaces["Surfaces"]
        GH["gh0st<br/>encrypted local client"]
        OW["OpenCode Watchdog<br/>degeneration guardrail"]
    end

    U --> POS
    POS --> AOS
    AOS --> GM
    GM -. "cheaper than paid" .-> AOS
    GI -. "installs into" .-> AOS
    AOS --> GH
    AOS --> OW
    OW -. "halts degenerate run" .-> AOS

    POS --> PUB[("sanitized public snapshot")]
    PUB --> SITE[noaerth.com]

    classDef core fill:#0A0C10,stroke:#5EE7D0,color:#ECEEF1
    classDef det fill:#0A0C10,stroke:#7C8CFF,color:#ECEEF1
    class POS,AOS core
    class GI,GM det
```

The rule that holds it together: **no component is allowed to report a number it did not
measure.** Savings are proxies until they are billed. Capability counts come from the ledger,
not from a marketing page.

---

## Current signal

Everything below this line is regenerated from the GitHub API by
`.github/workflows/sync-profile.yml`. Nothing here is hand-maintained, and nothing here is
estimated.

<!-- githubos:start -->
<!-- githubos:end -->

---

## Open source

Public, buildable, and covered by tests.

- **[GrokInstall](https://github.com/M4G3LL4N0/grokinstall)** — `go install` a single binary.
  The deepest documentation in the portfolio and the easiest thing here to actually try.
- **[OpenCode Watchdog](https://github.com/M4G3LL4N0/opencode-watchdog)** — the most
  immediately useful thing to a stranger. Solves a problem every agentic-coding user hits.
- **[GrokMax](https://github.com/M4G3LL4N0/grokmax)** — the cost-control reference
  implementation. Routing, caching, and honest telemetry in one pipeline.
- **[gh0st](https://github.com/M4G3LL4N0/gh0st)** — desktop client with local-first encryption.
- **[AgentOS](https://github.com/M4G3LL4N0/agentos)** — the engine the rest of the stack runs on.
- **[Portfolio OS](https://github.com/M4G3LL4N0/noaerth-portfolio-os)** — the control plane that
  actually manages this portfolio.

Issues, discussions and good-first-issue labels are live on every public repository.

## Contributing

Contributions are welcome on the open-source spearhead first. Read
[CONTRIBUTING.md](CONTRIBUTING.md) — the short version is: branch, keep it reviewable, prove it
with a test, open a PR.

## Security

Report vulnerabilities privately. See [SECURITY.md](SECURITY.md).

## License

Profile content and documentation: [MIT](LICENSE).

---

<p align="center">
  <sub>
    Some projects reference Grok, ChatGPT, OpenAI and other providers as
    <em>integration targets</em> inside provider-neutral runtimes. Not affiliated with or endorsed by them.<br/><br/>
    Still curious how you got here? <a href="https://github.com/M4G3LL4N0/why-are-you-here">why are you here?</a>
  </sub>
</p>
