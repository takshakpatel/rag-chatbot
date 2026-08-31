"use client";

export interface ReadoutValues {
  state: string;
  sourcesHit: number;
  candidates: number;
  latencyMs: number;
}

const STATE_DOT: Record<string, string> = {
  SURFACE: "bg-ink-dim",
  DESCENT: "bg-thermo",
  HOLD: "bg-hold",
  VERIFIED: "bg-verified",
  TURN: "bg-refusal",
  ASCENT: "bg-hold",
};

export default function Readouts({ values }: { values: ReadoutValues }) {
  const state = values.state || "SURFACE";
  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      <Cell
        label="State"
        dot={STATE_DOT[state] ?? "bg-ink-dim"}
        value={state}
      />
      <Cell label="Sources hit" value={String(values.sourcesHit).padStart(2, "0")} />
      <Cell label="Candidates" value={String(values.candidates).padStart(3, "0")} />
      <Cell label="Latency" value={`${Math.round(values.latencyMs)}ms`} />
    </div>
  );
}

function Cell({
  label,
  value,
  dot,
}: {
  label: string;
  value: string;
  dot?: string;
}) {
  return (
    <div className="glass-tile rounded-xl px-3.5 py-2.5">
      <div className="flex items-center gap-1.5">
        {dot && <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />}
        <div className="digits text-[9px] uppercase tracking-[0.14em] text-ink-faint">
          {label}
        </div>
      </div>
      <div className="digits mt-1 text-lg font-semibold leading-none tabular-nums text-ink">
        <span className="digit-snap inline-block" key={value}>
          {value}
        </span>
      </div>
    </div>
  );
}
