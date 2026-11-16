# Truthful post-action feedback

The Arcade target-confirmation flow previously sent `target.health <= 0` as
`suppression_created`, so killing a hostile announced suppression. It now passes
the engine's `defeated_target` result to a separate `HOSTILE DOWN` token. The
suppression field remains available only for callers reporting that actual
effect. No suppression or damage rule changes.

Critical-hit feedback reads the current `AttackResolution.critical` rather than
an actor's mutable last-crit flag. HIT/MISS comes from the resolved hit flag,
including the edge case of a hit that deals zero damage. An ordinary miss can
mention that the target was in cover without claiming that a specific cover
object blocked the shot; genuinely blocked attacks are rejected by the engine.

The aftermath builder now distinguishes absent damage (`None`) from explicit
zero damage. Movement/first aid/stance-like nonattack updates omit `DMG 0`;
actual missed attacks can still show zero. Existing skill-check callers that
explicitly provide zero keep their old output. Treatment retains its patient-
specific recovery message.

Tests check move/aid/kill/suppression output and the real-engine kill's view
aftermath during battle-to-campaign integration. The full suite passed **808
tests and eight subtests**; after the final zero-damage/miss wording correction,
all ten focused flow/aftermath tests passed. This is rule/text integration
evidence, not a rendered GPU/audio playthrough. No window or desktop control
was used. The distributed R2 archive predates this change.
