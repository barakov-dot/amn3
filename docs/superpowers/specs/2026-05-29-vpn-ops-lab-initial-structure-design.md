# VPN Ops Lab Initial Structure Design

## Purpose

`vpn-ops-lab` is a research repository for parallel development of `amn2` and future VPN products. It collects analysis of similar GitHub projects, license findings, architectural notes, UX observations, production practices, feature gaps, candidate ideas, rejected ideas, and lessons that may later be added to a shared Codex skill.

The repository is not production code. It is a controlled research laboratory where external projects are studied, not copied.

## Main Rule

`amn2` remains the production direction.

`vpn-ops-lab` remains the research laboratory.

Features move from `vpn-ops-lab` to `amn2` only after checking:

- license compatibility;
- practical value;
- operational and security risks;
- architectural compatibility;
- test plan.

Until an idea passes these checks, it is only a research candidate.

## Root Layout

The current workspace folder is the repository root. There is no nested `vpn-ops-lab/` directory.

```text
README.md
research/
  upstreams/
    README.md
ideas/
  candidates-for-amn2.md
  candidates-for-hybrid.md
  add-to-skill.md
  rejected.md
watch-notes/
  README.md
prototypes/
  README.md
```

## Area Responsibilities

`README.md` defines the project purpose, safety rules, relationship to `amn2`, and the feature-transfer gate.

`research/upstreams/README.md` explains how to analyze external VPN-related projects. Each upstream analysis should record the project link, license, relevant architecture, feature observations, UX notes, production practices, risks, and whether any idea may be useful for `amn2` or a future hybrid project.

`ideas/candidates-for-amn2.md` tracks ideas that may eventually move into `amn2`. Each candidate must stay in research status until license, value, risk, architecture, and test-plan checks are complete.

`ideas/candidates-for-hybrid.md` tracks ideas intended for a future hybrid VPN product, separate from immediate `amn2` work.

`ideas/add-to-skill.md` captures reusable research and implementation lessons that may be folded into a shared Codex skill later.

`ideas/rejected.md` records rejected or deferred ideas with reasons, so the same analysis does not need to be repeated.

`watch-notes/README.md` describes how to keep periodic notes about upstream changes, releases, security-relevant updates, and newly discovered projects.

`prototypes/README.md` defines the boundary for experiments. Prototypes must be original implementations or controlled experiments, not copied external code, and any path from prototype to `amn2` must include tests.

## Data Flow

Research starts in `research/upstreams/` or `watch-notes/`.

Useful findings move into one of the `ideas/` files:

- `candidates-for-amn2.md` for production-relevant ideas;
- `candidates-for-hybrid.md` for future-product ideas;
- `add-to-skill.md` for reusable Codex workflow lessons;
- `rejected.md` for ideas that should not be pursued.

Prototype work may happen only after an idea is understood well enough to test safely. Prototype results feed back into the relevant idea file.

## Safety And Error Handling

If a license is unclear, incompatible, missing, or too restrictive, the idea must not be treated as transferable to `amn2`.

If a feature depends on copying code from an external project, it must be rejected or redesigned as an original implementation before any production consideration.

If operational or security risks are not understood, the idea remains in research status.

If architectural compatibility with `amn2` is unclear, the candidate entry must say what needs to be checked before implementation.

## Testing Expectations

The initial repository structure is documentation-first, so verification starts with file presence and content review.

Later, any prototype or transferred feature proposal should include:

- expected behavior;
- risk notes;
- test plan;
- minimum acceptance checks before `amn2` work begins.

## First Implementation Scope

The first implementation should create the approved Markdown-first repository skeleton in the current workspace root:

- root `README.md`;
- `research/upstreams/README.md`;
- four idea tracking files under `ideas/`;
- `watch-notes/README.md`;
- `prototypes/README.md`.

No production VPN code, automation scripts, or external code imports are part of the first implementation.
