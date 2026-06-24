# Incident Escalation Chain

How to escalate incidents and who to contact.

## Severity Levels

| Level | Response Time | Who to Page | Example |
|-------|----------------|------------|---------|
| **P0 - Critical** | 5 min | Oncall eng + manager | Data loss, auth broken, all users affected |
| **P1 - High** | 15 min | Oncall eng | API down for subset of users, degraded performance |
| **P2 - Medium** | 1 hour | Oncall eng | Feature broken, errors elevated but service up |
| **P3 - Low** | 4 hours | File issue | Bug, minor feature broken |
| **P4 - Info** | 1 day | Slack channel | Nice-to-fix, observability only |

## Escalation Flow

### P0 (Critical)

1. **Declare incident** (call, not Slack)
   - Who: First responder (oncall)
   - Message: "P0 incident: [brief description]"

2. **Page escalation** (PagerDuty or similar)
   - Engineering lead
   - On-call manager
   - Database team (if DB affected)

3. **Status page update** (within 5 min)
   - Communicate to customers
   - Update every 15 min

4. **War room** (Zoom or similar)
   - Led by incident commander
   - Engineering lead + oncall + manager + comms
   - Document in shared doc

5. **Post-incident** (within 24 hours)
   - Postmortem (POSTMORTEM_TEMPLATE.md)
   - Action items assigned
   - Follow-up in 1 week

### P1 (High)

1. **Slack #incidents channel**
   - Who: Oncall engineer
   - Message: "P1 incident: [description]"

2. **Page oncall engineer**
   - If not already engaged

3. **Investigate** (15 min)
   - Use RUNBOOKS.md
   - Document findings

4. **Communicate** (Slack update)
   - Status every 30 min
   - ETA for resolution

5. **Postmortem** (if root cause systemic)
   - Lightweight: 1-2 hours
   - Action items if applicable

### P2 (Medium)

1. **Slack #incidents channel**
   - Who: First observer
   - Message: "P2 incident: [description]"

2. **Assign to engineer**
   - Can be lower-priority oncall
   - 1-4 hour SLA

3. **Investigate during business hours**
   - Fix or escalate

### P3-P4 (Low/Info)

1. **GitHub issue**
   - Label: `bug` or `enhancement`
   - Prioritize in planning

## Oncall Rotation

| Week | Engineer | Manager |
|------|----------|---------|
| Week of 06-23 | @alice | @bob |
| Week of 06-30 | @charlie | @dave |

**Handoff:** Friday 4pm UTC

## Escalation Triggers

Escalate from P2→P1 if:
- Still broken after 30 min investigation
- Affecting multiple customers
- Root cause unknown

Escalate from P1→P0 if:
- Data loss risk
- Full service down
- Multiple critical systems affected
- Customer SLA breach

## Communication Templates

### Initial notification (P1)
```
P1 incident: [service] [description]
Status: Investigating
ETA: TBD
Lead: @oncall
```

### Update (every 30 min for P1)
```
Status: [Investigating|Diagnosing|Mitigating|Resolved]
Latest: [what we found/did]
ETA: [estimated time to resolution]
```

### Resolution
```
Status: Resolved
Root cause: [one sentence]
Impact: [X users, Y minutes]
Postmortem: [link to doc]
```

## Tools

- **Page oncall:** PagerDuty, Opsgenie, or call
- **War room:** Zoom, Google Meet
- **Chat:** Slack #incidents
- **Documentation:** Google Doc (shared)
- **Status page:** Statuspage.io or similar
