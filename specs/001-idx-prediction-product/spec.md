# Feature Specification: Nusantara Alpha Customer Prediction Product

**Feature Branch**: `001-idx-prediction-product`

**Created**: 2026-05-26

**Status**: Draft

**Input**: User description: "Build Nusantara Alpha, a customer-facing
Indonesian equity prediction product for curated model evidence review, IDX
stock selection, next-market-session predictions, educational framing,
uncertainty, traceability, public portfolio-demo access, and no financial
advice."

## Clarifications

### Session 2026-05-26

- Q: What counts as a curated/approved model in the customer-facing flow? → A: A model is approved only if it has display approval, historical evidence, evaluation period, supported universe, known limitations, and traceability metadata.
- Q: What evidence must users see before requesting a prediction? → A: Users must see an evidence summary with key metrics, evaluation period, supported universe, known limitations, data-quality notes, and historical-performance caveat.
- Q: What happens when evidence is weak or missing? → A: Allow predictions with prominent limitations when evidence is weak or data-limited; block only when required evidence is missing.
- Q: How should confidence be explained to users? → A: Show Low/Medium/High confidence with plain-language explanation; optional numeric score in details.
- Q: How should unsupported IDX stocks be handled? → A: Let users search or enter unsupported stocks, show them as unavailable with a reason, block prediction until removed or replaced, and track aggregate non-personal interest for future support planning.
- Q: Can the public demo use mock models or dummy predictions? → A: Public demo must use real approved models only; mock/demo models and dummy predictions are local or experimental only.
- Q: What data may the public demo use when live/current data is unavailable? → A: It may use public, delayed, static, or otherwise approved non-sensitive data with data-as-of and limitations shown.

### Session 2026-05-29

- MVP local review feedback: The first working skeleton is functionally present
  but not acceptable as a customer-facing experience. The product must move to
  a prediction-first, clearer, less text-heavy interface with more natural
  user-facing language, calmer limitation copy, readable grouping, and a
  polished reviewer-ready presentation.
- Prediction interaction decision: Once a valid model and supported ticker are
  selected and required evidence is available, the prediction should become the
  primary visible content and should appear automatically or with a minimal
  action labelled in plain language such as "Predict". The product must not use
  awkward academic action labels such as "Request educational prediction".
- Evidence balance decision: Evidence-before-prediction remains mandatory, but
  evidence should be presented as a concise, readable summary before or
  alongside the prediction-first experience, with detailed methodology and
  traceability available in secondary sections.

## Constitution Alignment *(mandatory)*

- **Educational boundary**: The product frames all predictions, model evidence,
  backtests, and paper-trading summaries as educational research and portfolio
  demonstration. It must not provide financial advice, buy/sell instructions,
  guaranteed returns, personalized guidance, position sizing, or allocation
  advice.
- **Real-money execution boundary**: The product does not place trades, route
  orders, connect prediction outputs to brokerage execution, or automate
  real-money decisions. All prediction and paper-trading views are simulated
  educational experiences.
- **Chronology and leakage boundary**: Next-market-session predictions and
  historical evidence must be tied to explicit data-as-of and prediction
  timestamps. The product must distinguish historical evidence from future
  prediction and must not present evidence that depends on information
  unavailable at the relevant prediction time.
- **Market-data quality and bias**: Model evidence and prediction availability
  must identify relevant data risks, including missing data, stale data,
  survivorship bias, corporate actions, delistings, trading halts, missing
  sessions, illiquidity, exchange-calendar alignment, and ticker identity
  changes when those risks affect the selected model or stock.
- **Evidence before prediction**: Users must be able to review selected model
  evidence before requesting predictions. Evidence includes historical
  performance, evaluation period, supported stock universe, known limitations,
  and paper-trading evidence when available.
- **Uncertainty and limitations**: Prediction outputs explain confidence as
  Low/Medium/High model uncertainty, not correctness. A numeric score may be
  shown in details, but plain-language explanation must come first. Weak,
  unstable, missing, incomplete, or data-limited evidence is shown plainly and
  is not hidden behind positive product language.
