- Income tax engine (Task 7, new-policy PR 3), non-numeric contract only:
  `engines/simulator/income_tax.py` reads #219's draft packet read-only.
  A draft policy is never loaded (`IT_POLICY_NOT_APPROVED`), an unapproved
  band parameter gates the result (`IT_PARAMETER_NOT_APPROVED`), and
  DEC-004's open output method gates it too, so no result is `calculated`,
  including a known zero. Every result from a parameter set carries policy
  identity and its parameter and assertion uses. No calculated amount
  changes.
