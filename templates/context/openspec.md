# OpenSpec Workflow Guide

## What is OpenSpec?

OpenSpec is a spec-driven development workflow that aligns humans and AI on what to build before writing code. It uses a structured directory approach to separate current truth from proposed changes.

## Directory Structure

```
openspec/
├── project.md          # Project conventions and architecture
├── specs/              # Current truth (source of truth)
│   └── component/
│       └── spec.md
└── changes/            # Proposed changes
    └── feature-name/
        ├── proposal.md # Why and what changes
        ├── tasks.md    # Implementation checklist
        └── specs/      # Delta showing changes
            └── component/
                └── spec.md
```

## Workflow

### 1. Draft Proposal
Create a change proposal that captures spec updates:
```
Create an OpenSpec change proposal for [feature description]
```

AI creates `openspec/changes/feature-name/` with:
- `proposal.md` - Why and what changes (see format below)
- `tasks.md` - Implementation checklist
- `specs/` - Delta showing additions/modifications/removals

**Important**: Specs must follow the directory structure:
```
specs/
└── spec-name/          ← directory named after the spec
    └── spec.md         ← file must be named "spec.md"
```

Not: `specs/spec-name.md` (direct file won't be merged during archiving)

#### Proposal Format

Proposals must include these required sections:

```markdown
# Feature Name

**Status**: Proposed
**Priority**: High/Medium/Low
**Complexity**: High/Medium/Low

## Why

Explain the motivation and problem being solved:
- What problem exists?
- Why is it important?
- What's the impact if not addressed?

## What Changes

List the specific changes being made:
- New components/modules being added
- Existing components being modified
- Components being removed
- Dependencies being added/changed

## Technical Approach (Optional)

Implementation details, patterns, and decisions.

## Success Criteria (Optional)

How to verify the change is complete and working.
```

**Note**: Use `## Why` and `## What Changes` headers exactly as shown - these are validated by openspec.

### 2. Review & Align
Iterate on specifications until they match requirements:
```bash
openspec list                    # View active changes
openspec show feature-name       # Review proposal and tasks
openspec validate feature-name   # Check spec formatting
```

Refine specs with AI until aligned.

### 3. Implement Tasks
Once specs are approved, implement:
```
The specs look good. Let's implement this change.
```

AI works through tasks in `tasks.md`, marking them complete.

### 4. Archive Completed Change
After implementation, merge changes back to source of truth:
```bash
openspec archive feature-name --yes
```

This moves the change to `openspec/archive/` and updates `openspec/specs/`.

## Delta Format

Deltas show how specs change using three sections:

```markdown
## ADDED Requirements
### Requirement: New Feature
The system SHALL provide new capability.

#### Scenario: Usage example
- WHEN condition
- THEN expected behavior

## MODIFIED Requirements
### Requirement: Updated Feature
The system SHALL provide updated capability.
(Include complete updated text)

## REMOVED Requirements
### Requirement: Deprecated Feature
(Document what's being removed)
```

## Commands Reference

### Viewing Changes and Specs

```bash
openspec list                    # List all changes (summary)
openspec list --changes          # List changes with task counts
openspec list --specs            # List source of truth specs
openspec view                    # Interactive dashboard with progress
openspec show <change>           # Display change details (proposal, tasks, specs)
openspec show <change> --json    # Output in JSON format
openspec show <spec> --type spec # Show specific spec from source of truth
```

### Validation

```bash
openspec validate <change>         # Validate change formatting
openspec validate <change> --strict # Strict validation (recommended)
```

### Managing Changes

```bash
openspec archive <change>        # Archive change (interactive)
openspec archive <change> --yes  # Archive without prompts (automation)
openspec update                  # Refresh agent instructions and commands
```

### Common Workflows

```bash
# Check project status
openspec view

# Review a specific change
openspec show python-dev-environment

# Validate before implementation
openspec validate python-dev-environment --strict

# Archive completed work
openspec archive python-dev-environment --yes

# List all active changes with task progress
openspec list --changes
```

## Integration with Development Process

### Discussion Phase
- Draft change proposal
- Review and refine specs
- Align on requirements

### Planning Phase
- Finalize tasks.md with TDD steps
- **REQUIRED**: Validate spec formatting with `openspec validate <change> --strict`
- Ensure all requirements have scenarios
- Fix any validation errors before proceeding to implementation

### Implementation Phase
- Work through tasks incrementally
- Mark tasks complete as you go
- Reference specs for behavior

### Check Phase
- Run all automated checks (tests, types, linting)
- Review all tasks marked complete
- **READY FOR REVIEW** - Request user review explicitly
- **Address review concerns** - Iterate on feedback
- **USER APPROVAL RECEIVED** - Explicit consent required before archiving

### Archive Phase
- Verify all tasks complete AND user approval received
- Archive change to update source of truth
- Ready for next feature

## Best Practices

1. **One change per feature** - Keep changes focused and atomic
2. **Complete specs first** - Don't start implementation until specs are approved
3. **Use deltas** - Show only what changes, not entire specs
4. **Validate early and often** - Run `openspec validate <change> --strict` before implementation (REQUIRED)
5. **Include Check phase** - Every tasks.md must have a Check phase with review steps
6. **User review required** - Never archive without explicit user approval
7. **Archive promptly** - Don't let completed changes linger after approval

## Key Differences from .todo

- **OpenSpec** - Structured features and architecture changes with specs
- **.todo** - One-off fixes, investigations, and quick tasks without formal specs
