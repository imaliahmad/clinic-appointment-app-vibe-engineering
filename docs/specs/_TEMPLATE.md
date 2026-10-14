# <Feature name>
Status: draft | approved | building | built | tested | reviewed | done
Plan item: <number from docs/PLAN.md>
Branch: feature/NN-short-name

## Goal
One or two sentences: what the user can do after this feature.

## Changes
- `path/to/file.py`: what changes
- ...

## Steps
1. <Step name>
   - Build: what gets implemented
   - Check: exact manual test (URL, what to click/run, expected result)
2. ...
3. ...
4. ...
5. ...

## Test cases
Each case gets an ID so tests and results can refer to it.

### Unit (pure rules in `app/rules/`)
- U1: <inputs> → <expected result>
- U2: <boundary case> → <expected result>

### API (`tests/api/`)
- A1: <request> → <status code, expected data>
- A2: <bad input> → 400, `status: false`
- A3: not logged in → 401
- A4: wrong role → 403

### Postman (`postman/clinic.postman_collection.json`)
- P1: <folder> / <request name> → <expected>

## Out of scope
What this feature deliberately does not do.

## Test results (Phase 3, updated in Phase 5)
| Level | Result |
|---|---|
| Unit | |
| API | |
| Postman | |
Coverage: each case ID → test name.
Spec gaps found: 

## Review summary (Phase 4)
- Code changed in review: yes / no (files: )
- Must fix: 
- Should fix applied: 
- Skipped: 

## AI usage
| | Session % | Weekly % |
|---|---|---|
| Before | | |
| After | | |
| Used | | |
Model(s): 
Tokens (from ccusage / tracker): 
