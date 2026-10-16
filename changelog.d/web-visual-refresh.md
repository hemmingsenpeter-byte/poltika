- The web app has a new look at Pete's request (decision log D47): a bush-green
  frame, kōwhai yellow only for "you are here" and "take note", a cool paper
  ground, Source Serif 4 for titles and headline figures, Source Sans 3 for
  the interface at a 16px base, and no shadow under resting surfaces. Every
  text pair stays at WCAG AA. The header now reads "Poltika" and "Pilot on a
  synthetic population"; no other copy, contract, endpoint or calculated
  amount changed.
- The home page is now the Poltika logo above the search field, at Pete's
  instruction (decision log D48). The heading and the "What Poltika does"
  copy are removed. The search note, start actions and classic-calculator
  link sit under an "Advanced" disclosure. The placeholder now reads "Search
  a policy setting, such as the Family Tax Credit" so it does not suggest
  that the search reads questions.
- A Settings page (`/settings`, under Data in the sidebar) now holds the
  policy versions, their status, the population and this deployment's
  Poltika, API and build versions, at Pete's instruction (decision log D49).
  The policy versions are gone from the header. FastAPI declares the new UI
  route.