- **Curated model access**: The customer-facing flow exposes only approved
  curated models. Experimental, deprecated, hidden, unavailable, or unapproved
  models are excluded from selection and cannot generate predictions.
- **Traceability**: Every prediction output records the selected stock ticker,
  prediction target, selected model name, selected model identifier or version,
  data-as-of timestamp, prediction timestamp, and relevant evaluation context.
- **Data governance**: The product must avoid exposing secrets, credentials,
  private datasets, or proprietary data. Local demonstrations and experiments
  may use permitted sample or mock data; the public demo uses real approved
  models with public, delayed, static, or otherwise approved non-sensitive data.
- **User clarity**: The main journey remains simple for non-expert users:
  choose a curated model, choose supported IDX stocks, immediately understand
  the prediction, inspect the supporting evidence and limitations, and
  understand risk without reading dense internal-style text.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explore a Supported Prediction (Priority: P1)

A retail-style user opens Nusantara Alpha, sees clear educational framing,
chooses an approved prediction model, selects one or more supported IDX stocks,
and immediately sees a readable next-market-session prediction view centered on
the selected ticker, model signal, confidence, key context, and limitations.
The user can inspect concise evidence before interpreting the output and can
open deeper methodology or traceability details without the main screen feeling
like an internal experiment tracker.

**Why this priority**: This is the primary product journey and the minimum
valuable experience for users, recruiters, and project reviewers.

**Independent Test**: A tester can complete the full journey with one approved
model and one supported IDX stock, then verify that the prediction is the
primary visible content, the output includes all required fields, the wording is
natural for non-expert users, and no financial-advice language appears.

**Acceptance Scenarios**:

1. **Given** at least one approved model with evidence and one supported IDX
   stock, **When** the user selects the model, reviews evidence, selects the
   stock, and requests a prediction, **Then** the product displays a structured
   next-market-session prediction with signal, confidence, context,
   limitations, model identifier or version, data-as-of timestamp, prediction
   timestamp, evaluation context, evidence reference, and educational
   disclaimer.
2. **Given** the user is viewing the prediction flow, **When** the disclaimer is
   presented, **Then** it clearly states that predictions are educational
   research and not financial advice, buy/sell recommendations, guaranteed
   profit, personalized guidance, position sizing, or allocation advice.
3. **Given** a prediction output is displayed, **When** the user reads the
   confidence field, **Then** the product shows a Low/Medium/High category and
   explains confidence as model uncertainty, not as a guarantee that the
   prediction is correct.
4. **Given** the user has selected a valid model and supported ticker, **When**
   required evidence and data are available, **Then** the prediction area is the
   main visual focus and shows ticker, signal, confidence, context, and key
   limitations before secondary technical details.
5. **Given** a manual prediction action is still required, **When** the user
   reaches the action, **Then** the label uses simple product language such as
   "Predict" and does not use awkward academic wording.
6. **Given** the user views the main prediction screen, **When** limitations or
   evidence summaries are shown, **Then** they are readable as plain product
   guidance rather than raw metadata, isolated tags, or cell-like debug text.

---

### User Story 2 - Review Model Evidence and Limitations (Priority: P2)

A recruiter, technical reviewer, or project reviewer selects a curated model and
inspects its historical evidence, evaluation period, supported universe,
limitations, data-quality caveats, and methodology context before interpreting
any prediction.

**Why this priority**: The product's credibility depends on evidence being
visible before prediction and separated from future-looking outputs.

**Independent Test**: A tester can select each approved model and verify that
evidence, limitations, evaluation period, supported stock universe, and
historical-versus-future distinctions are visible before prediction.

**Acceptance Scenarios**:

1. **Given** an approved model has complete historical evidence, **When** the
   reviewer opens the model evidence view, **Then** the product shows historical
   performance key metrics, evaluation period, supported stock universe, known
   limitations, data-quality notes, and a statement that historical performance
   may not generalize.
2. **Given** paper-trading evidence exists for the selected model, **When** the
   reviewer inspects evidence, **Then** paper-trading evidence is shown
   separately from historical backtest evidence.
