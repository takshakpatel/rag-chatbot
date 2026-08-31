export default function ContractComment() {
  const contract = `THIS IS THE DEEP-DIVE DEPTH PROFILE (seed d6159bf5).
THESIS: The RAG answer is a measured reading pinned to a vertical corpus-depth axis. It refuses the arrangement of a chat that just answers: every claim carries a depth, a state, and a source that verifies it.
OWN-WORLD: abyssal ink-blue-black ground deepening by depth zone; thermocline cyan marks the active retrieval depth; warmth drains with depth (surface pinks only at the shallows); every measurement is tabular dive-computer digits; one vertical depth ruler rules the composition.
STORY: A developer asks at the surface, watches descent retrieve and verify sources, and reads an answer whose every citation is a depth-pin they can pull to the exact source slice. Refusal reads as an honest turnaround, not a dead end.
FIRST VIEWPORT: left spine = vertical depth ruler over the corpus; center = the descent profile: the question at SURFACE, the answer as a RESULTS reading with inline cyan depth-pins, and a dive-computer readout (sources hit, candidates scanned, latency, state). Primary action: the ask prompt styled as the next descent.
FORM: Deep-Dive Depth Profile; user-picked competitive challenger; seed key d6159bf5.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.`;

  // Emit a real HTML comment so the contract survives the production build.
  return (
    <div
      dangerouslySetInnerHTML={{
        __html: `<!--\n${contract}\n-->`,
      }}
    />
  );
}
