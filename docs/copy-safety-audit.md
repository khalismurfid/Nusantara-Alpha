# Copy Safety Audit

Date: 2026-05-29

Scope reviewed:

- `app_streamlit/`
- `backend/`
- `docs/`
- `tests/`

Result:

- Runtime disclaimer text frames the product as educational research and not
  financial advice.
- Prediction output copy uses model signal, confidence, context, uncertainty,
  limitations, and traceability language.
- Forbidden advice phrases are centralized in
  `app_streamlit/copy/disclaimers.py` for testing and audit purposes.
- Static search found the forbidden phrases only in the centralized test/audit
  list, not as product recommendation copy.
- The code avoids presenting prediction outputs as instructions, guaranteed
  outcomes, position sizing, allocation advice, or personalized guidance.
- MVP UX wording audit found `Request educational prediction`, `Limited
  universe`, and `No guarantee...` only in guard lists, tests, or validation
  instructions that reject those phrases. Runtime seed copy and Streamlit
  service copy now use plain guidance such as reviewed tickers, model evidence,
  and future market sessions may differ.
- Primary action copy is automatic where possible; the accepted fallback label
  is `Predict`.

Residual risk:

- Future UI copy changes must continue using the centralized disclaimer and
  forbidden-phrase tests.
- Future limitation copy should avoid raw metadata fragments and pass
  `assert_limitation_copy_readable`.