3. **Given** required evidence is present but weak, unstable, incomplete, stale,
   or data-limited,
   **When** the reviewer inspects evidence, **Then** the product visibly
   explains that limitation rather than hiding it.
4. **Given** historical evidence is shown for a model, **When** the reviewer
   inspects the evidence, **Then** the product identifies the evaluation period,
   relevant data-as-of assumptions, and any material data-quality or bias risks
   that affect interpretation.
5. **Given** the reviewer is on the main prediction screen, **When** evidence
   and methodology are available, **Then** the product shows a concise evidence
   summary in the primary journey and keeps detailed methodology available as
   secondary content.

---

### User Story 3 - Handle Unsupported or Unavailable Prediction States (Priority: P3)

A user encounters unavailable models, unsupported stocks, missing evidence,
missing required data, stale data, or failed prediction generation and receives
clear guidance without receiving an invalid prediction.

**Why this priority**: Blocking invalid or unsupported predictions protects the
educational framing, model curation, chronological integrity, and user trust.

**Independent Test**: A tester can attempt each invalid request type and verify
that the product blocks prediction, explains the reason in plain language, and
offers an appropriate next step when one exists.

**Acceptance Scenarios**:

1. **Given** no approved model is available, **When** the user opens the
   prediction flow, **Then** the product explains that prediction is unavailable
   and does not display experimental, deprecated, hidden, or unapproved models.
2. **Given** the user searches for or enters a stock outside the selected
   model's supported universe, **When** the stock appears in the selection flow,
   **Then** the product marks it unavailable, explains that it is unsupported
   for that model, records aggregate non-personal interest for future support
   planning, and blocks prediction until the stock is removed or replaced.
3. **Given** required data is missing or stale for a selected stock, **When**
   the user requests a prediction, **Then** the product blocks or withholds the
   prediction and explains the data availability issue.
4. **Given** prediction generation fails or returns an empty or invalid response,
   **When** the user requests a prediction, **Then** the product shows a clear
   error and does not display a partial result as a valid prediction.
5. **Given** market-data quality or bias risks make a selected stock prediction
   unreliable, **When** the user requests a prediction, **Then** the product
   either blocks the prediction with a clear explanation or displays the result
   with a visible limitation explaining the risk.
6. **Given** historical evidence or prediction inputs would require information
   unavailable at the relevant prediction time, **When** the user or reviewer
   reaches that output, **Then** the product withholds the affected prediction
   or evidence and explains the chronology issue.

---

### User Story 4 - Access a Public Portfolio Demo (Priority: P4)

A recruiter, academic reviewer, or portfolio reviewer opens a public product URL
and completes the core Nusantara Alpha flow without running code locally.

**Why this priority**: Public demo access makes the product reviewable as a
portfolio artifact while preserving the same educational, uncertainty, and data
governance boundaries as the local product.

**Independent Test**: A tester can open the public demo URL, select an approved
model, inspect evidence, choose a supported stock, request a prediction, and
verify that the output includes disclaimer, timestamps, limitations, and demo
data context without exposing restricted data.

**Acceptance Scenarios**:

1. **Given** the public demo is available, **When** a reviewer opens its URL,
   **Then** the reviewer can use the core journey without installing software or
   running code locally.
2. **Given** the deployed demo uses a real approved model and approved
   non-sensitive data, **When** evidence or predictions are shown, **Then** the
   product clearly explains the data-as-of timestamp and demo limitations.
3. **Given** the product is deployed for portfolio review, **When** any model,
   evidence, stock, prediction, or error state is displayed, **Then** the same
   educational/research disclaimer and no-financial-advice boundary remain
   visible.
4. **Given** restricted data, credentials, private files, or unrestricted
   internal artifacts are unavailable for public release, **When** the public
   demo is prepared, **Then** the demo uses a real approved model with public,
   delayed, static, or otherwise approved non-sensitive data and no mock/demo
   model or dummy prediction output.

### Edge Cases

