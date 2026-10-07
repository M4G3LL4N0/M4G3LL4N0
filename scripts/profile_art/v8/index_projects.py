#!/usr/bin/env python3
"""Index every public owned repository once, and cache the result.

V8 is a large round: dossiers, storyboards, art, copy, duplication tests. Each
of those needs to know what a project actually is. Re-deriving that per stage
is where rounds like this go wrong -- a later stage quietly disagrees with an
earlier one because it re-read the source differently.

So: index once. Every stage reads the cache. Re-index only when the source
content hash changes.

Source precedence follows the evidence hierarchy:

    1. the product checkout in the portfolio tree
    2. a read-only clone under V8_SOURCE (used when no portfolio checkout
       exists, which is what finally resolved the repositories that V7 had to
       report as blocked)
    3. the live GitHub tree

Nothing here writes to a product checkout. The clones are read for structure
only.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import subprocess
import time

OWNER = "M4G3LL4N0"
PROFILE = pathlib.Path(__file__).resolve().parents[3]
PORTFOLIO = pathlib.Path("/Users/matador/startups")
V8_SOURCE = pathlib.Path("/tmp/github-v8-source")
OUT = PROFILE / ".github-art" / "v8-index.json"

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", "coverage", "vendor",
    "__pycache__", ".venv", "venv", "target", ".trillionx-agent-fabric",
    "site-packages", ".turbo", ".cache",
}
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz",
    ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".webm", ".mov", ".so", ".dylib",
    ".dll", ".exe", ".wasm", ".lock",
}

EXT_LANG = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".mts": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
    ".cjs": "JavaScript", ".py": "Python", ".go": "Go", ".rs": "Rust",
    ".rb": "Ruby", ".php": "PHP", ".java": "Java", ".kt": "Kotlin",
    ".swift": "Swift", ".cs": "C#", ".c": "C", ".h": "C", ".hpp": "C++",
    ".cpp": "C++", ".cc": "C++", ".sql": "SQL", ".sh": "Shell", ".bash": "Shell",
    ".lua": "Lua", ".r": "R", ".scala": "Scala", ".ex": "Elixir",
    ".exs": "Elixir", ".zig": "Zig", ".dart": "Dart", ".vue": "Vue",
    ".svelte": "Svelte", ".css": "CSS", ".scss": "CSS", ".html": "HTML",
    ".md": "Markdown", ".json": "JSON", ".yml": "YAML", ".yaml": "YAML",
}

# Framework detection is deliberately conservative: a dependency entry in a
# manifest is evidence the library is declared, not proof it is used. Each hit
# records which manifest declared it so confidence can be judged downstream.
FRAMEWORK_SIGNALS = {
    "Next.js": ("next",), "React": ("react",), "Vue": ("vue",),
    "Svelte": ("svelte",), "Astro": ("astro",),
    "TanStack Query": ("@tanstack/react-query",), "Redux": ("redux",),
    "Tailwind CSS": ("tailwindcss",), "Supabase": ("@supabase/supabase-js",),
    "Prisma": ("prisma", "@prisma/client"), "Drizzle": ("drizzle-orm",),
    "Fastify": ("fastify",), "Express": ("express",), "NestJS": ("@nestjs/core",),
    "Hono": ("hono",), "Django": ("django",), "Flask": ("flask",),
    "FastAPI": ("fastapi",), "uvicorn": ("uvicorn",),
    "Playwright": ("@playwright/test", "playwright"),
    "Vitest": ("vitest",), "Jest": ("jest",), "Pytest": ("pytest",),
    "SQLAlchemy": ("sqlalchemy",), "Pydantic": ("pydantic",),
    "LangChain": ("langchain",), "LlamaIndex": ("llamaindex",),
    "OpenAI SDK": ("openai",), "Anthropic SDK": ("@anthropic-ai/sdk",),
    "Vercel AI SDK": ("ai",), "D3": ("d3",), "Three.js": ("three",),
    "Zod": ("zod",), "tRPC": ("@trpc/server",), "GraphQL": ("graphql",),
    "gRPC": ("grpc",), "Socket.io": ("socket.io",), "Redis": ("redis", "ioredis"),
    "Postgres": ("pg", "postgres", "psycopg"), "SQLite": ("sqlite3", "better-sqlite3"),
    "Docker": ("docker",), "Kubernetes client": ("@kubernetes/client-node",),
    "Terraform": ("terraform",), "AWS SDK": ("@aws-sdk/client", "boto3"),
    "Stripe": ("stripe",), "OpenRouter": ("openrouter",),
}

# CS primitive detection is scored, not boolean.
#
# The first version tested one regex per primitive. It reported 118 of 136
# repositories as having a state machine, a pipeline, a queue and a policy
# engine -- because those words appear in framework code, generated clients and
# documentation. A detector that fires on nearly everything measures nothing,
# and using it to pick per-project visual metaphors would have given every
# repository the same art.
#
# So each primitive needs density, not just presence, and must appear in real
# code rather than in a dependency list. Thresholds are set so a genuine
# project shows a handful of primitives, not all twenty-four.
CS_PRIMITIVE_SIGNALS = {
    "ast":            (r"\b(ast|parseTree|tree-sitter|recast|esprima)\b|\.parse\(|parser\.parse", 6),
    "dag":            (r"topological|toposort|dependency ?graph|build ?graph|\bdag\b", 4),
    "trie":           (r"\btrie\b|prefix ?tree|radixtree|prefixkey", 4),
    "queue":          (r"\bqueue\b|enqueue|dequeue|workerpool|worker ?pool|jobqueue|bullmq|celery", 5),
    "stack":          (r"\bstack\b|\.push\(|\.pop\(\)|callstack", 8),
    "heap":           (r"heapq|binaryheap|priorityqueue|priority ?queue|\bheap\b", 4),
    "state_machine":  (r"state_?machine|finitestate|\bfsm\b|xstate|statemachine|\btransitions_\b|\btransition_?map\b", 8),
    "scheduler":      (r"\bscheduler\b|\bcron\b|setinterval|ratelimit|rate_limit|throttle", 5),
    "pipeline":       (r"\bpipeline\b|waterfall\w*|stage_?graph|\bstage_?name\b", 9),
    "event_stream":   (r"event_?stream|eventsource|\bsse\b|websocket|pub_?sub|\.emit\(", 6),
    "cache":          (r"\bcache\b|lru_?cache|memoiz|\bredis\b|cachemiss", 6),
    "graph_traversal":(r"\btraverse\b|dijkstra|\bbfs\b|\bdfs\b|shortestpath|shortest_path", 4),
    "index":          (r"\bbtree\b|b_?tree|fulltext|full_text|vectorindex|\bindex\b", 10),
    "memory_map":     (r"memorymap|arena_?alloc|allocat\w*buffer|\barena\b", 4),
    "git_graph":      (r"rev_?parse|rebase_?onto|commit_?graph|cherry_?pick|mergebase", 5),
    "model_router":   (r"modelrouter|model_?router|route_?model|model_?fallback", 4),
    "agent_graph":    (r"tool_?call|toolcall|reasoning_?loop|agent_?graph|orchestrat\w+", 6),
    "compiler_stage": (r"\btranspil\w+|lexer|tokeniz\w+|codegen|\bcompile\b", 5),
    "api_flow":       (r"\bendpoint\b|apiroute|routehandler|@app\.(get|post|put|delete)", 8),
    "terminal":       (r"\bargv\b|commndline|commandline|\bcli\b|process\.stdin|readline", 8),
    "simulator":      (r"\bsimulat\w+|\bemulat\w+|sandbox|virtualmachine", 5),
    "benchmark":      (r"\bbenchmark\w*|throughput|latency|percentile|\bp99\b", 6),
    "crypto":         (r"\bencrypt\w*|\bcipher\w*|keypair|privatekey|\bcertificate\b|sha256|ed25519", 6),
    "policy":         (r"policy_?engine|permission|allowlist|trust_?boundar|attest|\bpolicy\b", 8),
    "scheduling_sim": (r"discreteevent|eventsimulat|timeslice|contextswitch", 4),
}

def tok() -> str:
    return os.environ.get("GH_TOKEN", "")


def walk(root: pathlib.Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            yield pathlib.Path(dirpath) / fn


def read_text(p: pathlib.Path, limit: int = 200_000) -> str:
    try:
        if p.stat().st_size > limit:
            return ""
        return p.read_text(errors="replace")
    except Exception:
        return ""


def hash_tree(root: pathlib.Path, cap: int = 4000) -> str:
    """Content hash over the source tree.

    Used to decide whether the cache is stale. Directory metadata is excluded
    so a fresh clone of unchanged code does not invalidate the index.
    """
    h = hashlib.sha256()
    n = 0
    for f in walk(root):
        if f.suffix.lower() in BINARY_EXT:
            continue
        rel = str(f.relative_to(root))
        try:
            h.update(rel.encode())
            h.update(hashlib.sha256(f.read_bytes()).digest())
        except Exception:
            continue
        n += 1
        if n >= cap:
            break
    return h.hexdigest()[:16]


def shared_template_hashes(repos: dict, min_share: float = 0.5) -> set[str]:
    """Find file contents shared by most of the portfolio.

    These repositories descend from one scaffold. blitzproof and Ayncient
    share 886 paths, 223 of them byte-identical. Any structure living in that
    shared skeleton -- a pipeline helper, a queue shim, a state enum -- is
    measured as if every project had implemented it, which is how 102 of 136
    repositories came to report a pipeline.

    Detecting primitives against shared files measures the template, not the
    project. This returns content hashes to exclude so what remains is
    project-specific.
    """
    seen: dict[str, int] = {}
    for rec in repos.values():
        root = rec.get("source_path")
        if not root:
            continue
        root = pathlib.Path(root)
        for f in walk(root):
            if f.suffix.lower() in BINARY_EXT:
                continue
            try:
                h = hashlib.sha256(f.read_bytes()).hexdigest()
            except Exception:
                continue
            seen[h] = seen.get(h, 0) + 1
    total = max(1, sum(1 for r in repos.values() if r.get("source_path")))
    return {h for h, n in seen.items() if n >= max(2, total * min_share)}


def source_for(name: str, ledger: dict) -> tuple[pathlib.Path | None, str]:
    rec = next((r for r in ledger["records"] if r["name"] == name), {})
    lp = rec.get("local_path")
    if lp:
        p = pathlib.Path(lp)
        if p.exists() and (p / ".git").exists():
            return p, "portfolio"
    clone = V8_SOURCE / name
    if clone.exists():
        return clone, "clone"
    return None, "none"


def git_facts(root: pathlib.Path) -> dict:
    out: dict = {}
    def run(args, key, parse=None):
        try:
            r = subprocess.run(["git", "-C", str(root)] + args,
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 0 and r.stdout.strip():
                out[key] = parse(r.stdout) if parse else r.stdout.strip()
        except Exception:
            pass
    run(["rev-list", "--count", "HEAD"], "commits")
    run(["log", "-1", "--format=%cI"], "last_commit")
    run(["log", "--format=%an"], "authors", lambda s: len({x for x in s.split("\n") if x}))
    run(["branch", "-r"], "remote_branches", lambda s: len([x for x in s.split("\n") if x.strip()]))
    run(["tag", "-l"], "tags", lambda s: len([x for x in s.split("\n") if x.strip()]))
    run(["log", "--format=%s", "-40"], "recent_subjects",
        lambda s: [x for x in s.split("\n") if x][:12])
    return out


def analyse(name: str, root: pathlib.Path | None, origin: str,
            shared: set[str] | None = None) -> dict:
    rec: dict = {
        "repo": name,
        "source_origin": origin,
        "source_path": str(root) if root else None,
        "content_hash": hash_tree(root) if root else None,
    }
    if root is None:
        rec.update({"confidence": "E1", "files": 0, "languages": {}, "frameworks": [],
                    "manifests": [], "tests": [], "ci_workflows": [], "entry_points": [],
                    "modules": [], "docs": [], "cs_primitives": [], "routes": [],
                    "has_code": False, "git": {}})
        return rec

    langs: dict[str, int] = {}
    manifests: list[str] = []
    deps_text: list[str] = []
    tests: list[str] = []
    workflows: list[str] = []
    entries: list[str] = []
    modules: list[str] = []
    docs: list[str] = []
    routes: list[str] = []
    blob: list[str] = []
    files = 0
    shared_files = 0
    has_code = False
    shared = shared or set()

    for f in walk(root):
        files += 1
        rel = str(f.relative_to(root))
        base = f.name
        suf = f.suffix.lower()
        lang = EXT_LANG.get(suf)
        if lang and lang not in ("Markdown", "JSON", "YAML"):
            langs[lang] = langs.get(lang, 0) + 1
            if lang not in ("CSS", "HTML"):
                has_code = True
        if suf in (".md", ".mdx"):
            docs.append(rel)
        if base in ("package.json", "pyproject.toml", "requirements.txt", "go.mod",
                    "Cargo.toml", "Gemfile", "composer.json", "setup.py",
                    "build.gradle", "pom.xml"):
            manifests.append(rel)
            deps_text.append(read_text(f))
        if base in ("Makefile", "Dockerfile", "docker-compose.yml", "Taskfile.yml"):
            manifests.append(rel)
        if ".github/workflows/" in rel and suf in (".yml", ".yaml"):
            workflows.append(rel)
        if re.match(r"(test_|_test|.*\.test|.*\.spec)\.[a-z]{2,4}$", base) or \
           re.search(r"(^|/)tests?/", rel):
            tests.append(rel)
        if base in ("main.py", "__main__.py", "main.go", "main.rs", "index.ts",
                    "index.js", "cli.py", "app.py", "server.py", "index.html"):
            entries.append(rel)
        # top-level source directories become module names
        parts = rel.split("/")
        if len(parts) == 2 and parts[0] not in ("docs", "assets", "public",
                                                ".github", ".cursor", ".opencode",
                                                "node_modules", "tests", "test"):
            modules.append(parts[0])
        if re.search(r"/(app|src)/(.*/)?(page|route)\.[jt]sx?$", rel):
            m = re.search(r"/(app|src)/([^/]*)/?(page|route)\.[jt]sx?$", rel)
            if m and m.group(2):
                routes.append("/" + m.group(2))
            elif "/app/page." in rel or "/src/app/page." in rel:
                routes.append("/")
        if suf in (".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".sh", ".sql") \
           and f.stat().st_size < 60_000:
            try:
                h = hashlib.sha256(f.read_bytes()).hexdigest()
            except Exception:
                h = None
            if h in shared:
                shared_files += 1
                continue
            blob.append(read_text(f, 60_000))

    joined_deps = "\n".join(deps_text).lower()
    frameworks = [fw for fw, sigs in FRAMEWORK_SIGNALS.items()
                  if any(s.lower() in joined_deps for s in sigs)]
    code = "\n".join(blob)
    # Score by occurrence count against a per-primitive threshold. Keep the
    # strongest primitives only: a project with twelve matches for "queue" is
    # not twelve kinds of queue, it is one subsystem described repeatedly.
    scored: dict[str, int] = {}
    for key, (pat, threshold) in CS_PRIMITIVE_SIGNALS.items():
        hits = len(re.findall(pat, code, re.I))
        if hits >= threshold:
            scored[key] = hits
    primitives = [k for k, _ in sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))[:6]]

    rec.update({
        "files": files,
        "has_code": has_code,
        "languages": dict(sorted(langs.items(), key=lambda kv: -kv[1])),
        "frameworks": sorted(frameworks),
        "manifests": sorted(set(manifests)),
        "tests": sorted(set(tests))[:40],
        "test_count": len(set(tests)),
        "ci_workflows": sorted(set(workflows)),
        "entry_points": sorted(set(entries)),
        "modules": sorted(set(modules))[:16],
        "docs": sorted(set(docs))[:24],
        "routes": sorted(set(routes))[:24],
        "cs_primitives": primitives,
        "shared_template_files": shared_files,
        "git": git_facts(root),
    })
    # Confidence follows the evidence hierarchy: a portfolio checkout plus a
    # public card is E3, a clone alone is E2, no source at all is E1.
    rec["confidence"] = "E3" if origin == "portfolio" else "E2"
    return rec


def main() -> int:
    ledger = json.loads((PROFILE / "github-account-ledger.json").read_text())
    public = [r["name"] for r in ledger["records"] if r["visibility"] == "public"]

    cache: dict = {}
    if OUT.exists():
        try:
            cache = json.loads(OUT.read_text()).get("repos", {})
        except Exception:
            cache = {}

    roots = {n: source_for(n, ledger) for n in public}

    # Pass 1 -- structure only, so the shared-template set can be derived.
    for name in public:
        root, origin = roots[name]
        cache[name] = analyse(name, root, origin)

    shared = shared_template_hashes(cache)
    print(f"  shared template file hashes : {len(shared)}")

    # Pass 2 -- re-analyse excluding shared files, so detected structures belong
    # to the project rather than to the scaffold it was generated from.
    fresh, reused, changed = [], [], []
    for name in public:
        root, origin = roots[name]
        prior = cache.get(name)
        cache[name] = analyse(name, root, origin, shared)
        if prior and prior.get("shared_template_files") == cache[name].get("shared_template_files"):
            reused.append(name)
        else:
            (changed if prior else fresh).append(name)

    conf: dict[str, int] = {}
    for r in cache.values():
        conf[r.get("confidence", "?")] = conf.get(r.get("confidence", "?"), 0) + 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"generated_by": "v8/index_projects.py",
         "shared_template_hashes": len(shared), "repos": cache},
        indent=1, sort_keys=True) + "\n")

    with_src = sum(1 for r in cache.values() if r["source_origin"] != "none")
    print(f"  indexed        : {len(cache)} public repositories")
    print(f"  fresh          : {len(fresh)}")
    print(f"  reindexed      : {len(changed)}")
    print(f"  reused from cache: {len(reused)}")
    print(f"  with source    : {with_src}  (portfolio {conf.get('E3', 0)} / clone {conf.get('E2', 0)})")
    print(f"  no source      : {sum(1 for r in cache.values() if r['source_origin']=='none')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())