# The inquiry

Why this instrument exists for the person building it, and what the work is
pointed at. The charter says what the instrument does. This file says what it is
*for*. When the two pull in different directions, this file wins on direction and
the charter wins on how the instrument is built.

Kept by Jared, written down with Claude on 2026-10-07. He is applying to MFA
programs in spring 2027, and this repo is meant to hold the beginning of a
creative inquiry he wants to carry through one. Every session that adds work here
should be able to say how it serves the question below, or say plainly that it
does not.

## The question

**What does colour become when an instrument that cannot see it is in the room?**

A spectrometer measures light honestly: how much energy arrives at each
wavelength. That is a physical quantity. Colour, the experience, is not that
quantity. It is that light passed through a particular eye, a brain that corrects
for the light source, the memory of what things are supposed to look like, and a
body that has been awake for sixteen hours. The two come apart, and they come
apart in ways that can be staged.

Jared, 2026-09-22, the remark the whole lane starts from:

> "It doesn't really mean anything if we aren't creating color experiences ... in
> the way that Albers has his color studies manifested in objects. We need to do
> something similar ... in the world of James Turrell and his Ganzfelds ... if
> it's going to be a meaningful continuation of light and space art in our
> particular lane."

And the part that makes it more than a sensor project: colour analysis without
"body, subjectivity, sense experience, illusion and memory" is a limited
experience of colour, and it is the only kind an AI has. The work stages the
colour that exists only in a body, next to the instrument that cannot have it.

## Where it sits in the lineage

The Light and Space artists (Turrell, Irwin, Wheeler, Bell, Corse) made
perception itself the medium. Research on 2026-09-22 found a gap in that lineage:

- Spencer Finch is the nearest. He measures a specific light once, with a
  colorimeter, then rebuilds it with filtered lamps. The instrument is never in
  the room, and a colorimeter cannot tell two different lights apart if they
  happen to look alike.
- Turrell fixes the optics once and lets the body do everything else. No sensor.
- Irwin: a fixed mechanism and a moving viewer.
- Lozano-Hemmer runs live sensor loops, but senses heat and presence, not
  spectrum.

Nobody puts live spectral measurement, light re-emitted to match it, and the gap
between the instrument and the eye in the same room, running, at the same time.
That is the open lane.

## The move that makes it possible

The head's LED ring is eight separately dimmable colours on a twelve-channel
driver. Pointed at a swatch, it is a light source for measuring. Pointed at a
space, it is a lamp that can hold a measured light. So spectra becomes a pair:
the head that measures and the lamp that answers it. The lamp needs no new
purchase, and in the charter's terms it is a model over the store. It reads
stored curves and plays them back. Nothing about it goes into the core
measurement table.

## The pieces

Proposed by Claude on 2026-09-22 ("mine to propose and yours to refuse"), in
build order. None is built.

1. **Moonlight, Held.** Build first. A small, enclosed, white-walled viewing
   chamber, about the size of a head, lit by the lamp holding one warm, measured
   light. The light slowly dims. In dim light the eye switches to the receptors
   that favour blue-green (the Purkinje shift, the reason moonlight looks blue
   even though it is warm reflected sunlight). The chamber turns blue to anyone
   inside it. The live trace beside it does not move. *Why a chamber and not a
   room:* the LEDs are single 5 mm parts and cannot light a room, and a chamber
   controls how long the eye has been in the dark, which a gallery cannot. That
   reasoning is inferred, not yet tested.
2. **The Room's Yellow.** Each person in a class turns a dial until the lamp
   looks pure yellow, with no red or green in it, and the setting is logged with
   the measured light. The wall shows the spread: twenty-five yellows, each one
   somebody's certainty. Same lamp, no new hardware. Turns the teaching into the
   work.
3. **Two Curves, One Colour.** Two paints mixed to look identical, one from the
   earth pigments and one from the bright modern ones. They are made of different
   light, so when the lamp changes they split apart. This is the bridge to the
   paint side of the repo: the six pigments the Stage 1d test already needs.
   Needs the Hamamatsu spectrometer to prove the match.
4. **The Live Window.** The instrument watches the sky through a window and the
   lamp inside re-creates it continuously. The wall shows both curves and the
   difference the eight LEDs cannot close. The piece nobody has made. Needs the
   Hamamatsu.
5. **Mondrian, Re-run.** Edwin Land's 1971 colour-constancy experiment as a
   one-hour student exercise. Teaching, not exhibition.

1 and 2 can be made with parts on the bench. 3 and 4 belong in an MFA proposal as
where the work goes next, not as work already done.

## What counts as progress

The inquiry advances when one of these happens. Instrument work that serves none
of them is still allowed, but it is not this lane, and a session doing it should
say so.

- **A light someone has stood in.** A built thing, shown, with what people said.
- **A studio log entry.** `process/STUDIO_LOG.md`: what was seen, what the
  instrument said, what changed. The gap between them is the evidence.
- **A participant result.** A class's yellows, a room's agreement or
  disagreement, logged with the measured light.
- **A sharper question.** A finding that changes what the next piece should be.

Before an MFA application, the record should show the gap, not the gadget: dated
entries, traces beside notes, people in the loop.

## What this lane is not

- **Not a data visualisation.** None of the pieces names a colour or charts one
  for its own sake. The instrument is on the wall because it is honest, not
  because it is pretty.
- **Not the paint maths as headline.** Kubelka-Munk (predicting what two paints
  look like mixed) is the craft underneath and the bridge to piece 3. It is not
  what the inquiry is about.
- **Not a reason to bend the core.** The measurement layer stays general. Lamp
  code reads the store and never adds a column to it.

## Open

- **The Hamamatsu C12880MA.** Claude recommended buying it once the first eight
  channels light. Jared has not ruled. Pieces 3 and 4 wait on it.
- **The ESP32 has not lit an LED yet.** Nothing in piece 1 can start until it
  does.
- **The colour library has not been read for this.** The Drive library behind
  `docs/PRIOR_ART.md` was read for measurement and mixing only. Its perception
  texts have not been read against this question.

## Sources

- "What the Curve Leaves Out", 2026-09-22:
  https://notes.aaand.space/spectra-color-experience.html. The full research,
  lineage and the five pieces.
- "The Twelve Senses", 2026-08-30, notes.aaand.space: an earlier seed, "a lamp
  that remembers daylight", written before this repo existed.
- Josef Albers, *Interaction of Color*: "All color perception is really
  illusional." In Jared's Drive.
