# Wiki Schema

## Purpose

This file instructs the LLM on how to maintain this knowledge base. Read this before performing any wiki operation.

## Conventions

- All wiki pages use Obsidian-compatible markdown with YAML frontmatter
- Cross-references use `[[wikilinks]]` syntax: `[[page-name]]` or `[[path/page-name|Display Text]]`
- Every page has frontmatter with at minimum: `title`, `tags`, `created_at`, `publish`
- File names use lowercase kebab-case: `distributed-consensus.md`, `andrej-karpathy.md`
- Tags use lowercase with hyphens: `machine-learning`, `distributed-systems`

## Page Types

### Entity (`wiki/entities/`)
People, tools, companies, projects, frameworks. One page per distinct entity.
Template: `schema/templates/entity.md`

### Concept (`wiki/concepts/`)
Ideas, patterns, mental models, principles. Abstract knowledge.
Template: `schema/templates/concept.md`

### Topic (`wiki/topics/`)
Broad domain areas that group entities and concepts. E.g., `machine-learning`, `personal-finance`.
Created as needed when multiple entities/concepts cluster around a domain.

### Source Summary (`wiki/topics/` or contextually appropriate directory)
Summary of an ingested source with key takeaways. Links to entities and concepts mentioned.
Template: `schema/templates/source-summary.md`

### Synthesis (`wiki/syntheses/`)
Comparisons, analyses, and cross-cutting insights that connect multiple entities or concepts.
Template: `schema/templates/comparison.md`

### Exploration (`wiki/explorations/`)
Saved query answers — synthesized responses to questions asked of the wiki.

## Ingest Instructions

When ingesting a new source:
1. Identify all entities (people, tools, projects) and concepts (ideas, patterns) mentioned
2. For each entity/concept, create a new page or update the existing one
3. Add `[[wikilinks]]` between related pages
4. Create a source summary page with key takeaways
5. Update `wiki/index.md` with new entries
6. Update `wiki/log.md` with the operation record

## Update Instructions

When updating an existing page with new information:
- Preserve all existing content
- Add new facts in the appropriate section
- If new information contradicts existing content, add a warning callout:
  `> [!warning] Contradiction: [description]`
- Do not duplicate existing information
- Update the `updated_at` field in frontmatter
