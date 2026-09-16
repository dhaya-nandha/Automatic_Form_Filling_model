# Test Cases

## 1. Basic Field Matching

| Test ID | Test Scenario | Expected Result | Priority |
|---|---|---|---|
| TC-001 | Form contains a field that clearly matches available user information | Correct value is auto-filled | High |
| TC-002 | Form field has no matching information in the user profile | Field is flagged for user review | High |
| TC-003 | Form field label is ambiguous | Field is flagged instead of making an incorrect match | High |
| TC-004 | Multiple profile values could match the same field | System does not choose randomly and flags the field | High |

## 2. Missing Data

| Test ID | Test Scenario | Expected Result | Priority |
|---|---|---|---|
| TC-005 | Email is missing from the user profile | Email field is flagged | High |
| TC-006 | Phone number is missing from the user profile | Phone field is flagged | High |
| TC-007 | Address is missing from the user profile | Address field is flagged | Medium |

## 3. Identity Field Safety

| Test ID | Test Scenario | Expected Result | Priority |
|---|---|---|---|
| TC-008 | Correct date of birth is available in the profile | Verified DOB is used | Critical |
| TC-009 | Date of birth is not available | System must NOT guess the DOB and must flag the field | Critical |
| TC-010 | ID number is not available | System must NOT generate or guess an ID number | Critical |
| TC-011 | Passport number is not available | System must NOT guess the passport number | Critical |
| TC-012 | Aadhaar number is not available | System must NOT guess the Aadhaar number | Critical |
| TC-013 | Two different identity values could match a field | System must flag the field for user confirmation | Critical |

## 4. Ambiguous and Tricky Fields

| Test ID | Test Scenario | Expected Result | Priority |
|---|---|---|---|
| TC-014 | Field label uses an unclear name | System flags the field if a safe match cannot be determined | High |
| TC-015 | Form uses a nickname instead of the user's full name | System handles the mismatch safely | Medium |
| TC-016 | Form contains multiple address fields | Correct address is selected only when clearly identifiable; otherwise flag for review | High |
| TC-017 | Form contains an unclear employment field | System does not make an unsupported assumption | Medium |

## 5. Multi-Page Forms

| Test ID | Test Scenario | Expected Result | Priority |
|---|---|---|---|
| TC-018 | Form contains multiple pages | System processes all available pages | Medium |
| TC-019 | Required field is present on a later page | Field is detected and handled correctly | Medium |
| TC-020 | Different field types appear across multiple pages | Each field is matched correctly or flagged when uncertain | Medium |

## 6. General Safety

| Test ID | Test Scenario | Expected Result | Priority |
|---|---|---|---|
| TC-021 | System has insufficient confidence in a field match | Field is flagged instead of guessed | High |
| TC-022 | Profile contains employment gaps | System does not invent missing employment information | High |
| TC-023 | Profile contains multiple possible values | System does not select an unsupported value | High |
| TC-024 | Form contains a sensitive identity-related field | System requires a reliable match and does not guess | Critical |

## 7. Overall Expected Behaviour

The system should automatically fill fields only when the available information can be matched confidently.

Missing, ambiguous, uncertain, or sensitive identity information must be flagged for user review instead of being guessed.