- No model is selected when the user attempts to request a prediction.
- No stock is selected when the user attempts to request a prediction.
- The selected model becomes unavailable after the user has reviewed evidence.
- The selected model is hidden, deprecated, experimental, or unapproved.
- A user searches for or enters an IDX stock that is not supported by the
  selected model.
- The selected stock is unsupported by the selected model's stock universe.
- A stock appears supported but required recent data is missing, stale, or
  outside the model's accepted data freshness window.
- Model evidence is missing, incomplete, stale, unstable, or data-limited.
- Historical backtest evidence and paper-trading evidence conflict or cover
  different periods.
- Market data has gaps, stale prices, trading halts, corporate actions,
  delistings, illiquidity, ticker identity changes, or exchange-calendar
  mismatches relevant to the selected stock.
- Prediction generation fails, times out from the user's perspective, returns no
  predictions, or returns a response missing required fields.
- Multiple selected stocks produce mixed results, with some successful
  predictions and some blocked outputs.
- User-facing wording accidentally resembles financial advice or direct trading
  instruction.
- A simulated paper-trading or prediction flow could be mistaken for
  real-money trading execution.
- A reviewer opens the public demo URL while data, evidence, or prediction
  generation is unavailable.
- A public demo has no real approved model available for prediction.
- A public demo uses delayed, static, or otherwise limited approved data instead
  of live data.
- A mock/demo model or dummy prediction output is accidentally exposed through
  the public demo.
- Public demo content is misconfigured to reference a private dataset,
  credential, proprietary file, or unrestricted internal artifact.
- Public demo limitations or data-as-of timestamps are missing from evidence or
  prediction views.
- Prediction output is buried below dense evidence or methodology text.
- Primary action labels sound awkward, academic, or unlike a customer-facing
  product.
- Limitation text appears as raw metadata, isolated cells, or confusing tags.
- The main screen overwhelms non-expert users with traceability or methodology
  details before they understand the prediction.
- Users mistake a dense evidence panel for the prediction itself.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST display clear educational research framing before
  or during the prediction flow.
- **FR-002**: The product MUST NOT present predictions, evidence, or simulated
  results as financial advice, buy/sell recommendations, guaranteed returns,
  personalized investment guidance, position sizing advice, or portfolio
  allocation advice.
- **FR-003**: The product MUST avoid user-facing wording such as "you should
  buy", "you should sell", "safe trade", "guaranteed profit", "recommended
  position size", and "optimal allocation".
- **FR-004**: The product MUST use careful wording such as "model signal",
  "predicted direction", "confidence", "historical evidence", "limitations",
  and "uncertainty" where prediction output is described.
- **FR-005**: The product MUST NOT place real trades, route orders, connect to
  brokerage execution, automate real-money decisions, or imply that simulated
  outputs are executable trades.
- **FR-006**: Users MUST be able to select only from approved curated prediction
  models in the main customer-facing prediction flow.
- **FR-007**: A model MUST qualify for customer-facing approval only when it has
  display approval, historical evidence, evaluation period, supported universe,
  known limitations, and traceability metadata.
- **FR-008**: Each selectable curated model MUST show a readable name, short
  description, evaluation period, supported stock universe, and display status.
- **FR-009**: Experimental, deprecated, hidden, unavailable, or unapproved models
  MUST NOT appear in the main customer-facing prediction flow.
- **FR-010**: If no approved model is available, the product MUST explain that
  prediction is unavailable and MUST NOT expose unapproved models as a fallback.
- **FR-011**: Users MUST be able to inspect selected model evidence before
  requesting predictions.
- **FR-012**: Model evidence shown before prediction MUST include an evidence
  summary with key metrics, evaluation period, supported stock universe, known
  limitations, data-quality notes, and a caveat that historical performance may
  not generalize.
- **FR-013**: When paper-trading evidence exists, the product MUST show it
  separately from historical backtest evidence.
- **FR-014**: The product MUST clearly distinguish historical evidence from
  future prediction.
- **FR-015**: The product MUST state that historical performance may not
  generalize to future market sessions.
- **FR-016**: Weak, unstable, missing, incomplete, stale, or data-limited
  evidence MUST be shown honestly rather than hidden.
