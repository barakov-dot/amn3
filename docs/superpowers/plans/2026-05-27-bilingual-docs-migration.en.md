# Bilingual Documentation Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** create Russian and English versions for all current documentation without breaking legacy links or project workflow.

**Architecture:** legacy files without a language suffix remain in place. Each document gets separate `.ru.md` and `.en.md` versions; the existing language is copied without semantic changes, and the second language is created as an equivalent translation or a compact working version for large internal plans.

**Tech Stack:** Markdown, Git, existing documentation policy, `rg`, `git diff --check`, pytest.

---

## Files

- Create `.ru.md` and `.en.md` pairs for legacy files in `docs/`.
- Create `.ru.md` and `.en.md` pairs for legacy files in `docs/superpowers/specs/`.
- Create `.ru.md` and `.en.md` pairs for legacy files in `docs/superpowers/plans/`.
- Do not delete or rename old `.md` files without a suffix.

---

### Task 1: Inventory

- [x] Check the file list with `rg --files docs`.
- [x] Split documents into Russian-source and English-source groups.
- [x] Confirm that the Git working tree is clean before migration.

### Task 2: Create Language Copies of Source Documents

- [x] Create `.ru.md` copies for Russian-source legacy files.
- [x] Create `.en.md` copies for English-source Superpowers legacy files.
- [x] Do not modify old legacy files.

### Task 3: Create Missing Translations

- [x] Create English versions of top-level Russian documents.
- [x] Create Russian versions of Superpowers specs and plans.
- [x] Preserve commands, file names, APIs, and code blocks where translation would change meaning.

### Task 4: Verification

- [x] Verify that every legacy document has both `.ru.md` and `.en.md`.
- [x] Run `git diff --check`.
- [x] Run a secret scan.
- [x] Run the project tests, even though only docs changed.

### Task 5: Commit

- [x] Add the new documents to Git.
- [x] Create a dedicated documentation migration commit.
