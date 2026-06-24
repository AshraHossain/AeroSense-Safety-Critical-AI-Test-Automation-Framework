# Postmortem: [Incident Title]

**Date:** YYYY-MM-DD  
**Duration:** HH:MM - HH:MM (X minutes)  
**Severity:** P1 (critical) / P2 (high) / P3 (medium) / P4 (low)  
**Lead:** [Name]

## Summary
[1-2 sentences describing what happened and impact]

## Timeline

| Time | Event |
|------|-------|
| HH:MM | Initial incident detection |
| HH:MM | Alert triggered |
| HH:MM | Oncall paged |
| HH:MM | Diagnosis: [root cause hypothesis] |
| HH:MM | Mitigation: [action taken] |
| HH:MM | Incident resolved |

## Impact

- **Users affected:** X
- **Duration:** Y minutes
- **Services down:** [list]
- **Data loss:** Yes / No
- **Customer notifications sent:** Yes / No

## Root Cause

[Describe the underlying cause, not just the symptom]

**Why was this not caught earlier?**
- [Missing alert condition]
- [Missing test case]
- [Manual process that failed]

## Resolution

[What was done to fix it]

### Immediate (0-1 hour)
- [ ] Mitigated impact
- [ ] Alerted stakeholders
- [ ] Documented incident

### Short-term (1-24 hours)
- [ ] Root cause analysis
- [ ] Temporary workaround deployed
- [ ] Monitoring improved

### Long-term (1+ week)
- [ ] Permanent fix implemented
- [ ] Tests added to prevent recurrence
- [ ] Documentation updated

## Lessons Learned

### What went well
- [Positive aspect of response]

### What went poorly
- [What could be better]

### What we learned
- [Key insight]

## Action Items

| Item | Owner | Due | Priority |
|------|-------|-----|----------|
| Add alert for [condition] | @oncall | 1 week | P0 |
| Test [scenario] | @qa | 2 weeks | P1 |
| Update [docs] | @eng | 1 week | P2 |

## Prevention

**How to prevent this in the future:**
1. [Specific alert or monitoring]
2. [Specific test case]
3. [Specific process change]

## Follow-up

- [ ] Action items tracked in issue tracker
- [ ] Postmortem shared with team
- [ ] Metrics reviewed (didn't this happen before?)
- [ ] Similar issues searched (is this systemic?)

**Postmortem review date:** [1 week after incident]

---

**No blame culture:** This postmortem documents system/process failures, not individual failures. Everyone did their best with available information.