- **FR-017**: Model evidence and prediction availability MUST identify material
  market-data quality or bias risks relevant to the selected model or stock.
- **FR-018**: When required evidence is present but weak, unstable, incomplete,
  stale, or data-limited, the product MAY allow prediction only with prominent
  limitations visible before and with the prediction output.
- **FR-019**: When required evidence is missing, the product MUST block model
  approval or prediction and explain that required evidence is unavailable.
- **FR-020**: Users MUST be able to select one or more supported IDX stocks for
  the selected model.
- **FR-021**: Users MUST be able to search for or enter IDX stocks even when
  some stocks are unsupported by the selected model.
- **FR-022**: Unsupported stocks MUST be shown as unavailable with a clear reason
  before prediction is requested.
- **FR-023**: Prediction MUST be blocked until unsupported stocks are removed or
  replaced with supported stocks.
- **FR-024**: The product MUST track aggregate, non-personal interest in
  unsupported stocks for future support planning without treating searches as
  investment intent or financial advice.
- **FR-025**: The product MUST explain when a stock is unavailable because it is
  outside the selected model's supported universe.
- **FR-026**: The product MUST explain when prediction is unavailable because
  required data is missing or stale.
- **FR-027**: Users MUST be able to request a next-market-session prediction only
  after selecting an approved model and at least one supported IDX stock.
- **FR-028**: Each prediction request MUST be tied to the selected model and the
  selected stock or stocks.
- **FR-029**: The product MUST validate model status, stock support, data
  availability, chronological validity, and required evidence before returning
  any prediction.
- **FR-030**: The product MUST NOT generate or display a prediction when the
  selected model is unavailable, unsupported, hidden, deprecated, experimental,
  or unapproved for display.
- **FR-031**: For each selected stock with a valid prediction, the output MUST
  include selected stock ticker, prediction target, predicted direction or model
  signal, Low/Medium/High confidence category, plain-language confidence
  explanation, short context summary, key limitation summary, selected model
  name, selected model identifier or version, data-as-of timestamp, prediction
  timestamp, evaluation context, evidence reference, and educational research
  disclaimer.
- **FR-032**: Confidence MUST be explained as model uncertainty and not as a
  guarantee of correctness.
- **FR-033**: The product MUST clearly state that model confidence can be wrong.
- **FR-034**: The product MUST explain uncertainty in plain language suitable for
  non-expert users before any optional numeric confidence score is shown.
- **FR-035**: The product MUST avoid overstating precision when evidence is
  limited.
- **FR-036**: Error messages MUST be understandable to non-expert users and MUST
  explain what the user can do next when a practical next step exists.
- **FR-037**: The product MUST handle no model selected, no stock selected,
  unsupported stock, unavailable model, missing model evidence, missing required
  data, stale data, failed prediction generation, empty prediction response, and
  invalid prediction response.
- **FR-038**: Every prediction output MUST be traceable to a specific model
  identifier or version.
- **FR-039**: Every prediction output MUST include timestamp information that
  lets users and reviewers understand when input data and prediction output were
  generated.
- **FR-040**: The product MUST make it possible to review which model and which
  evidence produced a prediction.
- **FR-041**: Historical evidence and prediction outputs MUST be withheld or
  clearly marked unavailable when they depend on information unavailable at the
  relevant prediction timestamp.
- **FR-042**: Market-data quality or bias risks MUST be disclosed when they
  materially affect interpretation and MUST block prediction when they make the
  output unreliable or untraceable.
- **FR-043**: The product MUST NOT expose secrets, credentials, private datasets,
  proprietary data, or restricted source data in customer-facing screens,
  examples, downloadable outputs, or demonstration content.
- **FR-044**: Demonstration data and evidence MUST be described as permitted
  sample, mock, public, delayed, static, or otherwise approved data when shown
  to users or reviewers, and public-demo content MUST distinguish approved data
  from local-only sample/mock experimentation.
- **FR-045**: The main customer-facing journey MUST remain: choose model,
  inspect evidence, choose stock, request prediction, understand risk.
