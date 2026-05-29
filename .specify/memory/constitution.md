<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles:
- II. Chronological Integrity -> III. Chronological Integrity
- III. Evidence Before Prediction -> V. Evidence Before Prediction
- IV. Honest Uncertainty -> VI. Honest Uncertainty
- V. Curated Model Access -> VII. Curated Model Access
- VI. Reproducibility and Traceability -> VIII. Reproducibility and Traceability
- VII. Separation of Concerns -> IX. Separation of Concerns
- VIII. Testability -> X. Testability
- IX. User Clarity -> XI. User Clarity
- X. Data Governance -> XII. Data Governance
- XI. Simplicity Before Complexity -> XIII. Simplicity Before Complexity
- XII. Academic and Portfolio Integrity -> XIV. Academic and Portfolio Integrity
Added principles:
- II. No Real-Money Execution
- IV. Market Data Integrity and Bias Control
Added sections: None
Removed sections: None
Templates requiring updates:
- Updated: .specify/templates/plan-template.md
- Updated: .specify/templates/spec-template.md
- Updated: .specify/templates/tasks-template.md
- Updated: .specify/templates/checklist-template.md
- Reviewed, no update required: .specify/templates/commands/*.md was not present
- Reviewed, no update required: .specify/extensions/git/commands/*.md
- Reviewed, no update required: AGENTS.md
Follow-up TODOs: None
-->
# Nusantara Alpha Constitution

## Core Principles

### I. No Financial Advice
Nusantara Alpha MUST frame every prediction, backtest, paper-trading result,
portfolio demonstration, and performance discussion as educational research only.
The product MUST NOT present outputs as financial advice, buy/sell
recommendations, guaranteed profit, personalized investment guidance, or
portfolio allocation advice. User-facing prediction and performance views MUST
include clear risk and educational-use disclaimers.

Rationale: The product exists for learning, methodology review, and portfolio
demonstration. Clear boundaries protect users, reviewers, and the project from
misleading financial claims.

### II. No Real-Money Execution
Nusantara Alpha MUST NOT place real trades, route orders, connect prediction
outputs to brokerage execution, or automate real-money trading decisions. Any
portfolio, backtest, or trading workflow MUST be simulated, educational, and
clearly labelled as not executable investment activity.

Rationale: The product is an educational prediction and portfolio demonstration
project, not a trading or brokerage system.

### III. Chronological Integrity
All modelling, feature engineering, validation, backtesting, paper-trading, and
prediction workflows MUST preserve time order. Historical simulations and
next-session predictions MUST use only information that would have been
available at the relevant prediction timestamp. Future labels, revised data,
post-event features, or validation leakage MUST NOT influence earlier
predictions.

Rationale: Equity prediction results are invalid if future information leaks
into training, validation, or inference.

### IV. Market Data Integrity and Bias Control
Market data used for modelling, validation, backtesting, paper-trading, and
prediction MUST be evaluated for quality and bias risks before it supports a
user-facing result. Specifications and plans MUST address relevant risks such
as survivorship bias, corporate actions, delistings, trading halts, missing
sessions, stale prices, illiquidity, exchange-calendar alignment, and ticker
identity changes when those risks can affect the feature.

Rationale: Time order alone is not enough; equity prediction evidence can be
misleading when market-data quality and market-structure biases are ignored.

### V. Evidence Before Prediction
Users MUST be able to inspect relevant model evidence before or alongside any
prediction output. Evidence MUST include the selected model identity, model
version when available, evaluation period, historical performance context,
known limitations, and the interpretation boundary for the displayed output.

Rationale: Predictions without accessible evidence encourage overconfidence and
make educational review weaker.

### VI. Honest Uncertainty
Prediction outputs MUST communicate confidence, uncertainty, assumptions, and
limitations in plain language. Weak, unstable, incomplete, stale, or
data-limited evidence MUST be visibly identified and MUST NOT be hidden,
downplayed, or marketed as stronger than it is.

Rationale: Honest uncertainty is required for responsible learning, academic
review, and recruiter review.

### VII. Curated Model Access
Customer-facing flows MUST expose only models that have been intentionally
selected for display through a curated registry, allowlist, or equivalent
selection mechanism. Experimental, deprecated, unvalidated, or internal-only
models MUST NOT appear in the main customer-facing flow. Changes to model
visibility MUST be deliberate and traceable.

Rationale: Users need a controlled, understandable model surface rather than
accidental access to unfinished experiments.

### VIII. Reproducibility and Traceability
Important outputs MUST be traceable to the model version, data period, feature
timestamp, prediction timestamp, selected ticker, and evaluation context used to
generate them. Prediction, backtest, and paper-trading artifacts MUST retain
enough metadata to reproduce or explain the result within the limits of the
available data.

Rationale: Reviewers and future maintainers must be able to understand how a
result was produced.

### IX. Separation of Concerns
The system MUST keep user experience, application logic, model logic, data
processing, validation, storage, and documentation in separate ownership
boundaries. Core model logic MUST NOT be embedded directly in interface code.
Shared contracts between layers MUST be explicit enough to test independently.

Rationale: Clear boundaries reduce leakage risk, improve testability, and keep
the product maintainable as modelling and interface work evolve.

### X. Testability
Critical behaviour MUST be covered by automated or otherwise repeatable tests.
Required coverage includes leakage prevention, chronological validation,
market-data quality controls, bias controls, no-real-money-execution safeguards,
model selection rules, prediction output structure, risk disclaimers,
traceability metadata, and error handling. Any exception MUST be documented
with a concrete risk, mitigation, and follow-up path before implementation is
considered complete.

Rationale: The highest-risk behaviours are governance and correctness issues,
not cosmetic features.

### XI. User Clarity
The main user journey MUST remain understandable to non-expert users: inspect
evidence, choose a stock, request a prediction, and understand risk. User-facing
language MUST avoid unexplained jargon and MUST distinguish educational
predictions from investment decisions.

Rationale: The product serves learners and reviewers who need clear context, not
opaque modelling language.

### XII. Data Governance
The project MUST NOT expose secrets, credentials, private datasets, proprietary
data, or licensed data beyond its allowed use. Demonstrations MUST use sample,
mock, public, or otherwise permitted data. Data provenance, availability
assumptions, and sensitive configuration boundaries MUST be documented when
they affect product behaviour.

Rationale: Data misuse creates legal, ethical, and reproducibility risks.

### XIII. Simplicity Before Complexity
The project MUST prioritize a working, well-structured, honest product flow
before complex modelling, infrastructure, or visual features. Added complexity
MUST have a documented reason tied to user value, correctness, reproducibility,
or maintainability.

Rationale: A simple and truthful educational product is more valuable than an
opaque system with inflated capability claims.

### XIV. Academic and Portfolio Integrity
The project MUST remain suitable for academic review and recruiter review.
Methodology, assumptions, limitations, and evaluation choices MUST be documented
clearly. Claims about predictive quality, realism, or performance MUST be
proportional to the evidence available.

Rationale: Nusantara Alpha is a portfolio and educational artifact; credibility
depends on honest scope and transparent methodology.

## Product Constraints

- Prediction views MUST display educational framing, risk disclaimers, ticker,
  prediction horizon, prediction timestamp, model identity, evaluation context,
  uncertainty, and known limitations.
- Prediction outputs MUST NOT trigger, route, or automate real-money trade
  execution.
- Backtests and paper-trading results MUST be labelled as simulated educational
  demonstrations and MUST NOT imply achievable real-world returns.
- Data and feature artifacts used for modelling MUST record an availability
  timestamp or a documented availability assumption, and MUST document material
  market-data quality and bias assumptions.
- Customer-facing model selectors MUST be backed by a curated model registry,
  allowlist, or equivalent explicit selection mechanism.
- Public examples, screenshots, tests, and demos MUST avoid secrets, credentials,
  private datasets, and proprietary data unless the repository documents that
  exposure is permitted.

## Development Workflow and Quality Gates

- Every specification MUST state how the feature handles advice boundaries,
  real-money execution boundaries, chronology, market-data quality and bias,
  evidence, uncertainty, traceability, curated model access, data governance,
  and user clarity.
- Every implementation plan MUST pass the Constitution Check before research and
  MUST re-check it after design.
- Prediction, model, data, validation, and customer-facing evidence features
  MUST include tasks and tests for chronological integrity, leakage prevention,
  market-data quality and bias controls, no-real-money-execution safeguards,
  curated model selection, output traceability, disclaimers, and error handling.
- Reviews MUST block changes that violate the constitution unless the
  constitution is amended first.
- Documentation for user-facing prediction features MUST describe methodology,
  limitations, assumptions, and evaluation context.

## Governance

This constitution supersedes conflicting specifications, plans, tasks, and
informal project practices. All future Spec Kit artifacts and implementations
MUST comply with it.

Amendments MUST include a written rationale, a summary of affected principles or
sections, a semantic version change, and updates to dependent templates when the
change affects specification, planning, task generation, or review workflows.

Versioning follows semantic governance:
- MAJOR: Backward-incompatible principle removals or redefinitions.
- MINOR: New principles, new sections, or materially expanded governance.
- PATCH: Clarifications, wording fixes, and non-semantic refinements.

Compliance review is required at specification, planning, task generation, and
implementation review. Any justified exception MUST be recorded in the plan's
Complexity Tracking section with mitigation and follow-up work.

**Version**: 1.1.0 | **Ratified**: 2026-05-26 | **Last Amended**: 2026-05-26
