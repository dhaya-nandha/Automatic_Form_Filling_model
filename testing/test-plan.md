# Test Plan

## 1. Objective

The objective of testing is to verify that the Automatic Form Filling system fills form fields with the correct user information and safely handles missing, ambiguous, or sensitive information.

## 2. Auto-Fill Rules

The system should auto-fill a field when:
- The field label clearly matches available user information.
- The required information is present in the user profile.
- The value can be matched with high confidence.

## 3. User Flagging Rules

The system should flag a field for the user when:
- The required information is missing.
- The field label is ambiguous.
- Multiple possible values match the field.
- The information is sensitive and cannot be matched with sufficient confidence.

## 4. Edge Cases

Test the system with:
- Ambiguous field labels
- Missing data
- Multiple addresses
- Nicknames
- Employment gaps
- Multi-page forms
- Different types of forms
- Tricky or unclear field labels

## 5. Identity Field Safety

The system must NEVER guess:
- ID numbers
- Date of birth
- Passport numbers
- Aadhaar numbers
- Other identity-related fields

If the correct value cannot be determined with sufficient confidence, the system must flag the field for the user instead of guessing.

## 6. Expected Result

Correct and confidently matched fields should be auto-filled.

Uncertain, missing, ambiguous, or sensitive information that cannot be safely matched should be flagged for user review.

## 7. Priority

High priority:
- Identity field safety
- Field matching accuracy
- Incorrect data prevention
- Missing-data handling

Medium priority:
- Multi-page forms
- Ambiguous labels
- Multiple addresses

Low priority:
- General UI and formatting issues
