# Studio log

What was seen, newest last. `BENCH_LOG.md` records whether the instrument works.
This file records what happens when someone looks: the evidence for the inquiry in
`docs/INQUIRY.md`.

An entry is worth writing whenever the eye and the instrument were in the same
place: a session in the chamber, a class run, a test light that looked wrong. Keep
the two columns apart. What you saw is not corrected by what the trace said, and
the trace is not corrected by what you saw. The gap is the point.

```
## YYYY-MM-DD — piece or test
Commit: <sha, or "none" if nothing ran>
Setup: what was lit, how dark the room was, how long you'd been in it
Saw: in your own words, before looking at the trace
Instrument said: the reading, or a photo of the trace
Who else: anyone else who looked, and what they said
Next: what this changes
```

Photos and traces go in `process/studio/YYYY-MM-DD/`, named in the entry.

## Owed before the first entry

- The ESP32 lighting channel 0 (`BENCH_LOG.md`).
- A diffuser and a small white-walled enclosure for Moonlight, Held.
