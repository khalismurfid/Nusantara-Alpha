# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`

**Created**: [DATE]

**Status**: Draft

**Input**: User description: "$ARGUMENTS"

## Constitution Alignment *(mandatory)*

<!--
  ACTION REQUIRED: Fill this section before writing user stories. Keep answers
  product-facing and technology-agnostic unless the user explicitly requested an
  implementation detail.
-->

- **Educational boundary**: [How the feature avoids financial advice, buy/sell
  recommendations, guaranteed profit, personalized investment guidance, and
  allocation advice]
- **Real-money execution boundary**: [How the feature avoids placing trades,
  routing orders, connecting prediction outputs to brokerage execution, or
  automating real-money decisions]
- **Chronology and leakage boundary**: [What time-order assumptions, data
  availability rules, or leakage risks apply]
- **Market-data quality and bias**: [What risks apply around survivorship bias,
  corporate actions, delistings, trading halts, missing sessions, stale prices,
  illiquidity, exchange-calendar alignment, or ticker identity changes]
- **Evidence before prediction**: [What evidence, evaluation context,
  limitations, or methodology users can inspect before or alongside outputs]
- **Uncertainty and limitations**: [How confidence, uncertainty, assumptions,
  incomplete data, or weak evidence are communicated]
- **Curated model access**: [How any customer-facing model is intentionally
  selected and how experimental, deprecated, or unvalidated models are excluded]
- **Traceability**: [Which model version, data period, feature timestamp,
  prediction timestamp, ticker, and evaluation context are captured]
- **Data governance**: [What public, mock, sample, licensed, or private data is
  used and how secrets or restricted data are kept out of outputs]
- **User clarity**: [How the main journey remains understandable to non-experts:
  inspect evidence, choose stock, request prediction, understand risk]

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases. For prediction, model, data,
  validation, paper-trading, or evidence features, include chronology,
  market-data quality, bias, no-real-money-execution, uncertainty,
  curated-model, disclaimer, and traceability cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?
- How does the system behave when evidence is insufficient, stale, unstable, or
  unavailable?
- How does the system prevent prediction output when only uncurated,
  experimental, deprecated, or unvalidated models are available?
- How does the system preserve chronology when market data, features, labels, or
  evaluation windows have different timestamps?
- How does the system handle survivorship bias, corporate actions, delistings,
  trading halts, missing sessions, stale prices, illiquidity, exchange-calendar
  alignment, or ticker identity changes?
- How does the system prevent simulated prediction or paper-trading flows from
  triggering real-money trading or brokerage execution?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

For prediction, model, data, validation, paper-trading, or evidence features,
include requirements for educational framing, no real-money execution,
chronological integrity, market-data quality and bias controls, inspectable
evidence, uncertainty, curated model access, traceability metadata, data
governance, and error handling.

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- [Assumption about target users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope boundaries, e.g., "Mobile support is out of scope for v1"]
- [Assumption about data/environment, e.g., "Existing authentication system will be reused"]
- [Dependency on existing system/service, e.g., "Requires access to the existing user profile API"]