- **FR-046**: Technical details MAY appear in expandable sections, but the main
  journey MUST remain understandable without advanced machine learning
  knowledge.
- **FR-047**: Prediction responses MUST be consistent and structured across all
  selected stocks.
- **FR-048**: The product MUST remain usable for demonstration when some data,
  model evidence, or predictions are unavailable by showing clear unavailable
  states instead of broken or misleading outputs.
- **FR-049**: The product MUST prioritize clarity, honesty, and interpretability
  over decorative or flashy presentation.
- **FR-050**: The product MUST avoid hidden assumptions and inflated claims about
  model performance or ability to beat the market.
- **FR-051**: The product SHOULD be deployable to a public server for portfolio
  and academic review.
- **FR-052**: Reviewers SHOULD be able to open a URL and use the product without
  running code locally.
- **FR-053**: The public demo MUST support the core user flow: choose model,
  inspect evidence, choose stock, request prediction, and understand risk.
- **FR-054**: The public demo MUST preserve educational/research disclaimers and
  MUST NOT frame predictions as financial advice, buy/sell guidance, guaranteed
  profit, personalized guidance, position sizing advice, or allocation advice.
- **FR-055**: The public demo MUST use real approved models for prediction and
  MUST NOT expose mock models, demo-only models, experimental models, or dummy
  prediction outputs.
- **FR-056**: The public demo MUST NOT expose secrets, credentials, private
  datasets, proprietary files, restricted source data, or unrestricted internal
  artifacts.
- **FR-057**: The public demo MAY use public, delayed, static, or otherwise
  approved non-sensitive data with a real approved model, but MUST clearly
  explain the relevant data-as-of timestamp and demo limitations.
- **FR-058**: The system SHOULD be designed so the public demo can run in a
  low-cost or free server environment when feasible.
- **FR-059**: If the public demo cannot complete evidence retrieval, stock
  availability checks, or prediction generation, it MUST show a clear
  unavailable state instead of a broken or misleading output.
- **FR-060**: If no real approved model is available for the public demo, the
  public demo MUST block prediction and explain that public prediction is
  unavailable rather than falling back to mock or dummy outputs.
- **FR-061**: Once a valid approved model and supported ticker are selected and
  required evidence and data are available, the prediction output MUST become
  the primary visible content in the main experience.
- **FR-062**: The primary prediction view MUST prominently show selected ticker,
  model signal or predicted direction, confidence category, key context, and
  key limitations before secondary technical details.
- **FR-063**: The product MUST NOT require users to read dense evidence,
  methodology, or traceability text before they can understand the main
  prediction output.
- **FR-064**: The product MUST provide a concise evidence summary before or
  alongside prediction interpretation while keeping detailed evidence,
  methodology, and traceability in secondary or expandable sections.
- **FR-065**: If a manual prediction action is used, the action label MUST use
  plain customer-facing language such as "Predict" and MUST NOT use awkward
  academic wording such as "Request educational prediction".
- **FR-066**: When a valid model and supported ticker are selected, the product
  SHOULD show the prediction automatically or with only a lightweight user
  action, provided all evidence, data, chronology, and model approval gates pass.
- **FR-067**: User-facing labels, warnings, limitations, and evidence summaries
  MUST be written in plain, natural product language for non-expert users.
- **FR-068**: The product MUST avoid presenting limitations as raw metadata,
  isolated cell-like text, unexplained tags, or debug-style labels.
- **FR-069**: Limitation copy MUST explain the practical meaning of constraints
  in calm, readable language rather than using awkward fragments such as
  "limited universe" as standalone UI text.
- **FR-070**: The main prediction screen MUST group information into clear
  user-facing sections: prediction, confidence, why this signal appeared, key
  limitations, model evidence, and traceability details.
- **FR-071**: Technical details and traceability MUST remain available for
  reviewers, but they MUST be visually secondary to the main prediction,
  confidence, context, and limitation summary.
- **FR-072**: The main flow MUST feel like a customer-facing product experience
  and MUST NOT feel like filling out an internal ML form or reading an
  experiment tracker.
