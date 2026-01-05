# Agent Catalog

This document defines all agents available in the Ongoing Agent Builder system, organized by ERP module. Each module has 6+ specialized agents that handle common tasks, bugs, and feature requests.

---

## Table of Contents

1. [Meta Agents (System-Level)](#meta-agents)
2. [Briefs Module Agents](#briefs-module)
3. [Time Tracking Module Agents](#time-tracking-module)
4. [Resource Planning Module Agents](#resource-planning-module)
5. [Leave Management Module Agents](#leave-management-module)
6. [RFP Module Agents](#rfp-module)
7. [Retainers Module Agents](#retainers-module)
8. [Studio Module Agents](#studio-module)
9. [CRM Module Agents](#crm-module)
10. [LMS Module Agents](#lms-module)
11. [Boards Module Agents](#boards-module)
12. [Workflow Module Agents](#workflow-module)
13. [Chat Module Agents](#chat-module)
14. [Analytics Module Agents](#analytics-module)
15. [Surveys Module Agents](#surveys-module)
16. [Integrations Module Agents](#integrations-module)
17. [Admin Module Agents](#admin-module)

---

## Meta Agents

These are system-level agents that operate across all modules or handle platform-wide concerns.

### 1. 🚀 Instance Deployment Agent
**ID:** `meta.deployment`
**Type:** Comprehensive / Long-running
**Model:** Opus (complex decision-making)

**Purpose:** Deploys new SpokeStack instances for new clients. Conducts an interview-style onboarding to understand the client's business, selects appropriate modules, and configures the initial instance.

**Capabilities:**
- Conducts conversational interview with client stakeholders
- Analyzes business type (agency, consultancy, SaaS, etc.)
- Recommends module bundle (ERP, Marketing, Agency, Full)
- Configures organization settings and branding
- Sets up initial users with appropriate permission levels
- Creates seed data (sample clients, projects, templates)
- Configures integrations (Slack, Google, etc.)
- Generates onboarding documentation
- Creates client-specific workflow templates

**Interview Topics:**
1. Business overview (industry, size, structure)
2. Team composition and departments
3. Client types and project workflows
4. Current tools and pain points
5. Priority modules and features
6. Branding assets and preferences
7. Integration requirements
8. Compliance/security needs

**Outputs:**
- Configured Vercel deployment
- Seeded database with org-specific data
- Custom onboarding guide
- Training recommendations

---

### 2. 🔍 Triage Agent
**ID:** `meta.triage`
**Type:** Fast / Classification
**Model:** Haiku (speed)

**Purpose:** Quickly analyzes incoming issues/requests and routes them to the appropriate specialized agent.

**Capabilities:**
- Classifies issue type (bug, feature, enhancement, question)
- Identifies affected module(s)
- Estimates complexity (simple/medium/complex)
- Assigns priority based on impact analysis
- Routes to specialized agent

---

### 3. 🔬 Research Agent
**ID:** `meta.research`
**Type:** Investigation
**Model:** Sonnet

**Purpose:** Deep-dives into complex issues to understand root causes before code changes.

**Capabilities:**
- Codebase exploration
- Error log analysis
- Database query investigation
- Performance profiling analysis
- Dependency auditing

---

### 4. 📝 Code Review Agent
**ID:** `meta.review`
**Type:** Validation
**Model:** Sonnet

**Purpose:** Reviews agent-generated code changes before PR creation.

**Capabilities:**
- Security vulnerability scanning
- Performance impact analysis
- Code style consistency
- Test coverage verification
- Breaking change detection

---

### 5. 📚 Documentation Agent
**ID:** `meta.docs`
**Type:** Documentation
**Model:** Sonnet

**Purpose:** Generates and updates technical documentation.

**Capabilities:**
- API documentation generation
- README updates
- CHANGELOG maintenance
- Module-specific CLAUDE.md files
- User guide updates

---

### 6. 🧪 Test Agent
**ID:** `meta.test`
**Type:** Testing
**Model:** Sonnet

**Purpose:** Creates and runs tests for code changes.

**Capabilities:**
- Unit test generation
- Integration test creation
- E2E test scenarios
- Test coverage analysis
- Regression testing

---

## Briefs Module

**Path:** `/spokestack/src/modules/briefs/`
**Description:** Work request management with 7 brief types, status workflows, and priority tracking.

### 1. Brief Status Workflow Agent
**ID:** `briefs.status-workflow`
**Type:** Feature/Enhancement
**Model:** Sonnet

**Handles:**
- Status transition logic bugs
- Adding new brief statuses
- Status permission rules
- Status history tracking issues
- Automated status transitions

**Common Tasks:**
- "Brief stuck in submitted status"
- "Add 'On Hold' status to workflow"
- "Auto-transition to In Progress when assignee starts timer"

---

### 2. Brief Assignment Agent
**ID:** `briefs.assignment`
**Type:** Feature/Bug
**Model:** Sonnet

**Handles:**
- Auto-assignment logic
- Workload-based assignment
- Department routing
- Reassignment workflows
- Notification on assignment

**Common Tasks:**
- "Briefs not routing to correct department"
- "Add bulk assignment feature"
- "Notify team lead when high-priority brief assigned"

---

### 3. Brief Timeline Agent
**ID:** `briefs.timeline`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Gantt chart view issues
- Due date calculations
- Dependency tracking
- Timeline conflicts
- Resource availability checks

**Common Tasks:**
- "Timeline view not showing overlapping briefs"
- "Add buffer time between related briefs"
- "Show resource conflicts on timeline"

---

### 4. Brief Kanban Agent
**ID:** `briefs.kanban`
**Type:** UI/Feature
**Model:** Sonnet

**Handles:**
- Kanban board drag-drop
- Column configuration
- Card display customization
- Filter/sort functionality
- Swimlane views

**Common Tasks:**
- "Drag-drop not working on mobile"
- "Add client grouping swimlanes"
- "Show time logged on kanban cards"

---

### 5. Brief Notification Agent
**ID:** `briefs.notifications`
**Type:** Feature/Bug
**Model:** Sonnet

**Handles:**
- Email notification logic
- Push notification triggers
- Slack integration for briefs
- Notification preferences
- Digest emails

**Common Tasks:**
- "Not receiving brief deadline reminders"
- "Add Slack notification when brief submitted"
- "Weekly brief summary email"

---

### 6. Brief Reporting Agent
**ID:** `briefs.reporting`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Brief metrics calculations
- Turnaround time analytics
- Department performance stats
- Export functionality
- Dashboard widgets

**Common Tasks:**
- "Average turnaround time incorrect"
- "Add brief completion rate chart"
- "Export briefs to CSV not working"

---

### 7. Brief Templates Agent
**ID:** `briefs.templates`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Brief template management
- Default field values
- Template permissions
- Clone brief functionality
- Template versioning

**Common Tasks:**
- "Template fields not copying correctly"
- "Add template categories"
- "Allow client-specific templates"

---

## Time Tracking Module

**Path:** `/spokestack/src/app/(platform)/time/`
**Description:** Timer mode, manual entry, timesheets, billable tracking.

### 1. Timer Agent
**ID:** `time.timer`
**Type:** Bug/Feature
**Model:** Sonnet

**Handles:**
- Start/stop timer logic
- Timer persistence across sessions
- Multiple timer handling
- Timer auto-pause/resume
- Background timer tracking

**Common Tasks:**
- "Timer resets when switching tabs"
- "Add idle detection to pause timer"
- "Allow multiple concurrent timers"

---

### 2. Timesheet Agent
**ID:** `time.timesheet`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Weekly/monthly views
- Timesheet approval workflow
- Bulk time entry
- Copy previous week
- Timesheet locking

**Common Tasks:**
- "Weekly total calculation wrong"
- "Add manager approval step"
- "Lock timesheets after submission"

---

### 3. Billable Hours Agent
**ID:** `time.billable`
**Type:** Analytics/Feature
**Model:** Sonnet

**Handles:**
- Billable vs non-billable logic
- Rate calculations
- Client billing reports
- Utilization tracking
- Invoice integration

**Common Tasks:**
- "Billable hours not matching invoice"
- "Add custom hourly rates per client"
- "Show utilization percentage on dashboard"

---

### 4. Time Entry Agent
**ID:** `time.entry`
**Type:** Bug/Feature
**Model:** Sonnet

**Handles:**
- Manual entry validation
- Entry editing rules
- Entry deletion logic
- Bulk entry operations
- Entry import/export

**Common Tasks:**
- "Can't edit time entry after 24 hours"
- "Allow backdated entries for admins"
- "Import time from CSV"

---

### 5. Time Reports Agent
**ID:** `time.reports`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Time summary reports
- Project time breakdowns
- Team productivity reports
- Export formats
- Scheduled reports

**Common Tasks:**
- "Monthly report showing wrong project hours"
- "Add PDF export for time reports"
- "Auto-send weekly time report to clients"

---

### 6. Time Integration Agent
**ID:** `time.integration`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- Calendar sync for time
- Brief-to-time linking
- External tool imports
- API for time data
- Webhook triggers

**Common Tasks:**
- "Sync time entries with Google Calendar"
- "Auto-log time from brief status changes"
- "Push time data to accounting system"

---

## Resource Planning Module

**Path:** `/spokestack/src/app/(platform)/resources/`
**Description:** Team capacity grids, availability tracking, workload balancing.

### 1. Capacity Grid Agent
**ID:** `resources.capacity`
**Type:** UI/Feature
**Model:** Sonnet

**Handles:**
- Capacity visualization
- Fuel gauge displays
- Overallocation warnings
- Department views
- Date range navigation

**Common Tasks:**
- "Capacity not updating in real-time"
- "Add color coding for overallocated"
- "Show capacity by skill set"

---

### 2. Availability Agent
**ID:** `resources.availability`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Availability tracking
- Leave integration
- Partial availability
- Timezone handling
- Recurring availability

**Common Tasks:**
- "Leave not reflecting in availability"
- "Add part-time schedules"
- "Handle remote team timezones"

---

### 3. Workload Balancer Agent
**ID:** `resources.balance`
**Type:** Feature/Algorithm
**Model:** Opus (complex optimization)

**Handles:**
- Workload distribution algorithm
- Auto-rebalancing suggestions
- Skill-based matching
- Priority-aware allocation
- Conflict resolution

**Common Tasks:**
- "Suggest optimal brief assignment"
- "Rebalance when someone goes on leave"
- "Match brief requirements to team skills"

---

### 4. Resource Forecast Agent
**ID:** `resources.forecast`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Future capacity prediction
- Pipeline impact analysis
- Hiring recommendations
- Seasonal planning
- What-if scenarios

**Common Tasks:**
- "Predict Q2 resource needs from pipeline"
- "When do we need to hire?"
- "Impact if we win RFP X"

---

### 5. Resource Reports Agent
**ID:** `resources.reports`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Utilization reports
- Allocation summaries
- Team performance metrics
- Historical trends
- Export functionality

**Common Tasks:**
- "Generate monthly utilization report"
- "Show allocation trends over time"
- "Export resource data to Excel"

---

### 6. Resource Alerts Agent
**ID:** `resources.alerts`
**Type:** Automation
**Model:** Haiku

**Handles:**
- Overallocation notifications
- Availability change alerts
- Capacity threshold warnings
- Manager escalations
- Slack notifications

**Common Tasks:**
- "Alert when someone is 120% allocated"
- "Notify PM when resource becomes available"
- "Weekly resource summary to leadership"

---

## Leave Management Module

**Path:** `/spokestack/src/app/(platform)/leave/`
**Description:** Time-off requests, approval workflows, balance tracking.

### 1. Leave Request Agent
**ID:** `leave.request`
**Type:** Feature/Bug
**Model:** Sonnet

**Handles:**
- Request submission flow
- Date validation
- Conflict detection
- Request editing
- Cancellation logic

**Common Tasks:**
- "Can't request leave overlapping public holiday"
- "Add half-day leave option"
- "Show team calendar when requesting"

---

### 2. Leave Approval Agent
**ID:** `leave.approval`
**Type:** Workflow
**Model:** Sonnet

**Handles:**
- Approval workflow logic
- Multi-level approvals
- Auto-approval rules
- Delegation during leave
- Rejection handling

**Common Tasks:**
- "Add team lead approval before HR"
- "Auto-approve if balance available"
- "Set up delegation when leave approved"

---

### 3. Leave Balance Agent
**ID:** `leave.balance`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Balance calculations
- Accrual logic
- Carryover rules
- Balance adjustments
- Anniversary-based accruals

**Common Tasks:**
- "Annual leave not accruing correctly"
- "Add carryover limit of 5 days"
- "Pro-rate balance for new joiners"

---

### 4. Leave Calendar Agent
**ID:** `leave.calendar`
**Type:** UI/Feature
**Model:** Sonnet

**Handles:**
- Calendar view display
- Team absence view
- Public holiday display
- Blackout period handling
- Calendar export

**Common Tasks:**
- "Team calendar not showing all leave"
- "Add department filter to calendar"
- "Sync leave to Google Calendar"

---

### 5. Leave Policy Agent
**ID:** `leave.policy`
**Type:** Configuration
**Model:** Sonnet

**Handles:**
- Leave type configuration
- Policy rule enforcement
- Country-specific policies
- Tenure-based entitlements
- Policy documentation

**Common Tasks:**
- "Add bereavement leave type"
- "Implement UAE labor law compliance"
- "Different policies for contractors"

---

### 6. Leave Reports Agent
**ID:** `leave.reports`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Leave summary reports
- Absence patterns
- Balance forecasts
- Compliance reports
- Export functionality

**Common Tasks:**
- "Generate annual leave report for audit"
- "Show absence trends by department"
- "Forecast leave liabilities"

---

## RFP Module

**Path:** `/spokestack/src/app/(platform)/rfp/`
**Description:** Request for proposal pipeline, win probability, document ingestion.

### 1. RFP Pipeline Agent
**ID:** `rfp.pipeline`
**Type:** Feature/UI
**Model:** Sonnet

**Handles:**
- Pipeline stage management
- Stage transition logic
- Win probability calculation
- Pipeline visualization
- Bulk stage updates

**Common Tasks:**
- "RFP stuck between stages"
- "Add custom pipeline stages"
- "Improve win probability algorithm"

---

### 2. RFP Document Agent
**ID:** `rfp.documents`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Document upload/parsing
- Requirement extraction
- Template matching
- Version control
- Collaborative editing

**Common Tasks:**
- "Parse RFP PDF to extract requirements"
- "Match requirements to past proposals"
- "Track document versions"

---

### 3. RFP Estimation Agent
**ID:** `rfp.estimation`
**Type:** Feature/Analytics
**Model:** Opus (complex analysis)

**Handles:**
- Effort estimation from requirements
- Cost calculation
- Resource planning
- Timeline generation
- Historical comparison

**Common Tasks:**
- "Estimate hours from RFP requirements"
- "Compare to similar past RFPs"
- "Generate preliminary timeline"

---

### 4. RFP Collaboration Agent
**ID:** `rfp.collaboration`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Team assignment to sections
- Progress tracking
- Comment/review system
- Deadline management
- Notification logic

**Common Tasks:**
- "Assign sections to team members"
- "Track who completed what"
- "Remind about section deadlines"

---

### 5. RFP Analytics Agent
**ID:** `rfp.analytics`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Win/loss analysis
- Pipeline forecasting
- Performance metrics
- Trend analysis
- Competitive insights

**Common Tasks:**
- "Why are we losing design RFPs?"
- "Forecast Q3 pipeline value"
- "Show win rate by client type"

---

### 6. RFP Conversion Agent
**ID:** `rfp.conversion`
**Type:** Workflow
**Model:** Sonnet

**Handles:**
- RFP to Project conversion
- Client creation from RFP
- Data migration logic
- Handoff documentation
- Kickoff automation

**Common Tasks:**
- "Convert won RFP to project"
- "Create client from RFP data"
- "Generate kickoff brief automatically"

---

## Retainers Module

**Path:** `/spokestack/src/app/(platform)/retainers/`
**Description:** Retainer period management, burn rate monitoring, scope changes.

### 1. Burn Rate Agent
**ID:** `retainers.burn`
**Type:** Analytics/Feature
**Model:** Sonnet

**Handles:**
- Hours burn calculation
- Burn rate visualization
- Pacing alerts
- Projected overrun
- Budget vs actual

**Common Tasks:**
- "Burn rate not updating real-time"
- "Alert at 80% burn threshold"
- "Show burn rate trend graph"

---

### 2. Scope Change Agent
**ID:** `retainers.scope`
**Type:** Workflow
**Model:** Sonnet

**Handles:**
- Scope change requests
- Approval workflow
- Impact assessment
- Budget adjustment
- Change log

**Common Tasks:**
- "Add scope change request form"
- "Require client approval for scope changes"
- "Track scope creep over time"

---

### 3. Retainer Health Agent
**ID:** `retainers.health`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Health score calculation
- Risk indicators
- Renewal probability
- Client satisfaction signals
- Proactive alerts

**Common Tasks:**
- "Calculate retainer health score"
- "Flag at-risk retainers"
- "Predict renewal likelihood"

---

### 4. Retainer Period Agent
**ID:** `retainers.period`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Period creation/rollover
- Hours allocation
- Period comparison
- Carryover logic
- Period locking

**Common Tasks:**
- "Auto-create next month period"
- "Allow hour carryover to next period"
- "Lock previous periods from editing"

---

### 5. Retainer Reports Agent
**ID:** `retainers.reports`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Client retainer reports
- Utilization summaries
- Value delivered reports
- Export for invoicing
- Executive summaries

**Common Tasks:**
- "Generate monthly client report"
- "Show value delivered vs hours used"
- "Export for finance team"

---

### 6. Retainer Alerts Agent
**ID:** `retainers.alerts`
**Type:** Automation
**Model:** Haiku

**Handles:**
- Burn threshold alerts
- Renewal reminders
- Period end notifications
- AM escalations
- Client notifications

**Common Tasks:**
- "Alert AM at 90% burn"
- "Reminder 30 days before renewal"
- "Notify client of remaining hours"

---

## Studio Module

**Path:** `/spokestack/src/modules/studio/`
**Description:** Content creation suite - calendars, video projects, pitch decks, moodboards.

### 1. Content Calendar Agent
**ID:** `studio.calendar`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Calendar CRUD operations
- Platform scheduling
- Content status workflow
- Bulk operations
- Calendar views

**Common Tasks:**
- "Content not appearing on correct date"
- "Add bulk content scheduling"
- "Filter calendar by platform"

---

### 2. AI Calendar Generator Agent
**ID:** `studio.ai-calendar`
**Type:** AI/Feature
**Model:** Opus (creative generation)

**Handles:**
- GPT-4 prompt engineering
- Content mix algorithms
- Platform cadence logic
- Holiday integration
- Sample generation for pitches

**Common Tasks:**
- "AI not generating varied content"
- "Add Ramadan-specific content"
- "Improve platform-specific suggestions"

---

### 3. Video Project Agent
**ID:** `studio.video`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Video project workflow
- Script management
- Storyboard functionality
- Shot list handling
- Review/approval flow

**Common Tasks:**
- "Add script revision tracking"
- "Link storyboard to shot list"
- "Approval workflow for video cuts"

---

### 4. Pitch Deck Agent
**ID:** `studio.decks`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Deck creation/editing
- Slide management
- Template system
- Export functionality
- Presentation mode

**Common Tasks:**
- "Slide reordering not saving"
- "Add new deck template"
- "Export deck to PDF"

---

### 5. Moodboard Agent
**ID:** `studio.moodboard`
**Type:** Feature/AI
**Model:** Sonnet

**Handles:**
- Image collection
- AI analysis
- Collaboration features
- Export options
- Conversation history

**Common Tasks:**
- "AI analysis taking too long"
- "Add Pinterest import"
- "Share moodboard with client"

---

### 6. Social Publishing Agent
**ID:** `studio.publish`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- Platform connections
- Publishing queue
- Post scheduling
- Publish status tracking
- Error handling

**Common Tasks:**
- "Instagram publish failing"
- "Add TikTok integration"
- "Retry failed publishes"

---

### 7. Content Approval Agent
**ID:** `studio.approval`
**Type:** Workflow
**Model:** Sonnet

**Handles:**
- Approval workflows
- Multi-stakeholder reviews
- Comment/feedback system
- Version comparison
- Client portal integration

**Common Tasks:**
- "Add client approval step"
- "Show diff between versions"
- "Approval reminders"

---

## CRM Module

**Path:** `/spokestack/src/app/(platform)/crm/`
**Description:** Contact management, deal pipeline, activity tracking.

### 1. Deal Pipeline Agent
**ID:** `crm.pipeline`
**Type:** Feature/UI
**Model:** Sonnet

**Handles:**
- Pipeline visualization
- Stage management
- Drag-drop functionality
- Funnel metrics
- Pipeline customization

**Common Tasks:**
- "Add new pipeline stage"
- "Funnel conversion rates incorrect"
- "Custom fields per stage"

---

### 2. Contact Management Agent
**ID:** `crm.contacts`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Contact CRUD
- Duplicate detection
- Contact enrichment
- Import/export
- Contact relationships

**Common Tasks:**
- "Merge duplicate contacts"
- "Import contacts from CSV"
- "Link contacts to companies"

---

### 3. Activity Tracking Agent
**ID:** `crm.activity`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Activity logging
- Email integration
- Call logging
- Meeting scheduling
- Activity timeline

**Common Tasks:**
- "Auto-log emails to contacts"
- "Add call outcome tracking"
- "Show activity timeline"

---

### 4. Deal Automation Agent
**ID:** `crm.automation`
**Type:** Workflow
**Model:** Sonnet

**Handles:**
- Stage change automations
- Task creation triggers
- Email sequences
- Reminder rules
- Win/loss automation

**Common Tasks:**
- "Auto-create task when deal moves stage"
- "Send follow-up email after 3 days"
- "Auto-set lost reason"

---

### 5. CRM Reports Agent
**ID:** `crm.reports`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Pipeline reports
- Sales forecasting
- Rep performance
- Win/loss analysis
- Export functionality

**Common Tasks:**
- "Monthly sales forecast report"
- "Win rate by lead source"
- "Rep leaderboard"

---

### 6. CRM Integration Agent
**ID:** `crm.integration`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- External CRM sync
- Email platform integration
- Calendar integration
- API endpoints
- Webhook configuration

**Common Tasks:**
- "Sync with HubSpot"
- "Connect to Calendly"
- "Expose CRM API"

---

## LMS Module

**Path:** `/spokestack/src/modules/lms/`
**Description:** Learning management with courses, modules, lessons, assessments.

### 1. Course Builder Agent
**ID:** `lms.courses`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Course CRUD
- Module/lesson structure
- Content types
- Prerequisites
- Course publishing

**Common Tasks:**
- "Add SCORM lesson support"
- "Implement prerequisites"
- "Course versioning"

---

### 2. Assessment Agent
**ID:** `lms.assessment`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Quiz creation
- Question types
- Grading logic
- Attempt management
- Passing criteria

**Common Tasks:**
- "Add matching question type"
- "Partial credit scoring"
- "Limit quiz attempts"

---

### 3. Enrollment Agent
**ID:** `lms.enrollment`
**Type:** Feature/Automation
**Model:** Sonnet

**Handles:**
- Enrollment workflows
- Auto-enrollment rules
- Enrollment expiry
- Bulk enrollment
- Waitlists

**Common Tasks:**
- "Auto-enroll new employees"
- "Add enrollment expiration"
- "Bulk enroll department"

---

### 4. Progress Tracking Agent
**ID:** `lms.progress`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Lesson completion
- Course progress calculation
- Time tracking
- Resume functionality
- Progress reports

**Common Tasks:**
- "Progress percentage wrong"
- "Remember video position"
- "Progress not syncing"

---

### 5. Certificate Agent
**ID:** `lms.certificates`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Certificate generation
- Template management
- Verification system
- Expiry handling
- Credential sharing

**Common Tasks:**
- "Custom certificate template"
- "Add LinkedIn share"
- "Certificate expiration"

---

### 6. LMS Reports Agent
**ID:** `lms.reports`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Completion reports
- Engagement analytics
- Compliance tracking
- Manager dashboards
- Export functionality

**Common Tasks:**
- "Compliance training report"
- "Course engagement metrics"
- "Manager team progress view"

---

## Boards Module

**Path:** `/spokestack/src/modules/boards/`
**Description:** Kanban-style project boards with cards, checklists, templates.

### 1. Board Agent
**ID:** `boards.board`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Board CRUD
- Column management
- Board permissions
- Board templates
- Archive/restore

**Common Tasks:**
- "Add board templates"
- "Column limit not enforcing"
- "Archive old boards"

---

### 2. Card Agent
**ID:** `boards.card`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Card CRUD
- Drag-drop movement
- Card details
- Assignments
- Due dates

**Common Tasks:**
- "Card drag not working on mobile"
- "Add card cover images"
- "Due date reminders"

---

### 3. Checklist Agent
**ID:** `boards.checklist`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Checklist creation
- Item management
- Progress calculation
- Checklist templates
- Assignment to items

**Common Tasks:**
- "Add checklist templates"
- "Assign users to items"
- "Checklist progress in card summary"

---

### 4. Board Automation Agent
**ID:** `boards.automation`
**Type:** Workflow
**Model:** Sonnet

**Handles:**
- Card movement triggers
- Due date automations
- Status updates
- Notifications
- Integration triggers

**Common Tasks:**
- "Auto-move card when checklist done"
- "Notify on overdue cards"
- "Create brief from card"

---

### 5. Board Views Agent
**ID:** `boards.views`
**Type:** UI/Feature
**Model:** Sonnet

**Handles:**
- View types (kanban, list, calendar)
- Filters/sorting
- Saved views
- Custom fields display
- View permissions

**Common Tasks:**
- "Add calendar view"
- "Save custom filters"
- "Timeline view for cards"

---

### 6. Board Integration Agent
**ID:** `boards.integration`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- Brief linking
- External board sync
- Slack notifications
- API endpoints
- Webhook triggers

**Common Tasks:**
- "Sync with Trello"
- "Post to Slack on card move"
- "Link cards to briefs"

---

## Workflow Module

**Path:** `/spokestack/src/modules/workflow-builder/`
**Description:** Visual workflow designer with triggers, steps, and automation.

### 1. Workflow Designer Agent
**ID:** `workflow.designer`
**Type:** Feature/UI
**Model:** Sonnet

**Handles:**
- Visual builder
- Step configuration
- Connection logic
- Validation rules
- Template creation

**Common Tasks:**
- "Add branching logic"
- "Validate before publish"
- "Create from template"

---

### 2. Workflow Trigger Agent
**ID:** `workflow.triggers`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Trigger types
- Trigger conditions
- Schedule triggers
- Manual triggers
- Webhook triggers

**Common Tasks:**
- "Add field change trigger"
- "Schedule daily workflows"
- "Webhook trigger not firing"

---

### 3. Workflow Execution Agent
**ID:** `workflow.execution`
**Type:** Feature/Bug
**Model:** Sonnet

**Handles:**
- Run processing
- Step execution
- Error handling
- Retry logic
- Timeout management

**Common Tasks:**
- "Workflow stuck at step"
- "Add retry on failure"
- "Timeout too short"

---

### 4. Workflow Action Agent
**ID:** `workflow.actions`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Action step types
- External integrations
- Data transformations
- Conditional actions
- Custom scripts

**Common Tasks:**
- "Add Slack action"
- "HTTP request action"
- "Transform data between steps"

---

### 5. Workflow Approval Agent
**ID:** `workflow.approval`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Approval steps
- Multi-approver logic
- Timeout/escalation
- Approval UI
- Delegation

**Common Tasks:**
- "Add multi-level approval"
- "Escalate if no response"
- "Approval on mobile"

---

### 6. Workflow Analytics Agent
**ID:** `workflow.analytics`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Run statistics
- Bottleneck detection
- Performance metrics
- Usage reports
- Optimization suggestions

**Common Tasks:**
- "Show avg step duration"
- "Identify slow workflows"
- "Failure rate report"

---

## Chat Module

**Path:** `/spokestack/src/app/(platform)/chat/`
**Description:** Internal messaging with channels, threads, presence.

### 1. Channel Agent
**ID:** `chat.channel`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Channel CRUD
- Channel types (public/private/DM)
- Member management
- Channel settings
- Archive/restore

**Common Tasks:**
- "Add private channels"
- "Channel permissions"
- "Archive inactive channels"

---

### 2. Message Agent
**ID:** `chat.message`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Message sending
- Threading
- Reactions
- Editing/deletion
- Rich text/markdown

**Common Tasks:**
- "Add thread replies"
- "Message edit history"
- "Code block formatting"

---

### 3. Notification Agent
**ID:** `chat.notifications`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Push notifications
- Mention alerts
- Read receipts
- Notification settings
- DND mode

**Common Tasks:**
- "@mention not notifying"
- "Add DND schedule"
- "Mute channel"

---

### 4. Search Agent
**ID:** `chat.search`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Message search
- File search
- Advanced filters
- Search indexing
- Search UI

**Common Tasks:**
- "Search not finding old messages"
- "Add filter by date"
- "Search in attachments"

---

### 5. Presence Agent
**ID:** `chat.presence`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Online/offline status
- Typing indicators
- Away detection
- Custom status
- Status sync

**Common Tasks:**
- "Status not updating"
- "Add custom status"
- "Mobile presence sync"

---

### 6. Chat Integration Agent
**ID:** `chat.integration`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- Slack bridging
- Bot integrations
- Webhook channels
- External notifications
- API for chat

**Common Tasks:**
- "Bridge to Slack"
- "Bot message formatting"
- "Incoming webhooks"

---

## Analytics Module

**Path:** `/spokestack/src/app/(platform)/analytics/`
**Description:** Dashboard builder, custom widgets, metrics tracking.

### 1. Dashboard Agent
**ID:** `analytics.dashboard`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Dashboard CRUD
- Layout management
- Widget arrangement
- Sharing/permissions
- Templates

**Common Tasks:**
- "Dashboard not saving layout"
- "Share dashboard with team"
- "Dashboard templates"

---

### 2. Widget Agent
**ID:** `analytics.widget`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Widget types
- Data configuration
- Visualization options
- Refresh logic
- Widget library

**Common Tasks:**
- "Add funnel widget"
- "Widget data stale"
- "Custom visualization"

---

### 3. Metrics Agent
**ID:** `analytics.metrics`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Metric definitions
- Calculations
- Aggregations
- Time comparisons
- Goal tracking

**Common Tasks:**
- "Create custom metric"
- "Compare to previous period"
- "Set metric goals"

---

### 4. Data Source Agent
**ID:** `analytics.datasource`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Internal data sources
- External connections
- Query building
- Data transformations
- Caching

**Common Tasks:**
- "Connect to BigQuery"
- "Optimize slow queries"
- "Cache analytics data"

---

### 5. Export Agent
**ID:** `analytics.export`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Report exports
- Scheduled reports
- Format options
- Email delivery
- API access

**Common Tasks:**
- "Schedule weekly report"
- "Export to PDF"
- "API for metrics"

---

### 6. Alert Agent
**ID:** `analytics.alerts`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Threshold alerts
- Anomaly detection
- Alert notifications
- Alert rules
- Alert history

**Common Tasks:**
- "Alert when metric drops"
- "Anomaly detection"
- "Alert escalation"

---

## Surveys Module

**Path:** `/spokestack/src/modules/survey/`
**Description:** Template-based surveys, question logic, distribution.

### 1. Survey Builder Agent
**ID:** `surveys.builder`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Survey creation
- Question types
- Logic rules
- Template system
- Preview

**Common Tasks:**
- "Add matrix question"
- "Conditional question logic"
- "Survey templates"

---

### 2. Distribution Agent
**ID:** `surveys.distribution`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Distribution channels
- Link generation
- Email sending
- WhatsApp integration
- Embed code

**Common Tasks:**
- "WhatsApp distribution"
- "Unique links per recipient"
- "Embed in website"

---

### 3. Response Agent
**ID:** `surveys.response`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Response collection
- Validation
- Progress saving
- Submission handling
- Thank you pages

**Common Tasks:**
- "Save partial responses"
- "Custom thank you page"
- "Response validation"

---

### 4. Survey Analytics Agent
**ID:** `surveys.analytics`
**Type:** Analytics
**Model:** Sonnet

**Handles:**
- Response analysis
- Visualization
- Cross-tabulation
- NPS calculation
- Export

**Common Tasks:**
- "Real-time results"
- "NPS trend chart"
- "Export responses"

---

### 5. Survey Automation Agent
**ID:** `surveys.automation`
**Type:** Workflow
**Model:** Sonnet

**Handles:**
- Trigger-based surveys
- Follow-up logic
- Reminder sequences
- Integration triggers
- Response workflows

**Common Tasks:**
- "Auto-send after project close"
- "Reminder if not completed"
- "Trigger workflow on submission"

---

### 6. NPS Agent
**ID:** `surveys.nps`
**Type:** Feature/Analytics
**Model:** Sonnet

**Handles:**
- NPS surveys
- Score calculation
- Trend tracking
- Segment analysis
- Benchmarking

**Common Tasks:**
- "NPS by client segment"
- "Track NPS over time"
- "Promoter follow-up"

---

## Integrations Module

**Path:** `/spokestack/src/modules/integrations/`
**Description:** Slack, Google Drive, Calendar, Analytics integrations.

### 1. Slack Agent
**ID:** `integrations.slack`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- Workspace connection
- Channel mapping
- Message sync
- Bot commands
- Notifications

**Common Tasks:**
- "Slack OAuth failing"
- "Map channel to project"
- "Add /brief command"

---

### 2. Google Drive Agent
**ID:** `integrations.drive`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- Drive connection
- Folder linking
- File sync
- Permissions
- Real-time sync

**Common Tasks:**
- "Link project folder"
- "Sync files bidirectionally"
- "Permission errors"

---

### 3. Google Calendar Agent
**ID:** `integrations.calendar`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- Calendar connection
- Event sync
- Meeting creation
- Availability check
- Calendar selection

**Common Tasks:**
- "Sync brief deadlines"
- "Show availability"
- "Create meeting from brief"

---

### 4. Google Analytics Agent
**ID:** `integrations.ga`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- GA4 connection
- Data fetching
- Dashboard widgets
- Metric mapping
- BigQuery sync

**Common Tasks:**
- "Connect GA4 property"
- "Pull website metrics"
- "Analytics widget"

---

### 5. Webhook Agent
**ID:** `integrations.webhooks`
**Type:** Integration
**Model:** Sonnet

**Handles:**
- Webhook configuration
- Event subscriptions
- Delivery management
- Retry logic
- Security

**Common Tasks:**
- "Add webhook for brief create"
- "Webhook not delivering"
- "Webhook signature"

---

### 6. API Key Agent
**ID:** `integrations.api`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- API key generation
- Scope management
- Rate limiting
- Key rotation
- Usage tracking

**Common Tasks:**
- "Generate API key"
- "Limit key scope"
- "Track API usage"

---

## Admin Module

**Path:** `/spokestack/src/app/(platform)/admin/`
**Description:** Organization settings, user management, permissions.

### 1. User Management Agent
**ID:** `admin.users`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- User CRUD
- Role assignment
- Permission levels
- Bulk operations
- User provisioning

**Common Tasks:**
- "Add new user"
- "Bulk permission update"
- "Deactivate user"

---

### 2. Permission Agent
**ID:** `admin.permissions`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Permission configuration
- Access policies
- Role definitions
- Module access
- Feature flags

**Common Tasks:**
- "Add custom role"
- "Restrict module access"
- "Permission not working"

---

### 3. Organization Agent
**ID:** `admin.org`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Org settings
- Branding
- Domain configuration
- Billing (if applicable)
- Org metadata

**Common Tasks:**
- "Update org branding"
- "Configure custom domain"
- "Org settings not saving"

---

### 4. Audit Log Agent
**ID:** `admin.audit`
**Type:** Feature/Security
**Model:** Sonnet

**Handles:**
- Audit log querying
- Log retention
- Export functionality
- Alert rules
- Compliance reporting

**Common Tasks:**
- "Search audit logs"
- "Set log retention"
- "Audit export for compliance"

---

### 5. Notification Config Agent
**ID:** `admin.notifications`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Notification templates
- Delivery rules
- Channel configuration
- User preferences
- Notification testing

**Common Tasks:**
- "Edit email template"
- "Configure notification rules"
- "Test notification"

---

### 6. Data Management Agent
**ID:** `admin.data`
**Type:** Feature
**Model:** Sonnet

**Handles:**
- Data import/export
- Bulk operations
- Data cleanup
- Migration tools
- Backup/restore

**Common Tasks:**
- "Import clients from CSV"
- "Clean up old data"
- "Export all org data"

---

## Agent Selection Matrix

| Issue Type | Complexity | Recommended Agent Type | Model |
|------------|------------|----------------------|-------|
| Bug report | Simple | Module-specific agent | Haiku |
| Bug report | Complex | Research + Module agent | Sonnet |
| Feature request | Simple | Module-specific agent | Sonnet |
| Feature request | Complex | Research + Module agent | Opus |
| Question | Any | Research agent | Haiku/Sonnet |
| New instance | N/A | Deployment Agent | Opus |
| Multi-module | Complex | Orchestrated multi-agent | Opus |

---

## Dynamic Model Selection

Agents use adaptive model selection based on:

1. **Complexity Score** (1-10): Estimated from issue analysis
2. **Token Estimate**: Predicted output length
3. **Tool Requirements**: Number/type of tools needed
4. **Historical Performance**: Success rate by model for similar issues

```typescript
function selectModel(issue: AgentIssue): ModelChoice {
  const complexity = calculateComplexity(issue);
  const tokenEstimate = estimateTokens(issue);

  if (complexity >= 8 || issue.type === 'deployment') {
    return 'opus';
  }

  if (complexity <= 3 && tokenEstimate < 1000) {
    return 'haiku';
  }

  return 'sonnet';
}
```

---

## Total Agent Count

| Category | Count |
|----------|-------|
| Meta Agents | 6 |
| Briefs | 7 |
| Time Tracking | 6 |
| Resource Planning | 6 |
| Leave Management | 6 |
| RFP | 6 |
| Retainers | 6 |
| Studio | 7 |
| CRM | 6 |
| LMS | 6 |
| Boards | 6 |
| Workflow | 6 |
| Chat | 6 |
| Analytics | 6 |
| Surveys | 6 |
| Integrations | 6 |
| Admin | 6 |
| **Total** | **104** |