- **FR-073**: The product MUST preserve no-financial-advice framing without
  making the primary experience sound overly academic or unnatural.

### Scope Boundaries

- Public portfolio-demo access is in scope.
- Real-money trading execution is out of scope.
- Brokerage integration is out of scope.
- Automatic order placement is out of scope.
- Personalized financial advice is out of scope.
- Portfolio allocation advice is out of scope.
- Position sizing advice is out of scope.
- Guaranteed return claims are out of scope.
- Live trading system behavior is out of scope.
- Paid customer deployment is out of scope.
- High-availability production infrastructure is out of scope.
- Claims that the model can consistently beat the market are out of scope.

### Key Entities *(include if feature involves data)*

- **Curated Prediction Model**: An approved customer-facing model with display
  approval, readable name, identifier or version, description, historical
  evidence, evaluation period, supported stock universe, display status, known
  limitations, and traceability metadata.
- **Model Evidence**: Historical context for a curated model, including
  performance summary, key metrics, evaluation period, supported universe,
  methodology context, limitations, data-quality notes, historical-performance
  caveat, and optional paper-trading evidence.
- **Supported IDX Stock**: An Indonesian stock market security that is available
  for prediction under the selected model's supported universe.
- **Unsupported Stock Interest Signal**: Aggregate, non-personal evidence that
  users searched for or entered an unsupported IDX stock, used only for future
  support planning.
- **Prediction Request**: A user-initiated request tied to one selected curated
  model and one or more supported IDX stocks for the next market session.
- **Prediction Output**: A structured result for a selected stock containing
  signal, Low/Medium/High confidence category, plain-language confidence
  explanation, context, limitations, model identity, evidence reference,
  evaluation context, timestamps, and disclaimer.
- **Prediction View**: The main user-facing presentation of a prediction,
  organized around ticker, model signal, confidence, context, limitations,
  concise evidence summary, and secondary traceability details.
- **Data Availability State**: The freshness, completeness, and usability status
  of required data for a selected model and stock.
- **Educational Disclaimer**: Required user-facing language that frames the
  product as educational research and not financial advice or trade execution.
- **Public Demo Access**: A reviewable product instance reachable through a URL
  that supports the core journey without local setup.
- **Demo Data Source**: The public, delayed, static, or otherwise approved
  non-sensitive data used by the public demo with a real approved model,
  including data-as-of timestamp and limitations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90% of representative users can complete the main journey
  with one approved model and one supported IDX stock in under 3 minutes without
  assistance.
- **SC-002**: 100% of valid prediction outputs include signal, Low/Medium/High
  confidence category, plain-language confidence explanation, context,
  limitations, selected stock ticker, model name, model identifier or version,
  data-as-of timestamp, prediction timestamp, evaluation context, evidence
  reference, and educational disclaimer.
- **SC-003**: 100% of tested unsupported models, hidden models, deprecated
  models, experimental models, and unapproved models are blocked from the main
  customer-facing prediction flow.
- **SC-004**: 100% of tested unsupported stocks and stale-data cases prevent a
  misleading prediction and show a clear explanation.
- **SC-005**: 0 tested primary-flow screens or prediction outputs contain
  forbidden advice phrases such as "you should buy", "you should sell",
  "guaranteed profit", "recommended position size", or "optimal allocation".
- **SC-006**: At least 90% of representative users correctly identify that the
  prediction is exploratory educational research and not financial advice after
  completing the flow.
- **SC-007**: 100% of model evidence views show key metrics, evaluation period,
  historical performance context, supported stock universe, known limitations,
  data-quality notes, and a statement that historical performance may not
  generalize.
- **SC-008**: 100% of prediction outputs can be traced by a reviewer to the
  selected model identifier or version, selected ticker, data-as-of timestamp,
  prediction timestamp, evaluation context, and relevant evidence context.
- **SC-009**: In reviewer evaluation, at least 4 out of 5 reviewers rate the
  product as a clean customer-facing experience rather than an internal
  experiment tracker.
- **SC-010**: 100% of tested empty, failed, or invalid prediction responses show
  a clear error state and do not display a partial result as a valid prediction.
- **SC-011**: 100% of tested chronology violations withhold the affected
  prediction or evidence and explain that unavailable future information cannot
  be used.
- **SC-012**: 100% of tested material market-data quality or bias risks are
  visibly disclosed, and risks that would make an output unreliable or
  untraceable block the affected prediction.
- **SC-013**: 0 tested customer-facing screens, examples, downloadable outputs,
  or demonstration content expose secrets, credentials, private datasets,
  proprietary data, or restricted source data.
- **SC-014**: At least 90% of representative users correctly identify that a
  Low/Medium/High confidence category can be wrong and that limited evidence
  reduces prediction reliability.
- **SC-015**: 100% of tested unsupported-stock searches or entries show an
  unavailable reason, block prediction until removed or replaced, and are
  included in aggregate non-personal support-interest reporting.
- **SC-016**: A reviewer can open the public demo URL and complete the core
  journey with a real approved model and supported IDX stock without running
  code locally.
- **SC-017**: 100% of tested public-demo model, evidence, stock, prediction, and
  error states preserve the educational/research disclaimer and avoid
  financial-advice framing.
- **SC-018**: 0 tested public-demo screens, responses, examples, downloadable
  outputs, or logs expose secrets, credentials, private datasets, proprietary
  files, restricted source data, or unrestricted internal artifacts.
- **SC-019**: 100% of tested public-demo evidence and prediction views using
  public, delayed, static, or otherwise limited approved data show a data-as-of
  timestamp and demo limitation explanation.
- **SC-020**: 0 tested public-demo model selectors, evidence views, prediction
  outputs, or error states expose mock models, demo-only models, experimental
  models, or dummy prediction outputs as public predictions.
- **SC-021**: At least 90% of representative non-expert users can identify the
  selected ticker, model signal, confidence category, and key limitation within
  10 seconds of selecting a supported ticker.
- **SC-022**: At least 4 out of 5 reviewers describe the main experience as
  clear, polished, and customer-facing rather than internal, text-heavy, or
  experiment-like.
- **SC-023**: 100% of tested primary prediction screens show the prediction
  before dense methodology, raw traceability details, or extended evidence
  content.
- **SC-024**: 0 tested primary action labels use awkward academic wording such
  as "Request educational prediction".
- **SC-025**: 100% of tested limitation displays use readable explanatory copy
  rather than raw metadata, isolated cells, or unexplained tag-style fragments.
- **SC-026**: At least 90% of representative users can correctly explain, after
  viewing the main prediction screen, that the model signal is educational and
  uncertain while still understanding the prediction itself.

## Assumptions

- The initial product is an educational, customer-facing demonstration and does
  not require user accounts or personalized portfolios.
- The supported stock universe is determined by each curated model's evidence
  and metadata.
- Predictions target the next IDX market session after the relevant data-as-of
  timestamp.
- Historical evidence, model status, supported universe, and prediction results
  are available to the product as curated content or generated artifacts.
- If required evidence or required data is unavailable, the correct behavior is
  to block or withhold prediction rather than infer missing evidence.
- If required evidence is present but weak or data-limited, the correct behavior
  is to show prominent limitations before and with prediction output.
- Unsupported-stock interest is tracked only in aggregate for future support
  planning and does not represent user investment intent.
- The first release prioritizes clarity and reliability over broad model count,
  broad stock coverage, or advanced customization.
- The next MVP iteration prioritizes prediction-first UX, plain product
  language, readability, and customer-facing polish over adding new model
  capability.
- A concise evidence summary can satisfy evidence-before-prediction for the
  main journey when detailed evidence and traceability remain available before
  or alongside interpretation.
- The public demo uses real approved models only; mock/demo models and dummy
  prediction outputs are limited to local development or experimentation.
- The public demo may use public, delayed, static, or otherwise approved
  non-sensitive data with a real approved model if live or current data cannot
  be deployed safely.
- Public demo access is intended for portfolio, recruiter, and academic review,
  not paid production use.
- The public demo should run in a low-cost or free server environment when
  feasible, but high availability and production operations are not required for
  this feature.
