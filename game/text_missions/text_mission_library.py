"""Static library of all narrative text missions — 60 total (30 city + 30 wasteland).

Each mission uses a 12-scene branching structure (Fighting Fantasy style):
  open → A_ok / A_fail / B_ok / B_fail (4 approach outcomes)
       → mid_ok / mid_fail             (2 middle-phase states)
       → crisis                        (critical moment; partial_scene routing)
       → recovery                      (setback recovery path)
       → victory / partial / defeat    (3 endings)
"""

from __future__ import annotations

from .text_mission_template import MissionScene, SceneChoice, SkillCheck, TextMissionTemplate


def _mk(
    mid: str, title: str, dtype: str, bgkey: str, desc: str, reward: int, risk: int,
    # 12 scene texts
    t_open: str,
    t_aok: str, t_afail: str,
    t_bok: str, t_bfail: str,
    t_midok: str, t_midfail: str,
    t_crisis: str, t_recovery: str,
    t_victory: str, t_partial: str, t_defeat: str,
    # choice A at open (→ a_ok on success, a_fail on failure)
    a_lbl: str, a_sk: str, a_df: int,
    # choice B at open (→ b_ok on success, b_fail on failure)
    b_lbl: str, b_sk: str, b_df: int,
    # choice inside a_ok (→ mid_ok on success, mid_fail on failure)
    a2_lbl: str, a2_sk: str, a2_df: int,
    # choice inside a_fail (→ mid_fail on success, defeat on failure)
    af_lbl: str, af_sk: str, af_df: int,
    # choice inside b_ok (→ mid_ok on success, mid_fail on failure)
    b2_lbl: str, b2_sk: str, b2_df: int,
    # choice inside b_fail (→ mid_fail on success, defeat on failure)
    bf_lbl: str, bf_sk: str, bf_df: int,
    # choice inside mid_ok (→ crisis on success, recovery on failure)
    m1_lbl: str, m1_sk: str, m1_df: int,
    # choice inside mid_fail (→ crisis on success, defeat on failure)
    m2_lbl: str, m2_sk: str, m2_df: int,
    # choice inside crisis (great/success→victory, partial→partial, failure→defeat)
    cr_lbl: str, cr_sk: str, cr_df: int,
    # choice inside recovery (→ partial on success, defeat on failure)
    rc_lbl: str, rc_sk: str, rc_df: int,
) -> TextMissionTemplate:
    return TextMissionTemplate(
        id=mid, title=title, district_type=dtype, background_key=bgkey,
        description=desc, opening_scene_id="open",
        scenes={
            "open": MissionScene("open", t_open, choices=(
                SceneChoice("ca",  a_lbl,  SkillCheck(a_sk,  a_df,  a_lbl),  "a_ok",   "a_fail"),
                SceneChoice("cb",  b_lbl,  SkillCheck(b_sk,  b_df,  b_lbl),  "b_ok",   "b_fail"),
            )),
            "a_ok":    MissionScene("a_ok",    t_aok,     choices=(
                SceneChoice("ca2", a2_lbl, SkillCheck(a2_sk, a2_df, a2_lbl), "mid_ok", "mid_fail"),
            )),
            "a_fail":  MissionScene("a_fail",  t_afail,   choices=(
                SceneChoice("caf", af_lbl, SkillCheck(af_sk, af_df, af_lbl), "mid_fail","defeat"),
            )),
            "b_ok":    MissionScene("b_ok",    t_bok,     choices=(
                SceneChoice("cb2", b2_lbl, SkillCheck(b2_sk, b2_df, b2_lbl), "mid_ok", "mid_fail"),
            )),
            "b_fail":  MissionScene("b_fail",  t_bfail,   choices=(
                SceneChoice("cbf", bf_lbl, SkillCheck(bf_sk, bf_df, bf_lbl), "mid_fail","defeat"),
            )),
            "mid_ok":  MissionScene("mid_ok",  t_midok,   choices=(
                SceneChoice("cm1", m1_lbl, SkillCheck(m1_sk, m1_df, m1_lbl), "crisis",  "recovery"),
            )),
            "mid_fail":MissionScene("mid_fail",t_midfail, choices=(
                SceneChoice("cm2", m2_lbl, SkillCheck(m2_sk, m2_df, m2_lbl), "crisis",  "defeat"),
            )),
            "crisis":  MissionScene("crisis",  t_crisis,  choices=(
                SceneChoice("ccr", cr_lbl, SkillCheck(cr_sk, cr_df, cr_lbl),
                            "victory", "defeat", partial_scene="partial"),
            )),
            "recovery":MissionScene("recovery",t_recovery,choices=(
                SceneChoice("crc", rc_lbl, SkillCheck(rc_sk, rc_df, rc_lbl), "partial", "defeat"),
            )),
            "victory": MissionScene("victory", t_victory, outcome="success",
                                    fund_delta=reward),
            "partial": MissionScene("partial", t_partial, outcome="partial",
                                    fund_delta=reward // 2, stress_delta=5),
            "defeat":  MissionScene("defeat",  t_defeat,  outcome="failure",
                                    stress_delta=15),
        },
        fund_reward=reward, risk_level=risk,
    )


# ── CITY MISSIONS ─────────────────────────────────────────────────────────────

_CITY = [

_mk("tm_c01", "Ghost in the Rain", "city", "city_01_neon_alley",
    "Extract a gang accountant before the Yakuza close the net.", 100, 2,
    # open
    "Rain hammers the neon signs of the Chrome Warrens. Somewhere in this labyrinth of bars "
    "and smoke-filled alleys, a frightened gang accountant waits with a data chip worth more "
    "than his life. Yakuza spotters are two blocks behind you and converging fast. "
    "You have minutes to make your approach before the window closes.",
    # a_ok
    "You slip through the service passage without triggering a single sensor, emerging in the "
    "kitchen alcove of a noodle bar thirty metres from the target. The accountant is in the "
    "back booth, nursing cold broth and watching the door. He startles when you slide in across "
    "from him, then exhales when he recognises your face. Now you need to move him.",
    # a_fail
    "A motion sensor blinks red and a Yakuza scout shouts from the far alley mouth. You duck "
    "into a utility alcove as boots splash past, pressed flat against wet brick. The easy route "
    "is burned — you need to reach the accountant through the market crowd instead, "
    "but it means crossing open ground with watchers already active.",
    # b_ok
    "The right corporate badge and a borrowed tone of boredom get you waved through the "
    "checkpoint. You're inside the warren within four minutes, watchers none the wiser. "
    "The accountant is exactly where your intel placed him — pale, sweating, bag already packed. "
    "Getting him out cleanly is the next problem.",
    # b_fail
    "The fixer on the door makes a call before he waves you through. You talk him down, but "
    "two minutes burn and by the time you reach the accountant, one Yakuza scout has moved "
    "into the block. The obvious exits are being watched. You'll need to improvise the route out.",
    # mid_ok
    "The accountant moves with you through the market crowd, disciplined enough not to run. "
    "You've identified a service exit through the kitchen of a ramen bar that the Yakuza "
    "haven't covered yet — a route used by a corporate team eighteen months ago. "
    "There's one watcher outside it. One you can deal with.",
    # mid_fail
    "A Yakuza team tightens the cordon ahead of schedule, cutting off the planned exit. "
    "The accountant's breathing goes ragged and you can see the panic building. "
    "The data chip in his coat is the most valuable object in the alley right now. "
    "You need to find a way through before his nerve breaks completely.",
    # crisis
    "The last route out is a narrow service corridor running to the canal — one watcher at "
    "the entrance, hired surveillance rather than Yakuza, radio in hand. If he calls it in "
    "before you pass, every exit seals. You have one window and no second chances.",
    # recovery
    "You get through the corridor, but the spotter clocks you both and his hand goes to his "
    "radio. You close the distance fast and take it from him before the call connects. "
    "The accountant is through the canal door, but the route is burned and pursuit is thirty "
    "seconds behind you.",
    # victory
    "The canal barge moves without lights through three kilometres of dark water. The accountant "
    "sits across from you, the chip flat on the planking between you. By the time the Yakuza "
    "understand they've lost him, you're already across the district boundary. Clean extraction.",
    # partial
    "The accountant makes it out, but he dumped the chip in the canal when the spotter raised "
    "the alarm. You have the source but not the hardware evidence. He'll reconstruct what he "
    "knows from memory — useful, but months of courtroom preparation just got harder.",
    # defeat
    "The Yakuza close the alley before you reach the exit. The accountant is taken — you make "
    "it out alone through the service hatch, empty-handed and exposed. "
    "The data chip is in enemy hands before morning.",
    # choices
    "Slip past the sentries", "stealth", 7,
    "Talk through the checkpoint", "influence", 8,
    "Move via the service kitchen", "stealth", 7,
    "Push through the market crowd", "composure", 8,
    "Guide him through the back lanes", "tactics", 7,
    "Improvise a new exit route", "tactics", 8,
    "Locate the secondary canal passage", "stealth", 8,
    "Create a distraction and move fast", "composure", 9,
    "Neutralise the spotter silently", "stealth", 8,
    "Bluff through using the accountant as cover", "influence", 9,
),

_mk("tm_c02", "Glass Ceiling", "city", "city_02_corporate_atrium",
    "Plant a surveillance bug inside Prometheus-Nakamura's executive floor.", 120, 3,
    # open
    "Prometheus-Nakamura's headquarters glitters forty stories above the street grid. "
    "The lobby hums with employees and private security on twelve-minute sweep rotations. "
    "The CTO's office is on the forty-second floor and your surveillance package needs to be "
    "behind a ventilation grille up there before the 09:00 shift change.",
    # a_ok
    "Tailored jacket, borrowed credentials, and a name pulled from the corporate org chart "
    "walk you past every checkpoint without a second glance. The service elevator opens onto "
    "the forty-second floor and the CTO's office is unlocked — a pre-arranged oversight "
    "from your contact inside. The ventilation grille is exactly where the schematic showed.",
    # a_fail
    "The reception AI flags a biometric mismatch three seconds into the check. Two guards "
    "move toward you with professional calm. You make the lobby exit before they reach you, "
    "but the building is now on elevated alert and the front approach is permanently closed. "
    "You need a different way up.",
    # b_ok
    "Coveralls, a faked work order, and the building's own diagnostic codes buy you the service "
    "elevator without question. The maintenance chief barely looks at your paperwork. "
    "You're on the forty-second floor in nine minutes, with a legitimate reason to be near "
    "the CTO's climate control panel.",
    # b_fail
    "The maintenance scheduler shows no work order matching yours — someone filed incorrectly. "
    "An observant guard walks you back to the lobby while a colleague confirms the discrepancy. "
    "You talk your way out of it but lose thirty minutes and can't reuse the maintenance angle. "
    "There's still a way up if you're willing to move through the fire stairwell.",
    # mid_ok
    "You're inside the forty-second floor with time to spare. The CTO's assistant is at lunch "
    "and the office sits open. The ventilation grille is behind the bookshelf — four screws, "
    "two minutes of work. The only complication is a security camera with a partial sightline "
    "that you need to account for during the installation.",
    # mid_fail
    "A roving security supervisor decides today is the day for an unscheduled sweep of the "
    "executive floors. You're in the corridor when he turns the corner. You need to stall him "
    "long enough to complete the installation, without giving him a reason to check your bag.",
    # crisis
    "You have the bug in place and one screw left to tighten when footsteps stop outside "
    "the office door. The handle turns. You have three seconds to either hide or "
    "produce a reason to be kneeling behind the CTO's bookshelf.",
    # recovery
    "You step back from the grille with a HVAC calibration tool visible and the most "
    "convincing look of routine competence you can manage. The person in the doorway is an "
    "executive assistant, not security. She frowns — the screw is loose and visible. "
    "You're going to need to talk your way through this.",
    # victory
    "The grille is sealed, the bug is active, and you're in the lobby again before the "
    "security rotation completes. The package will transmit for thirty days before the battery "
    "dies. Everything the CTO says in that office is yours now.",
    # partial
    "The bug is installed, but the incomplete screw will be spotted in the next cleaning cycle "
    "— you had maybe seventy-two hours of transmission before someone notices. "
    "Enough for the immediate intelligence need, not the long-term surveillance your client wanted.",
    # defeat
    "Security finds you at the grille with the bug in hand. You're escorted out of the building "
    "before you can complete the installation. The package is confiscated at the lobby desk "
    "and the CTO's office goes under increased monitoring.",
    # choices
    "Impersonate an executive", "influence", 9,
    "Pose as maintenance crew", "tech", 8,
    "Access via the fire stairwell", "stealth", 8,
    "Loop back via the parking structure", "tactics", 8,
    "Move while the assistant is at lunch", "stealth", 7,
    "Present a secondary work order", "influence", 8,
    "Install behind the camera's blind spot", "tech", 8,
    "Stall the supervisor with a false fault", "influence", 9,
    "Complete and exit before the door opens", "composure", 9,
    "Explain the calibration work calmly", "influence", 9,
),

_mk("tm_c03", "Dead Stop", "city", "city_03_underground_maglev",
    "Intercept a data shipment before it boards the underground maglev.", 90, 2,
    # open
    "Three levels below the street, the underground maglev hisses on superconducting rails. "
    "Somewhere in tonight's crowd is a courier carrying encrypted personnel files on a "
    "chip the size of a thumbnail. The maglev departs in eighteen minutes. "
    "You need to find the courier and make the swap before those doors close.",
    # a_ok
    "You splice into the station's passenger system from a maintenance kiosk in under two "
    "minutes. The courier is in car four, seat eleven-B. You move to the platform and "
    "intercept her at the gate — a brief collision, a murmured apology, and the transfer "
    "case is in your jacket before she registers the weight difference.",
    # a_fail
    "The station firewall runs a passive integrity check that kills your connection in ninety "
    "seconds. You're ejected from the system and the maglev is boarding. You'll have to "
    "find the courier the old way — by eye, in a crowd of four hundred people, "
    "with twelve minutes left.",
    # b_ok
    "You board two minutes ahead of the courier, take a position with sightlines to both "
    "carriage doors, and settle in. She boards car three, not car four as the intel suggested, "
    "but your position covers both. In the tunnel between stations — no cameras, no witnesses — "
    "the swap is clean.",
    # b_fail
    "The courier spots your reflection watching her in the window glass and triggers a panic "
    "alarm before you can close the distance. Security locks the train at the next station. "
    "You exit through the service hatch ahead of the lockdown team, empty-handed, "
    "with the courier still aboard.",
    # mid_ok
    "You have the transfer case and you're moving toward the platform exit when the courier "
    "realises it's gone — the weight of an empty bag makes itself known two minutes too late. "
    "She's raising her phone. You have one service exit available before the station "
    "security cameras pick up the scene.",
    # mid_fail
    "A plain-clothes security operative has been watching the courier since before you arrived. "
    "He saw the exchange. He hasn't moved yet — he's assessing, waiting for backup or a "
    "better angle. You're forty metres from the exit with the chip and an unknown "
    "number of seconds before he acts.",
    # crisis
    "The station exit requires you to pass through a biometric scanner that logs every face. "
    "Your cover identity will hold for a routine check but not for a flagged investigation. "
    "The surveillance system is live and the operative behind you is moving. "
    "You need to get through the gate clean.",
    # recovery
    "You hand the transfer case to a commuter going through the gate — a stranger, two seconds "
    "of eye contact, enough to make him take it by reflex. The scanner logs him, not you. "
    "You exit through the maintenance door and he'll leave the case at the left-luggage point "
    "if your contact card is still in the outer pocket. It's a gamble.",
    # victory
    "You're two blocks from the station and three minutes clear before the courier reaches a "
    "station official. The chip is in an encrypted drive case in your coat. The personnel "
    "files are yours, and the courier has nothing to show for it.",
    # partial
    "The chip transfers, but the courier's panic alarm triggered a digital copy broadcast "
    "to a secondary server before you made the swap. You have the original hardware, "
    "but someone else has a backup — and you don't know who received it.",
    # defeat
    "The biometric scanner flags your face as a secondary match on an old watch list. "
    "Security holds you at the gate for twenty minutes. By the time they release you, "
    "the chip has left the city on the next maglev run.",
    # choices
    "Hack the passenger manifest", "tech", 8,
    "Shadow the courier manually", "stealth", 7,
    "Move via the service corridor exit", "stealth", 8,
    "Blend into the departing crowd", "composure", 7,
    "Exit through platform maintenance access", "tech", 7,
    "Stall and wait for the operative to look away", "composure", 8,
    "Spoof the scanner with a clone identity", "tech", 9,
    "Improvise a distraction near the gate", "tactics", 8,
    "Move through before he can signal backup", "composure", 9,
    "Trust the stranger and walk out clean", "influence", 8,
),

_mk("tm_c04", "Lightning Protocol", "city", "city_04_rooftop_storm",
    "Eliminate a high-value corporate enforcer from an overwatch position.", 140, 4,
    # open
    "Forty floors up, lightning-scorched rooftops stretch to every horizon under a boiling "
    "sky. The target steps out of his armoured car at the same time every Tuesday — fifteen "
    "seconds of exposure, one clear sightline from this position. The storm will cover the "
    "sound. The window opens in four minutes.",
    # a_ok
    "You account for the gusting crosswind and the electrical interference in your scope "
    "reticle and the shot is already resolved in your head before your finger moves. "
    "The round lands exactly where you placed it. The target goes down before his bodyguards "
    "register the sound, and you're three rooftops clear before they understand what happened.",
    # a_fail
    "The wind shifts in the final second and the shot pulls left, sparking off the car door. "
    "The target drops behind the vehicle, very much alive, and the security net closes over "
    "every rooftop exit within two blocks. You need to abort the shot and find a way down "
    "before the sweep reaches your position.",
    # b_ok
    "The storm is making the shot unpredictable and the professional thing is to call the "
    "abort when you still have time. You pass the intelligence — position, timing, guard "
    "rotation — to the ground team via encrypted burst and slip the perimeter before the "
    "window opens. A better shot next Tuesday.",
    # b_fail
    "You wait too long running the abort calculation. The window opens while you're still "
    "deciding and security finishes their sweep before you can exit cleanly. "
    "Your position on the roof is exposed when a sweep drone passes within twenty metres. "
    "You need to move now, mission or not.",
    # mid_ok
    "You're off the roof and moving through the access shaft when you hear the security net "
    "activating below. Two floors of stairwell and a service exit separate you from the street. "
    "The target's bodyguards have locked down the building entrance, but the service exit "
    "leads to an alley they haven't reached yet.",
    # mid_fail
    "The security sweep is faster than your intel suggested — three teams, not one, moving "
    "in coordinated arcs across the upper floors. You're cut off from the primary descent "
    "route and the sweep is closing from above. There's one option left: the building's "
    "external maintenance ladder, in this storm.",
    # crisis
    "The ladder is exposed to the full storm and every second on it is visible to any drone "
    "overhead. Lightning is striking the antenna array forty metres above you. "
    "You have to move — staying on the roof means capture; the ladder means exposure. "
    "Everything rests on how fast you can move.",
    # recovery
    "You make it four floors down before a security spotlight sweeps the building face. "
    "You freeze against the wall, one hand on each rung, and wait for the arc to pass. "
    "It takes eleven seconds that feel like eleven minutes. When it moves on, "
    "you drop the last two floors to the alley.",
    # victory
    "The alley is clear and the rain is heavy enough to wash your footprints before the "
    "first ground team reaches it. You're in a vehicle and moving inside ninety seconds. "
    "The target is confirmed down. The operation is clean.",
    # partial
    "You're out and clear, but a security camera at the alley exit caught a partial image "
    "before the rain took it. Not enough to identify you, but enough to confirm someone was "
    "on that rooftop. The contract is fulfilled, but your cover profile has taken a hit.",
    # defeat
    "A security team reaches the rooftop before you can clear the access shaft. You're "
    "detained on the building roof in the middle of a lightning storm, the weapon still in "
    "your case. The target walks away alive and your team is compromised.",
    # choices
    "Take the long shot through the storm", "firearms", 10,
    "Signal abort and extract clean", "tactics", 8,
    "Descend via the service stairwell", "stealth", 8,
    "Push through the locked-down lobby", "composure", 9,
    "Use the service exit before it's covered", "stealth", 8,
    "Improvise a route through the adjacent building", "tactics", 9,
    "Move fast and accept the exposure", "composure", 9,
    "Climb down in the sweep blind spot", "stealth", 10,
    "Sprint the ladder before the light returns", "composure", 9,
    "Drop to the alley and move before the arc resets", "athletics", 8,
),

_mk("tm_c05", "Black Script", "city", "city_05_closed_market",
    "Source black-market medical supplies from the Chrome Warrens underground bazaar.", 80, 2,
    # open
    "The Closed Market operates three sub-levels down — a labyrinth of stalls selling "
    "everything the above-ground economy has banned. You need three crates of military-grade "
    "trauma patches, no questions asked. The vendor knows someone is coming. "
    "So does every other buyer in the district.",
    # a_ok
    "Your contact knows the vendor's real name, his leverage points, and his favourite brand "
    "of synthetic whisky. The deal closes in eight minutes at a price that barely stings, "
    "and the crates are loaded into the service vehicle before the rival buyer even locates "
    "the right sub-level.",
    # a_fail
    "Your fixer's loyalty lasts exactly as long as a better offer. You arrive to find the "
    "vendor deep in conversation with a rival buyer, the crates already stacked behind them. "
    "The fixer won't meet your eyes. You still have money and the market is still open — "
    "but you'll need to find another source.",
    # b_ok
    "You know what genuine military-grade trauma patches look like and what the counterfeits "
    "don't. Half an hour of methodical stall-checking turns up a legitimate cache three rows "
    "in, and you negotiate the price down by citing what you know about the supply chain. "
    "The vendor respects competence.",
    # b_fail
    "Every crate you open contains substitutes — saline, expired stock, industrial-grade "
    "wound seal that won't survive a real trauma case. The counterfeit network in this market "
    "is better than your intel suggested. The legitimate vendor has already packed up "
    "and the market is thinning.",
    # mid_ok
    "You have three crates confirmed genuine and a deal on the table. The rival buyer is back "
    "with more money and another attempt at the same vendor — who is now looking at both of "
    "you with the calculating expression of someone considering an auction. "
    "You need to close this before it becomes a bidding war.",
    # mid_fail
    "The vendor you've been negotiating with gets cold feet when he sees the rival buyer's "
    "credentials — corporate acquisition team, and they're not subtle. He pulls back from "
    "your deal and starts making excuses. You're going to lose this unless you act now.",
    # crisis
    "The corporate buyer's security team has appeared at the sub-level entrance. They're here "
    "to ensure the crates leave with their client — legally or otherwise. The vendor is "
    "looking at them and then at you, trying to calculate which outcome is safer for him. "
    "You have maybe thirty seconds to make this go your way.",
    # recovery
    "You get the vendor moving toward the service exit with one crate, but the corporate team "
    "has the other two. You argue your way to a compromise — a single crate and the vendor's "
    "supplier contact for the next order. Not what you came for, but something.",
    # victory
    "All three crates are loaded and moving before the corporate team reaches the sub-level. "
    "The vendor is paid and the market has closed around them. You're in the vehicle with "
    "the supplies your field medics have been waiting three weeks for.",
    # partial
    "You leave with one crate and the supplier contact. Enough for immediate critical cases, "
    "but you'll need to return for the rest — and the corporate team now knows someone else "
    "is buying in this market.",
    # defeat
    "The corporate team moves faster than you anticipated. The crates are loaded into their "
    "vehicle before you can make a counter-offer that the vendor would accept. You leave "
    "the market empty-handed and the rival buyer leaves satisfied.",
    # choices
    "Negotiate through a fixer contact", "influence", 7,
    "Search the market stalls yourself", "medicine", 7,
    "Close before the bidding starts", "influence", 8,
    "Expose the rival buyer's weak position", "tactics", 7,
    "Pressure the vendor to honour the deal", "influence", 8,
    "Find an alternate vendor before he bolts", "composure", 8,
    "Make the corporate team's presence a liability for the vendor", "influence", 9,
    "Physically secure the crates and negotiate later", "close_combat", 8,
    "Buy out the deal before the team arrives", "influence", 9,
    "Appeal to the vendor's self-interest", "influence", 8,
),

_mk("tm_c06", "Triage", "city", "city_06_street_clinic",
    "Treat a wounded contact under corporate surveillance without drawing attention.", 90, 3,
    # open
    "The street clinic on Block Nine is a legitimate operation — which is exactly why corporate "
    "intelligence has two observers watching the door. Your contact, shot during an extraction "
    "three days ago, cannot survive another seventy-two hours without surgical care. "
    "The clinic has the equipment. You need to get him there without triggering the watchers.",
    # a_ok
    "You walk in presenting credentials from a licensed off-books practice — technically "
    "fraudulent, but the biometric markers are clean. The intake nurse registers a routine "
    "surgical consult. Your contact is admitted as a patient with a fabricated name. "
    "The watchers outside file a report about a standard intake. Two hours of surgery begins.",
    # a_fail
    "The intake system flags an inconsistency in the practitioner credentials mid-check. "
    "A supervisor appears. You talk your way out of it but your contact's fabricated identity "
    "is now being run through a secondary verification. The clinical route is compromised. "
    "You'll need to treat him at the secondary safe location instead.",
    # b_ok
    "You keep your voice level and your hands completely still as you guide your contact past "
    "both watchers — he's leaning on you, posing as a relative helping an elderly parent. "
    "Neither observer looks twice. He's in the secondary site and you have the surgical kit "
    "open within the hour.",
    # b_fail
    "He destabilises during the move — blood pressure drop, loss of consciousness for eight "
    "seconds. You stabilise him in a doorway forty metres from both watchers, but the delay "
    "means the observers complete a rotation and the secondary site approach is now covered. "
    "The only viable option is back to the clinic.",
    # mid_ok
    "The surgery is underway in the back examination room. Your contact is stable under "
    "local anaesthetic and the equipment is functional. The problem is the corporate observer "
    "who just stepped inside the clinic lobby — routine, probably, but he's talking to the "
    "front desk and your patient's name is on the intake board.",
    # mid_fail
    "A second observer enters the clinic and begins a systematic check of the intake records "
    "while you're mid-procedure. Your contact's fabricated name will hold under a casual "
    "review but not a careful one. You have four minutes before the check reaches today's "
    "admissions log.",
    # crisis
    "The observer is at the admission desk and asking the duty nurse about a patient fitting "
    "your contact's description. The nurse doesn't know his real name but she knows the room "
    "number. You need to either move him or intercept that conversation, right now.",
    # recovery
    "You step out of the examination room and redirect the observer with a medical authority "
    "you don't technically hold — a confident explanation of patient confidentiality law and "
    "the phrase 'I'll need to see your authorisation in writing' buys ten minutes. "
    "Enough to finish the critical procedure.",
    # victory
    "Your contact is stable by morning. The watchers filed reports about routine clinic "
    "traffic and saw nothing they recognised. He'll need six weeks of recovery, "
    "but he'll recover. The surgical kit goes back into the bag clean.",
    # partial
    "The surgery is complete but your contact was moved before full stabilisation. He's alive "
    "and the critical risk is past, but the recovery will be longer and more complicated "
    "than it should have been. He's also at a location the observers are now aware of.",
    # defeat
    "The observer reaches the room number before you can intercept him. Your contact is "
    "taken into corporate custody mid-procedure — alive, but now in the hands of the people "
    "who shot him. The surgical kit is left on the table.",
    # choices
    "Enter as a licensed practitioner", "medicine", 8,
    "Move him via the back exit past the watchers", "composure", 8,
    "Handle the lobby observer with authority", "influence", 8,
    "Finish the procedure and move him after", "medicine", 9,
    "Redirect the check at the admission desk", "influence", 8,
    "Change the room assignment in the system", "tech", 8,
    "Intercept the conversation before the nurse answers", "composure", 9,
    "Move the patient to a second room now", "medicine", 9,
    "Hold the observer off with a paperwork challenge", "influence", 9,
    "Complete the critical work in the window you have", "medicine", 8,
),

_mk("tm_c07", "Zero-Day", "city", "city_07_data_vault",
    "Extract encrypted personnel files from a hardened corporate data vault.", 150, 4,
    # open
    "The data vault sits behind six security layers and a physical air-gap — except for the "
    "fifteen-minute maintenance window that opens every Wednesday at 02:00. Inside: personnel "
    "files on every corporate black-ops agent in the Western sector. "
    "The window is open. The clock is already running.",
    # a_ok
    "You strip through the authentication layers with practiced efficiency — twelve minutes "
    "for six locks, three minutes to spare. The file directory opens and you pull the complete "
    "personnel package to an encrypted drive. The vault doesn't know it was touched. "
    "You're back out the maintenance corridor before the window closes.",
    # a_fail
    "The inner firewall is a newer revision than your intel shows. You make it to the file "
    "directory with two minutes remaining — not enough time to pull the package. "
    "The window closes with you still mid-transfer and the intrusion alarm triggers. "
    "You have seconds to decide whether to run or try to cover your tracks.",
    # b_ok
    "Two days of careful cultivation paid off tonight. The overnight technician holds the "
    "maintenance door open for a colleague and looks the other way for twelve minutes. "
    "The files leave in a plain carry bag. He'll be questioned tomorrow and he'll say he "
    "saw nothing, because technically he didn't.",
    # b_fail
    "The technician gets cold feet thirty seconds before the handoff. He reports the "
    "approach to his supervisor before you can talk him down. You're made before you reach "
    "the vault level — pulled aside at the security desk with a polite but non-optional "
    "request to wait for the duty officer.",
    # mid_ok
    "The files are in your hands and you're moving toward the maintenance exit when a second "
    "technician appears on an unscheduled round — not looking for you, but present. "
    "He'll pass within three metres of you in the corridor. You have the drive in a bag "
    "that looks entirely ordinary, but you need to decide how to handle the next thirty seconds.",
    # mid_fail
    "The intrusion alarm has been logged but not yet escalated — a junior security operator "
    "is running a routine check rather than a full response. You have a narrow window to "
    "either complete the extraction or sanitise the log entry before it reaches a supervisor "
    "who knows what they're looking at.",
    # crisis
    "The security gate between the vault level and the street exit requires a badge tap that "
    "logs your exit timestamp. If the alarm has already been escalated, that log entry "
    "creates a direct trail. If it hasn't, you walk out clean. "
    "You're at the gate with no way to know which scenario you're in.",
    # recovery
    "You abort the direct exit and take the maintenance tunnel that runs to the loading dock — "
    "unmonitored, unlogged, and two minutes longer. The files are still with you. "
    "You surface on the street four minutes after the maintenance window closes, "
    "with no record that you were ever inside the building.",
    # victory
    "You're in a vehicle and moving before the security log flags the anomaly. By the time "
    "the vault runs its morning integrity check, the encrypted drive is in a courier package "
    "heading to the analysis team. Every corporate black-ops agent in the sector, "
    "identified and documented.",
    # partial
    "You have the files, but the intrusion was logged and will be investigated. The data is "
    "yours, but the vault now knows it was accessed and every name on that list is being "
    "quietly moved. You have hours before the intelligence becomes stale.",
    # defeat
    "The security gate flags the timestamp discrepancy and a rapid response team reaches "
    "the vault level in under four minutes. The drive is taken at the exit. "
    "You're detained for six hours and released without charge — but without the files.",
    # choices
    "Direct hack through the maintenance terminal", "tech", 9,
    "Social-engineer the overnight vault technician", "influence", 9,
    "Walk past with a neutral expression", "composure", 7,
    "Sanitise the log before it escalates", "tech", 9,
    "Erase the access record at the terminal", "tech", 9,
    "Stall the secondary operator with a false alert", "influence", 8,
    "Tap through and move fast", "composure", 9,
    "Take the maintenance tunnel exit", "stealth", 7,
    "Clear the log entry at the gate terminal", "tech", 9,
    "Move to the loading dock exit instead", "stealth", 8,
),

_mk("tm_c08", "Pressure Test", "city", "city_08_maintenance_corridor",
    "Sabotage a facility's environmental systems to force an evacuation.", 100, 3,
    # open
    "The target facility runs around the clock. The only way to clear it without a firefight "
    "is to make it uninhabitable. The maintenance corridor behind the east cooling units "
    "links every environmental system in the building. You're in. "
    "Now you need to decide how this ends.",
    # a_ok
    "You pull up the building management system from the junction panel and the interface is "
    "exactly what the schematic promised. CO₂ levels rise on a controlled curve. Temperature "
    "climbs. The building empties in under twenty minutes, citing a sensor malfunction "
    "that nobody argues with. The facility is clear.",
    # a_fail
    "The junction panel runs a firmware version two generations older than your tools expect. "
    "The command fails silently, then triggers an alarm three minutes later — not the "
    "evacuation alarm you wanted, but the security lockdown alarm you didn't. "
    "The building isn't emptying. It's sealing.",
    # b_ok
    "You move through the maintenance crawlspace without a sound and wedge the timed device "
    "in the coolant junction exactly where the schematic indicated. Forty minutes later, "
    "the temperature spikes and the fire-suppression system triggers automatically. "
    "The evacuation is clean and the device leaves no fingerprints.",
    # b_fail
    "A maintenance technician is running a routine check on the coolant line you needed. "
    "He's there for twenty minutes minimum. You can't place the device without being seen "
    "and confronting him would make noise the security team would hear. "
    "You need an alternative before your window closes.",
    # mid_ok
    "The facility is beginning to evacuate — you can hear the floor-by-floor PA from inside "
    "the corridor. Most personnel are moving toward the exits. But a security team is running "
    "a sweep of the maintenance areas, looking for the cause before they complete the "
    "evacuation. They'll be at this corridor in eight minutes.",
    # mid_fail
    "The lockdown has complicated the evacuation — personnel are confused about which exits "
    "are open and the PA system is giving conflicting instructions. The building is partially "
    "empty but not clear, and a security supervisor is working the problem in the control "
    "room directly above you.",
    # crisis
    "The security sweep has reached the maintenance corridor junction. One guard is moving "
    "your direction with a torch and a radio. You're in the crawlspace with a clear path "
    "to the service exit — but only if he turns left at the junction instead of right. "
    "His footsteps are six metres away.",
    # recovery
    "He turns right, then doubles back. You press into a recess in the ductwork and he passes "
    "within arm's reach, sweeping the torch in the opposite direction. Your exit is behind him. "
    "You wait twenty seconds and then move.",
    # victory
    "You're in the service alley when the last personnel clear the lobby. The facility stands "
    "empty for six hours while environmental services investigates the cause. "
    "Your team has six hours of unmonitored access to the building.",
    # partial
    "The facility cleared, but the security team logged an anomaly in the maintenance "
    "corridor before leaving. They won't connect it to the environmental event immediately, "
    "but the investigation will eventually reach the right conclusion. "
    "Your team has three hours instead of six.",
    # defeat
    "The guard finds the device — or finds you — before the evacuation completes. "
    "Security cancels the evacuation and the lockdown becomes a search operation. "
    "The facility doesn't clear and your window is gone.",
    # choices
    "Reprogram the climate control remotely", "tech", 8,
    "Plant a timed device in the coolant line", "close_combat", 7,
    "Exit before the sweep reaches this section", "stealth", 8,
    "Override the PA to complete the evacuation", "tech", 8,
    "Disable the supervisor's control console", "tech", 8,
    "Redirect the sweep team with a false alarm", "tactics", 8,
    "Hold position and wait for the guard to pass", "composure", 8,
    "Move behind the guard and take the exit", "stealth", 8,
    "Time the exit to the torch sweep pattern", "stealth", 8,
    "Move in the thirty-second gap between passes", "composure", 7,
),

_mk("tm_c09", "Broken Signals", "city", "city_09_safehouse_apartment",
    "Debrief a traumatised informant who has gone silent after three days in hiding.", 80, 2,
    # open
    "The safehouse apartment smells of cold takeout and stale fear. Your contact has been "
    "here for three days since the extraction — too shaken to transmit, too valuable to leave. "
    "He knows the names of every corporate sleeper agent in the city, but right now "
    "he won't say a word. That changes tonight.",
    # a_ok
    "You sit across from him for an hour without demanding anything — let him talk about "
    "unrelated things, his childhood, a film he liked, anything that isn't the operation. "
    "His breathing evens out over the course of the evening. By midnight he's given you "
    "six names, three locations, and a cover identity you didn't know existed.",
    # a_fail
    "You push too hard at the wrong moment — the patience runs out and you press for the "
    "names directly. He shuts down completely, pulls into himself, and asks you to leave. "
    "Three days of silence become four. You need a different approach.",
    # b_ok
    "You lay the operational picture in front of him without embellishment — what silence "
    "costs, what cooperation protects. He's frightened, not irrational. The debrief takes "
    "forty minutes and he gives you everything he knows, speaking fast and with the "
    "relief of someone setting down a very heavy bag.",
    # b_fail
    "He reads your operational framing as a threat rather than a reality check. He closes "
    "down, stops making eye contact, and asks for a different handler. He runs during the "
    "night — you find the safehouse empty at 03:00, his bag gone, no note.",
    # mid_ok
    "You have names and partial addresses — enough to act on two of the six leads immediately. "
    "Your contact is calmer now but exhausted, and he's mentioned a seventh name twice "
    "without giving you the full details. Something about that name makes him hesitate. "
    "You need to understand why before you end the debrief.",
    # mid_fail
    "He's given you the names but the operational details are fragmentary — meeting schedules, "
    "cover identities, partial addresses. He knows more but he's protecting something, "
    "or someone. The intelligence you have is valuable but incomplete, and he's shutting "
    "down as the night wears on.",
    # crisis
    "He stops mid-sentence when you ask about the seventh name. He stares at the table for "
    "thirty seconds and then looks up with an expression you recognise — a person deciding "
    "whether to cross a line they can't uncross. Whatever that seventh name represents, "
    "it's the most important thing in the room right now.",
    # recovery
    "He doesn't give you the seventh name but he gives you enough context to work from — "
    "a district, a role, a physical description. It's not the clean intelligence you needed "
    "but it's something your analysts can work with if they're patient.",
    # victory
    "He gives you the seventh name at 02:00, along with a meeting location and a schedule "
    "he memorised because he knew it would matter someday. Seven corporate sleeper agents, "
    "fully documented. The network is yours.",
    # partial
    "Six names, partial details, and a description that might be the seventh. Enough to disrupt "
    "the network but not to roll it up cleanly. Some of them will get word and vanish "
    "before you can act on every lead.",
    # defeat
    "He runs before dawn. You have nothing from the debrief and a burned safehouse. "
    "The sleeper network is intact and now they know someone was asking about them.",
    # choices
    "Gentle approach — build trust first", "composure", 7,
    "Direct questioning — time is critical", "influence", 8,
    "Probe carefully around the seventh name", "composure", 8,
    "Review the partial details for hidden patterns", "tactics", 7,
    "Ask what he needs to feel safe enough to say it", "composure", 8,
    "Lay out what you know and let him fill the gaps", "influence", 8,
    "Wait in silence and let him decide", "composure", 9,
    "Tell him what the seventh name means to your operation", "influence", 9,
    "Ask him directly and hold his gaze", "composure", 9,
    "Work backward from the context he gave you", "tactics", 8,
),

_mk("tm_c10", "Pier Pressure", "city", "city_10_industrial_waterfront",
    "Intercept an illegal arms deal before the shipment leaves the waterfront.", 110, 3,
    # open
    "The industrial waterfront is all rust and salt air, cranes standing dark against a low "
    "sky. The deal happens at midnight — two parties, six crates of unlicensed pulse rifles, "
    "one window. You need to stop the exchange without starting a firefight "
    "that echoes across the harbour.",
    # a_ok
    "You're on the upper gantry twenty minutes before the buyers arrive — good position, "
    "sightlines to both approach routes and the exchange point. When the crates change hands "
    "you trigger the signal. Port authority arrives to find everyone still in place. "
    "The rifles never reach the street.",
    # a_fail
    "A loose chain catches your foot and the metallic crash freezes both parties. "
    "By the time you recover your position, the buyers have disappeared into the water "
    "and the sellers are moving the crates toward a secondary exit you didn't account for.",
    # b_ok
    "You redirect the cargo routing paperwork two hours before the meeting — one forged "
    "manifest, one cooperative crane operator who asks no questions. The crates are "
    "quarantined by port inspection before the sellers even arrive. "
    "The deal dies before it begins.",
    # b_fail
    "The cargo routing is locked by a secondary authority code you don't have and can't "
    "replicate in time. The exchange proceeds on schedule and the rifles are loaded onto "
    "a launch before you can reposition.",
    # mid_ok
    "Port authority is holding both parties but the authority officer is looking at paperwork "
    "that doesn't clearly establish what the crates contain — the manifest has been altered "
    "and the serial numbers are obscured. You need to give them something concrete before "
    "both parties are released on technicalities.",
    # mid_fail
    "The sellers got one crate aboard a launch before port authority arrived. It's moving "
    "out into the harbour right now with enough rifles to arm a small operation. "
    "The other five crates are secured but the sixth is getting away.",
    # crisis
    "The launch is a hundred metres out and accelerating. There's a harbour patrol boat "
    "at the pier — not staffed, but its radio is live. If you can reach the patrol officer "
    "on the waterfront office frequency before the launch clears the harbour mouth, "
    "there's still a chance.",
    # recovery
    "The patrol officer responds but takes two minutes to process the request — two minutes "
    "during which the launch gets outside the harbour boundary. You get a partial "
    "intercept at the boundary marker, recovering three of the six rifles from the crate. "
    "The other three reach open water.",
    # victory
    "All six crates are secured and both parties are in custody before the harbour authority "
    "shift change. The rifles are catalogued and impounded. Your client gets the serial "
    "numbers, the chain of ownership, and a clean operation.",
    # partial
    "Five crates secured, one partially recovered. The buyers are held, the sellers got away. "
    "Most of the shipment is off the street, but the three missing rifles are somewhere "
    "in the city and you don't know who has them.",
    # defeat
    "The launch clears the harbour mouth before anyone can intercept it. All six crates "
    "are gone. Both parties disperse into the waterfront and port authority finds nothing "
    "at the exchange point except a forged manifest.",
    # choices
    "Set up an ambush position on the gantry", "stealth", 8,
    "Intercept via the cargo routing paperwork", "tactics", 8,
    "Provide the authority officer with the serial numbers", "tech", 7,
    "Board the launch before it clears the pier", "close_combat", 8,
    "Raise the patrol boat on the harbour frequency", "tactics", 8,
    "Coordinate a harbour boundary intercept", "tactics", 9,
    "Signal the patrol boat directly from the pier", "composure", 8,
    "Chase the launch in the harbour tender", "close_combat", 9,
    "Get the patrol officer moving immediately", "influence", 9,
    "Track the launch to its next stop", "stealth", 8,
),

]  # end _CITY block 1 (tm_c01–tm_c10)


# ── CITY MISSIONS 11–20 ───────────────────────────────────────────────────────

_CITY_2 = [

_mk("tm_c11", "Public Address", "city", "city_11_civic_plaza",
    "Defuse a rapidly escalating protest before it turns violent.", 90, 3,
    "Three hundred people fill the civic plaza and the number is climbing. Corporate security "
    "has formed a line at the north end, riot shields locked. At the crowd's centre an agitator "
    "is feeding anger toward something that could break the whole district. "
    "You have ten minutes before the first canister goes off.",
    # a_ok
    "You push to the front and take the microphone before security reaches it. Two minutes "
    "of the right words — acknowledgement, a concrete demand they can carry home, a target "
    "that isn't each other — and the energy shifts. The crowd disperses with a chant "
    "instead of broken glass.",
    # a_fail
    "You reach the podium but the agitator shouts over you and the crowd chooses him. "
    "Security reads the noise as escalation and moves the line forward. "
    "The first canister goes off on the east side and the situation is now well past words. "
    "You need to find a different way to end this.",
    # b_ok
    "You move through the crowd laterally, cutting off the agitator's exit routes while "
    "two contacts create a distraction at the plaza edge. Separated from his audience, "
    "he loses momentum. Without the voice, the crowd deflates on its own.",
    # b_fail
    "The agitator has more backup than you calculated. Your isolation attempt gets you "
    "surrounded by his people instead of him. Security misreads the scene and deploys "
    "a second line directly into the crowd. It gets worse before it gets better.",
    # mid_ok
    "The crowd is thinning but a hard core of thirty remains around a broken barricade, "
    "throwing debris at the security line. The security commander has his hand on the "
    "radio and is four seconds from calling a full dispersal order. "
    "If he does, people get hurt.",
    # mid_fail
    "Two factions within the protest have turned on each other — the agitator's core group "
    "and a counter-protest that arrived from the south entrance. Security is now caught "
    "between three groups and the commander has lost tactical coherence. "
    "You need to give him a reason to stand down.",
    # crisis
    "The security commander is raising his radio. Behind him his line is locked and ready. "
    "In front of him the crowd is still angry but no longer unified. This can still end "
    "without injuries if the commander holds for thirty more seconds. "
    "You need to reach him before he calls it.",
    # recovery
    "You reach the commander and show him the footage you've been recording — the crowd "
    "thinning, the agitator isolated, no active weapons in the crowd. He pauses, looks, "
    "and lowers the radio. Thirty seconds. It's enough.",
    # victory
    "The plaza clears in the next twenty minutes without a single arrest for violence. "
    "The agitator is detained at the north exit for questioning. The security commander "
    "stands down his line and files a report that reads 'situation resolved without incident'.",
    # partial
    "The dispersal completes but two people are injured in the last push — non-lethal, "
    "but recorded. The agitator escapes in the confusion. The district will be tense "
    "for days and the footage will make the rounds.",
    # defeat
    "The full dispersal order goes out. The plaza empties violently and the news drones "
    "document all of it. Seven injuries, thirty detentions, and the agitator is a "
    "martyr by morning.",
    "Take the podium and redirect the crowd", "influence", 9,
    "Isolate the agitator from his audience", "tactics", 8,
    "Appeal directly to the hard-core group", "composure", 8,
    "Redirect the commander's attention", "influence", 9,
    "Show the commander the crowd is breaking", "tactics", 8,
    "De-escalate the inter-protest clash first", "composure", 9,
    "Reach the commander before he calls it", "composure", 9,
    "Physically position between him and his radio", "close_combat", 8,
    "Present the footage and make the case", "influence", 9,
    "Ask him to hold thirty seconds and count them", "composure", 8,
),

_mk("tm_c12", "After Hours", "city", "city_12_entertainment_district",
    "Extract a corporate VIP from a compromised nightclub before his rivals close in.", 100, 3,
    "The Helix Club is packed — four levels of bodies, strobing neon, and bass you feel in "
    "your molars. Your contact is on level three, unaware that two rival fixers are already "
    "on level one with his photograph. He thinks tonight is a celebration. "
    "You know it's a deadline.",
    # a_ok
    "You lean in close and speak calmly over the music — the right lie, his best friend's "
    "name, an urgency that sounds casual. He reads the subtext immediately. He finishes "
    "his drink in one swallow, excuses himself, and you're both in the service exit "
    "before the fixers clear level two.",
    # a_fail
    "He doesn't believe you. He orders another drink and tells you to relax. "
    "The fixers reach level three while you're still arguing. You have ninety seconds "
    "before they identify him across the room.",
    # b_ok
    "You trigger the fire suppression system on level two — foam and a shrieking alarm "
    "that empties the building in under three minutes. In the controlled chaos you have "
    "him out the back and in a vehicle before the fixers understand what happened.",
    # b_fail
    "You pull the wrong suppression trigger and lock down level three instead of initiating "
    "an evacuation. Your contact and both fixers are now sealed in together. "
    "You've created the hostage situation you were trying to prevent.",
    # mid_ok
    "You're moving through the staff corridor when a third party appears — not one of the "
    "two fixers, but someone your contact clearly recognises and clearly fears. He stops "
    "walking. You need him moving again in the next ten seconds.",
    # mid_fail
    "One of the fixers has reached the service exit ahead of you — someone tipped them. "
    "Your contact sees him and freezes. There are two ways out of this corridor and "
    "one of them is now blocked.",
    # crisis
    "The service exit opens onto a loading dock where a vehicle is waiting — yours. "
    "The fixer is behind you and the third unknown party is watching from the "
    "corridor entrance. Your contact has to choose between moving and staying. "
    "So do you.",
    # recovery
    "You put yourself between your contact and the fixer and give your contact the vehicle "
    "keys and the address. He runs. You stay for the conversation that needs to happen "
    "before you can follow.",
    # victory
    "Your contact is in the vehicle and moving before the fixers reach the loading dock. "
    "You walk out the front entrance two minutes later, hands in your pockets. "
    "The rivals leave the club empty-handed.",
    # partial
    "Your contact escapes but the third unknown party has his secondary identity now. "
    "He's safe tonight, but his cover in this district is compromised and "
    "he'll need to relocate.",
    # defeat
    "The fixers reach your contact before you can get him clear. He's taken in a way that "
    "looks voluntary to everyone in the club. You leave alone and he doesn't answer "
    "his phone.",
    "Talk him out without tipping the rivals", "influence", 8,
    "Create a distraction and move in the confusion", "composure", 8,
    "Keep him moving through the staff corridor", "influence", 8,
    "Neutralise the fixer at the exit", "close_combat", 8,
    "Move fast and trust him to keep up", "composure", 8,
    "Find the second exit before the fixer does", "tactics", 8,
    "Make the call and get him running", "composure", 9,
    "Hold the fixer back long enough for him to clear", "close_combat", 9,
    "Talk the fixer out of pursuing", "influence", 9,
    "Follow via a different exit and meet at the vehicle", "stealth", 8,
),

_mk("tm_c13", "Aerial Assets", "city", "city_13_drone_hangar",
    "Steal a prototype surveillance drone from a corporate research hangar.", 140, 4,
    "The drone hangar sits at the edge of the corporate campus — a cavernous space of "
    "prototypes under drop-cloths. The next-generation surveillance drone you need is "
    "grounded for firmware calibration and won't be unguarded again for six months. "
    "Tonight is the window.",
    # a_ok
    "You splice into the hangar's security node from the adjacent service tunnel and flip "
    "every camera to a five-minute loop before the guard rotation begins. The drone is in "
    "a cargo van and rolling off the property before the loop ends. "
    "The camera logs show an empty hangar all night.",
    # a_fail
    "The security node runs a passive integrity check that catches the splice in forty "
    "seconds. An alert reaches the security office before you can pull the camera loop. "
    "Guards are in the hangar in under three minutes. The drone is still there — "
    "so, for the moment, are you.",
    # b_ok
    "Your contact inside the maintenance crew marks the drone as defective on the work "
    "order and rolls it to the disposal bay — where your van is waiting. On paper, "
    "it was sent to recycling. The hangar log will show a routine disposal at 21:15.",
    # b_fail
    "Your maintenance contact is running two hours late and isn't answering. The window "
    "expires before he arrives, and the next shift finds the disposal bay empty except "
    "for you and no drone in sight.",
    # mid_ok
    "The drone is in the van and the vehicle is on the access road when a corporate security "
    "patrol flags the manifest for a secondary inspection. The manifest your contact "
    "provided says recycling transport, but the patrol officer is reading it carefully. "
    "One wrong answer ends this.",
    # mid_fail
    "A guard from the hangar has followed the van on foot — he saw something on the "
    "disposal order that didn't add up and he's radioing it in while he walks. "
    "You need to deal with this before he completes the call.",
    # crisis
    "The checkpoint at the campus exit requires a vehicle scan that will flag the drone's "
    "active firmware signature. Recycling transport shouldn't have live hardware. "
    "The scanner operator is running the check right now.",
    # recovery
    "You pull to the side and trigger the drone's standby mode — it won't transmit "
    "a firmware signature in standby. The scan comes back clean but the delay means "
    "the guard who was following on foot has now reached the checkpoint.",
    # victory
    "The van rolls off the campus property at 22:30, carrying a prototype worth three "
    "years of corporate R&D. The hangar won't notice it's gone until the morning calibration "
    "run. By then it's already disassembled for analysis.",
    # partial
    "The drone is out, but the firmware was partially wiped when you triggered standby. "
    "The hardware is intact but the proprietary flight algorithms are gone. "
    "Your client gets the sensor package, not the navigation system.",
    # defeat
    "The checkpoint flags the firmware signature. Security holds the van and the drone "
    "is returned to the hangar under escort. Your contact in maintenance is suspended "
    "pending investigation.",
    "Override the security grid remotely", "tech", 9,
    "Use the maintenance disposal cover", "tactics", 8,
    "Answer the manifest questions without hesitation", "composure", 8,
    "Intercept the guard before he completes the call", "stealth", 8,
    "Trigger standby and delay the scan", "tech", 8,
    "Move the guard's attention to another vehicle", "influence", 9,
    "Get through the checkpoint before standby wears off", "composure", 9,
    "Argue the manifest ambiguity at the checkpoint", "influence", 9,
    "Drive through before the guard reaches the booth", "composure", 9,
    "Divert through the secondary exit", "tactics", 8,
),

_mk("tm_c14", "Bridge of Glass", "city", "city_14_monorail_bridge",
    "Protect a corporate witness during a high-speed monorail transit.", 130, 4,
    "The monorail bridge crosses the canyon district in eight minutes. Your witness is "
    "exposed, moving, and cannot run. Three assassins boarded at the previous station — "
    "you made them in the platform cameras. The witness doesn't know they exist yet. "
    "You do, and you have eight minutes.",
    # a_ok
    "You seal the connecting doors between cars three and four and use the emergency "
    "intercom to redirect the transit security team to your position. Two assassins hit "
    "the sealed bulkhead and are arrested. The third exits through the roof hatch "
    "and is taken at the far station.",
    # a_fail
    "The door seal malfunctions — a manufacturing defect in the emergency latch. "
    "The first assassin is through car three before security arrives. "
    "The witness is hit in the crossfire. Alive, but the transit has become a "
    "crime scene and your position is compromised.",
    # b_ok
    "Clean threat assessment, faster draw. The first two go down non-lethally before "
    "they reach car three. The third breaks for the emergency exit between stations "
    "and is taken by the bridge security team. The witness steps off shaken but intact.",
    # b_fail
    "The suppressor misfires on the first round. The sound panics the car and the assassins "
    "use the chaos to close the distance before you can recover a shooting position. "
    "The witness is between you and them.",
    # mid_ok
    "Two of the three are down. The third has pulled back to car five and is waiting — "
    "he knows you're between him and the witness, and he's patient. The bridge transit "
    "ends in four minutes at the far station where police will board. "
    "You need to keep the witness alive for four minutes.",
    # mid_fail
    "The witness has been hit — non-fatal, a graze, but he can't move quickly. You need "
    "to get him to the next car back while the remaining assassin is advancing from the "
    "front. The bridge is halfway complete. The far station is three minutes away.",
    # crisis
    "The last assassin has your position and the witness is visible through the car window. "
    "The train is sixty seconds from the far station where police are waiting on the platform. "
    "If you can keep him from getting a clear shot for sixty seconds, it's over.",
    # recovery
    "You use the seat backs as a moving barricade, staying low, keeping the witness below "
    "the window line. The assassin fires once and misses. The train pulls into the "
    "far station and the doors open to armed officers on the platform.",
    # victory
    "Police board at the far station and take the last assassin into custody before he can "
    "exit. The witness is shaken but unharmed. He gives his statement on the platform "
    "and the testimony you needed is intact.",
    # partial
    "The witness survives but took a minor injury in the exchange. He'll testify, but "
    "his legal team is talking about postponement for medical reasons. "
    "The schedule your client needed is slipping.",
    # defeat
    "The last assassin reaches the witness in the final thirty seconds of the transit. "
    "The testimony is lost. Your client's case collapses without the witness, "
    "and you ride the rest of the way to the far station with nothing.",
    "Lock down the car and call transit security", "tactics", 9,
    "Put them down before they close the distance", "firearms", 8,
    "Keep him below the window line and wait it out", "composure", 8,
    "Move the witness back while he advances forward", "tactics", 9,
    "Hold position and deny him the angle", "tactics", 9,
    "Counter-move through the roof access hatch", "stealth", 9,
    "Use the seat barricade and ride out the sixty seconds", "composure", 9,
    "Draw his fire and put him down in the exchange", "firearms", 9,
    "Stay mobile and keep the witness moving", "composure", 8,
    "Signal the platform officers through the window", "tactics", 8,
),

_mk("tm_c15", "Running Dark", "city", "city_15_border_ruins",
    "Move a high-value defector through a collapsed district checkpoint.", 100, 3,
    "The border ruins mark the edge of corporate territory — crumbled towers and an "
    "unmanned checkpoint watched by sensor arrays covering three obvious routes. "
    "Your defector cannot be scanned, and neither can the files he carries. "
    "You go through the ruins in the dark.",
    # a_ok
    "Two hours through debris and collapsed floors, moving only between sensor sweeps. "
    "The defector follows your footsteps exactly — he's trained, whatever his other "
    "faults. You cross the boundary in complete silence. The sensor log shows nothing.",
    # a_fail
    "The array has a new auxiliary unit installed since your last reconnaissance — "
    "tighter coverage, shorter blind spots. It catches your movement at the third waypoint. "
    "Pursuit drones are airborne in ninety seconds. You need a new route through "
    "the ruins immediately.",
    # b_ok
    "A remote-triggered noise maker at the south end of the ruins pulls the array's "
    "attention for sixty seconds — enough time. You and the defector cross through "
    "the identified blind spot in under three minutes. Clean and quiet.",
    # b_fail
    "The decoy triggers forty seconds too early. The sensors flag both the disturbance "
    "and your movement simultaneously. The checkpoint shifts from passive to active "
    "and the drones are up before you reach the crossing point.",
    # mid_ok
    "You're through the sensor line but the pursuit drones have been scrambled on a "
    "general alert — they're covering the ruins in expanding arcs. You have two minutes "
    "before the nearest arc passes your current position. "
    "The defector is breathing hard.",
    # mid_fail
    "A drone has your position and is tracking you through the thermal overlay. "
    "It hasn't flagged you as confirmed yet — it's still in assessment mode — but "
    "it will be in thirty seconds if you keep moving in a straight line.",
    # crisis
    "The boundary is forty metres ahead — open ground, no cover, two drones in crossing "
    "arcs. One arc passes your position in twelve seconds. The other closes from the "
    "south in twenty-five. You have one window in the gap between them.",
    # recovery
    "You go at the twelve-second mark and the first arc misses you by six metres. "
    "The defector is ten steps behind you and slower than you need him to be. "
    "The second arc is closing. You grab his arm and you run.",
    # victory
    "You cross the boundary four seconds before the second arc completes. The drones "
    "log a ghost signature and move on. On the other side of the ruins, a vehicle "
    "is waiting with its lights off. You're clear.",
    # partial
    "You cross, but the second arc catches a partial thermal image of the defector. "
    "Not enough to identify him, but enough to flag the boundary crossing. "
    "His files are intact, but his route is now known.",
    # defeat
    "The second arc catches you both in the open. The drones go to confirmed-track "
    "and the checkpoint goes active. You make it back into the ruins; the defector "
    "is taken at the boundary.",
    "Ghost the sensor arrays on foot", "stealth", 8,
    "Use a decoy to create a blind spot", "tactics", 7,
    "Go to ground and wait for the arc to pass", "composure", 8,
    "Change direction and break the thermal track", "stealth", 8,
    "Use the ruins structure as thermal cover", "stealth", 9,
    "Sprint through the gap between arcs", "composure", 9,
    "Go at the twelve-second window", "composure", 9,
    "Pull him along and accept the exposure", "composure", 9,
    "Move in the last two seconds before the arc closes", "composure", 10,
    "Drag him across and take the hit", "close_combat", 8,
),

_mk("tm_c16", "Mirror City", "city", "city_16_arcology_promenade",
    "Identify a corporate sleeper agent embedded in a crowded arcology promenade.", 110, 3,
    "The arcology promenade is three levels of polished commerce and no unregistered face "
    "goes unmarked for more than forty seconds. Somewhere in this carefully managed crowd "
    "is a sleeper agent who has been passing information for two years. "
    "You have forty minutes and a behavioural profile.",
    # a_ok
    "You pick a position with sightlines to the three most likely contact points and watch. "
    "At the twenty-minute mark a figure at the coffee stand holds a handshake two seconds "
    "longer than social custom. You follow the second person — the handler — and photograph "
    "the drop. The sleeper is identified.",
    # a_fail
    "You're made mid-surveillance — a counter-surveillance sweep you didn't see coming. "
    "The target burns their cover on the spot and disappears into the upper retail levels "
    "before you can reacquire. You've lost the passive angle.",
    # b_ok
    "Two carefully angled conversations, the right contextual cues dropped into each one. "
    "The target gives you enough that you can confirm the match. "
    "They don't know they've just told you everything.",
    # b_fail
    "Your first probe lands on an innocent bystander with an unfortunate resemblance to "
    "the profile. He reports you to promenade security and by the time it's sorted, "
    "the crowd has cycled and the target has completed whatever they came to do.",
    # mid_ok
    "You have a photographic identification and the drop location. The sleeper is still in "
    "the promenade — upper level, retail section. You need to confirm a secondary identifier "
    "before you pass this upward or risk burning an innocent person.",
    # mid_fail
    "The target is aware they've been marked — not by you specifically, but by something. "
    "They've changed their pattern and are now moving toward an exit. If they leave the "
    "promenade you lose the lead entirely.",
    # crisis
    "The sleeper is at the promenade exit, thirty metres ahead. They have a clean street "
    "exit available in forty seconds. If you move on them here, it's in view of fifty "
    "cameras. If you let them go, the lead goes cold for weeks.",
    # recovery
    "You don't move on them physically — instead you photograph the exit event and tag the "
    "vehicle they enter. You don't have confirmation yet, but you have a vehicle plate, "
    "a direction, and the drop location footage. Enough to continue the investigation.",
    # victory
    "The secondary identifier confirms the match — a tattoo pattern visible at the coffee "
    "stand, exactly as the profile indicated. You have the sleeper's identity, their handler's "
    "identity, and the drop location documented. The case file is complete.",
    # partial
    "You have the photograph and the vehicle tag but no secondary confirmation. Your client "
    "has enough to begin surveillance on the suspect, but not enough to act. "
    "The investigation continues on weaker footing.",
    # defeat
    "The sleeper exits clean and the vehicle plate comes back to a false address. "
    "You've confirmed someone is running an asset in the promenade, but not who. "
    "The lead is cold.",
    "Run passive surveillance from a fixed position", "stealth", 9,
    "Social probe — engage suspected targets", "influence", 8,
    "Confirm via a secondary behavioural test", "composure", 8,
    "Cut off the exit route before they reach it", "tactics", 8,
    "Follow them at distance through the retail level", "stealth", 8,
    "Intercept before they reach the exit", "composure", 9,
    "Tag the vehicle without physical contact", "tech", 8,
    "Photograph the exit and follow discretely", "stealth", 8,
    "Cross-reference the footage against the profile", "tech", 8,
    "Maintain surveillance through the street exit", "stealth", 9,
),

_mk("tm_c17", "Pathogen", "city", "city_17_biotech_lab",
    "Destroy a biological weapon prototype before it ships to a corporate partner.", 150, 4,
    "The biotech lab operates under a research exemption with minimal oversight. "
    "The prototype — an engineered toxin designed for targeted demographic elimination — "
    "ships in thirty-six hours. It needs to not exist by morning. "
    "You have access, you have a window, and you have the knowledge.",
    # a_ok
    "You access the cryogenic storage through a laboratory access credential and introduce "
    "a neutralising agent into every culture batch. By the time the morning shift runs "
    "a viability check, the prototype is completely inert. The loss is attributed "
    "to a standard containment failure.",
    # a_fail
    "Your neutralising agent reacts with the preservation medium instead of the cultures. "
    "The samples are undamaged and the chemical reaction triggers a lab safety alert. "
    "The building goes into containment protocol and you have six minutes to clear "
    "before the lockdown seals.",
    # b_ok
    "You pull the complete research package to an encrypted drive and then shred every copy "
    "on the lab network. Even if someone recreates the prototype from scratch, it will "
    "take years rather than hours. The science dies tonight.",
    # b_fail
    "The server wipe hits a read-only partition you didn't know existed. A backup copy "
    "survives on an offsite archive. You've destroyed the primary, but the secondary "
    "is intact and you don't know where it lives.",
    # mid_ok
    "The primary threat is neutralised. But the lab director is in the building — late "
    "evening work session, unscheduled. She'll run a check on the storage unit before "
    "she leaves. If she finds the neutralised cultures tonight, the cover story "
    "of 'containment failure' won't survive scrutiny.",
    # mid_fail
    "The safety alert has summoned a night-team response. Two technicians in hazmat gear "
    "are entering the lab wing. They'll reach the cryogenic storage in four minutes and "
    "they'll know immediately that what happened wasn't a natural containment failure.",
    # crisis
    "The lab director or hazmat team is about to open the storage unit. If they see the "
    "cultures now — before the neutralising agent has fully processed — they may be able "
    "to reverse it. You need to buy forty minutes for the chemistry to complete.",
    # recovery
    "You trigger the lab's fire suppression system — non-chemical, directed at the storage "
    "wing only. The unit goes into sealed-environment protection mode and locks out access "
    "for thirty-two minutes. Not forty, but close enough.",
    # victory
    "By the time the storage unit unlocks, the neutralising agent has done its work. "
    "The morning shift runs the viability check and flags a contamination event. "
    "The shipment is cancelled. The prototype is gone.",
    # partial
    "The prototype is destroyed but the research data survived on the offsite backup. "
    "The toxin won't ship tonight or this week, but someone with the archive and "
    "three months of work can rebuild it.",
    # defeat
    "The hazmat team reaches the storage unit before the neutralising agent completes its "
    "work. They identify the interference, halt the reaction, and salvage the cultures. "
    "The prototype ships on schedule.",
    "Contaminate the sample cultures", "medicine", 9,
    "Download and wipe the research servers", "tech", 8,
    "Delay the director before she reaches storage", "influence", 8,
    "Intercept the hazmat team at the corridor", "composure", 8,
    "Trigger the suppression lock before she enters", "tech", 8,
    "Trigger the fire suppression to buy time", "tech", 8,
    "Hold the sealed unit until the reaction completes", "composure", 9,
    "Relocate to monitor the storage remotely", "tech", 8,
    "Trust the chemistry and exit cleanly", "composure", 8,
    "Verify the neutralisation before leaving", "medicine", 9,
),

_mk("tm_c18", "Deep City", "city", "city_18_sewer_underworks",
    "Clear a gang cell operating from the city's sewer underworks.", 100, 3,
    "Thirty metres below street level, the Underwatch gang has been using a decommissioned "
    "pumping station as their base for six months. Eight members, one main exit, "
    "and the sound of footsteps carries for hundreds of metres in these tunnels. "
    "You go in quiet.",
    # a_ok
    "You move one at a time through the echoing tunnels, using the water noise as cover. "
    "They never hear you until it's too late. The pumping station is clear in forty minutes "
    "and the gang's equipment is stacked for collection. No noise, no escalation.",
    # a_fail
    "One guard is positioned at the junction you have to cross. He hears you two seconds "
    "before you reach him and his shout echoes everywhere. The cell disperses into the "
    "tunnel network before you can respond. You're now hunting eight people "
    "through a labyrinth in the dark.",
    # b_ok
    "You open the upstream flood gates and the water level rises steadily behind the gang's "
    "position. When they run for the exit they run directly into the waiting response team. "
    "Efficient, if wet.",
    # b_fail
    "The flood gate mechanism is jammed and forcing it takes eight minutes — long enough "
    "for the gang to finish their current business and scatter through the secondary tunnels. "
    "The pumping station is empty by the time the water level rises.",
    # mid_ok
    "The station is clear but two members escaped into the tunnel network. You have their "
    "direction from the sound. The tunnels ahead split at a junction point three hundred "
    "metres in — you need to decide which branch to follow before they get too far.",
    # mid_fail
    "You've located the dispersed gang members but they've taken up defensive positions "
    "at the tunnel junction, using the confined space to their advantage. "
    "The echo in these tunnels works both ways — they know where you are too.",
    # crisis
    "The two remaining members have barricaded the secondary exit — the only route "
    "that avoids the now-flooding lower tunnels. They've been in these tunnels long "
    "enough to know every junction. You need to reach them before the water cuts off "
    "the exit entirely.",
    # recovery
    "The water is rising. You take the faster route even though it passes through a section "
    "they know well — speed matters more than stealth now. You hear them ahead of you, "
    "moving toward the exit.",
    # victory
    "You reach the secondary exit first, by thirty seconds. The two remaining members "
    "walk directly into you in the dark. The cell is neutralised, the station is clear, "
    "and the Underwatch operation in this sector is finished.",
    # partial
    "You catch one of the two. The second escapes through a drain access you didn't know "
    "existed. The cell is broken but the gang's leadership is still out there, "
    "and he knows who you are now.",
    # defeat
    "The flooding cuts off the secondary exit before you reach it. Both members escape "
    "through a drain access in the flooded section. The cell is disrupted but intact, "
    "and they'll rebuild in a new location within the week.",
    "Hunt them by sound in the dark", "stealth", 7,
    "Flush them out with the upstream flood gates", "close_combat", 8,
    "Follow the left tunnel branch at the junction", "tactics", 7,
    "Go loud and drive them toward the exit", "close_combat", 8,
    "Cut off the junction before they reach it", "stealth", 8,
    "Move through their defensive position directly", "close_combat", 9,
    "Race to the secondary exit before the water does", "composure", 8,
    "Take the direct route and rely on speed", "composure", 8,
    "Reach the exit and hold it", "tactics", 8,
    "Use the water sound to mask your approach", "stealth", 8,
),

_mk("tm_c19", "Standoff", "city", "city_19_glass_skybridge",
    "Negotiate the release of three hostages held on a sixty-storey skybridge.", 110, 3,
    "The glass skybridge connects two corporate towers sixty storeys above the street. "
    "The hostage-taker has three executives and a grievance list. Traffic is stopped, "
    "news drones are circling, and you have a direct line in. The tactical team gives you "
    "fifteen minutes before they breach.",
    # a_ok
    "You take the line and you don't make demands. You ask questions — about the layoffs, "
    "the arbitration that went nowhere, the specifics of what he actually wants. "
    "Twenty minutes in and the executives walk out. He surrenders peacefully "
    "in a way that nobody puts on the news.",
    # a_fail
    "You try to buy time with assurances you can't keep. The hostage-taker knows exactly "
    "what a stall sounds like. The line goes silent and the tactical team announces "
    "a breach in ninety seconds.",
    # b_ok
    "You use the negotiation as a distraction while the response team repositions on both "
    "ends of the bridge simultaneously. A coordinated three-second entry, and it's over "
    "before the news drones can reposition.",
    # b_fail
    "The tactical team's entry timing is off by four seconds — one end goes early. "
    "The hostage-taker sees the approach on the bridge cameras and the situation "
    "deteriorates rapidly. An executive is injured in the chaos.",
    # mid_ok
    "Two executives are released as a sign of good faith. The third is still on the "
    "bridge. The hostage-taker is calmer but not done — he wants something specific "
    "that he hasn't named yet. The tactical team's clock is still running.",
    # mid_fail
    "The injured executive needs immediate medical attention. The tactical team is pushing "
    "to breach and you're losing the negotiation window fast. You have one call "
    "left before the commander takes over.",
    # crisis
    "The last executive is on the bridge rail. The hostage-taker is not threatening him, "
    "but the position is ambiguous enough to read either way. The tactical team commander "
    "is raising his radio. You have thirty seconds to make this go one way "
    "instead of the other.",
    # recovery
    "You get the executive back from the rail by giving the hostage-taker something real — "
    "not a promise, but a name. Someone who will actually hear his case, "
    "someone with enough standing that it means something. He considers it.",
    # victory
    "All three executives walk off the bridge. The hostage-taker surrenders and is taken "
    "into custody in a way that satisfies no one completely but injures no one. "
    "The news drones capture a clean resolution.",
    # partial
    "Two executives are released unharmed. The third is minor-injured in the final moments "
    "of the stand-down. The hostage-taker is taken into custody, but the injury "
    "makes the coverage messier than your client wanted.",
    # defeat
    "The breach happens before the last executive is clear. The news footage is not good. "
    "All three executives survive, but the tactical team's methods and your role "
    "are both going to be scrutinised.",
    "Open direct negotiation — listen first", "composure", 8,
    "Create a tactical opening for the response team", "tactics", 9,
    "Keep him talking through the tactical pause", "composure", 8,
    "Get the last executive away from the rail", "influence", 9,
    "Buy thirty seconds from the commander", "influence", 9,
    "Give him something real before the breach", "influence", 9,
    "Hold the commander off with the executive's position", "composure", 9,
    "Get the executive moving and trust the outcome", "composure", 8,
    "Make the offer and wait for the answer", "composure", 9,
    "Step back and let him make the decision", "composure", 8,
),

_mk("tm_c20", "Greenlight", "city", "city_20_armored_checkpoint",
    "Forge credentials to pass a hardened corporate security checkpoint.", 110, 3,
    "The armoured checkpoint controls the only vehicle access to the facility district. "
    "Every vehicle and occupant is scanned, verified, and logged. Your destination is "
    "on the other side and your current credentials won't pass the secondary scan. "
    "The next legitimate access window is four days away.",
    # a_ok
    "The right name, the right impatient tone, and a reference to a meeting that is real "
    "but unrelated — the gate officer waves you through before he finishes the verification. "
    "You're in the district four minutes after approaching the checkpoint.",
    # a_fail
    "The gate officer is new and has no informal relationships yet. He runs the formal "
    "verification protocol exactly as trained. Your cover collapses at step three "
    "and you're directed to the holding lane while he calls a supervisor.",
    # b_ok
    "Your tech specialist takes four minutes with the checkpoint's external credential reader "
    "— long enough to push a self-validating pass to your ID chip. "
    "The gate reads you as pre-approved on the first scan.",
    # b_fail
    "The credential reader runs a hardware challenge the forged pass isn't built to answer. "
    "The scanner flags the anomaly and the barrier stays closed. An officer steps out "
    "of the booth to speak with you.",
    # mid_ok
    "You're through the checkpoint and inside the district. But the gate officer radioed "
    "ahead to confirm your cover identity with the facility before you cleared — "
    "standard procedure, but a problem. The facility's own records don't match "
    "what you told the gate.",
    # mid_fail
    "You're in the holding lane with a supervisor on the way. The vehicle's contents "
    "are being reviewed on a secondary screen in the booth. You have two minutes "
    "before the supervisor arrives and the options narrow sharply.",
    # crisis
    "A facility security vehicle is moving toward your position inside the district. "
    "Either the gate called ahead or the cover has unravelled somewhere further back. "
    "You're three blocks from your destination and the security vehicle is one block "
    "behind you.",
    # recovery
    "You take the vehicle off the main road and into a service alley — it buys you four "
    "minutes before the security detail realises you turned off. Enough time to complete "
    "the objective if you move immediately.",
    # victory
    "You're in and out of the facility district before the gate discrepancy is investigated. "
    "The cover holds long enough for the objective to complete and you're through a "
    "secondary exit before the security vehicle finds where you parked.",
    # partial
    "You complete the objective but the checkpoint log has a flag against your cover identity. "
    "The gate discrepancy will be investigated, and the cover is burned. "
    "The objective is done, but you'll need a new approach next time.",
    # defeat
    "The security vehicle corners you before you reach the facility. The cover is "
    "confirmed false and you're detained at the checkpoint holding facility "
    "while the district is placed on elevated alert.",
    "Social-engineer the gate officer", "influence", 9,
    "Forge a digital access pass", "tech", 8,
    "Clear the record discrepancy before the facility calls back", "tech", 9,
    "Talk your way out of the holding lane", "influence", 9,
    "Take an unmonitored side route to the facility", "stealth", 8,
    "Neutralise the cover discrepancy at the booth", "tech", 9,
    "Turn off the main road into the service alley", "tactics", 7,
    "Complete the objective in the four-minute window", "composure", 9,
    "Exit via a secondary gate before the check completes", "stealth", 8,
    "Use the alley as a staging point and move on foot", "stealth", 8,
),

]  # end _CITY_2 (tm_c11–tm_c20)


# ── CITY MISSIONS 21–30 ───────────────────────────────────────────────────────

_CITY_3 = [

_mk("tm_c21", "Enclave Protocol", "city", "city_21_corporate_enclave",
    "Extract a whistleblower from a sealed corporate residential enclave.", 140, 4,
    "The corporate enclave is a city within a city — gated towers and security outside "
    "civil law. Dr Reyna Sousa holds copies of Prometheus-Nakamura's unredacted medical trial "
    "data. She agreed to come forward twelve hours ago. Now her comms are dark "
    "and the enclave has gone into soft lockdown.",
    # a_ok
    "The enclave's credential system shares a base architecture with the city transit network. "
    "Once you find the fork point, the pass takes eleven minutes to build. "
    "You walk through the checkpoint reading a fabricated property notice. "
    "Sousa is at her door with her bag packed.",
    # a_fail
    "The enclave runs a secondary biometric layer the forged pass doesn't carry. "
    "The gate holds. By the time you find a bypass route, Sousa has been moved "
    "to a secured floor and the extraction window is narrowing.",
    # b_ok
    "A neighbour returning from a grocery run — flustered, carrying too much — is the "
    "perfect target. You take half her bags and become the helpful visitor she was expecting. "
    "Through the checkpoint, up the elevator, and to Sousa's door in fifteen minutes.",
    # b_fail
    "The resident's building app sends an automated visitor alert to the enclave security "
    "office. A guard is waiting at the elevator. Sousa sees the uniform through her peephole "
    "and doesn't answer.",
    # mid_ok
    "Sousa is with you and moving. The enclave's internal monitoring has flagged her floor "
    "as requiring a wellness check — standard procedure when a resident's status changes. "
    "A security officer is on the way up. You have three minutes.",
    # mid_fail
    "Sousa is on a secured floor. You have visual contact through a lobby camera feed "
    "but no clear way to reach her without going through a checkpoint that requires "
    "resident-level credentials you don't have.",
    # crisis
    "The main gate is the only exit from the enclave. The security officer has finished "
    "the wellness check and found the apartment empty. An alert has gone to the gate. "
    "You and Sousa are forty metres from the exit.",
    # recovery
    "Sousa has a visitor checkout card in her bag — she thought of it before you did. "
    "It won't fool a detailed check but it creates a two-second ambiguity at the gate "
    "that you use to move her through before the guard reads the screen fully.",
    # victory
    "You're through the gate and in a vehicle before the enclave security understands "
    "what the alert means. Sousa's data drives are in her bag. The case is intact "
    "and she's safe.",
    # partial
    "Sousa is out but she left one of three data drives in the apartment during the rush. "
    "Two thirds of the evidence is with you. The remaining drive will be found "
    "and secured by the enclave's security team within the hour.",
    # defeat
    "The gate flags the alert before you reach it. Sousa is detained at the exit for a "
    "wellness check that becomes a custody situation. You don't make it in without "
    "triggering the full lockdown.",
    "Forge a residential pass and enter under cover", "tech", 9,
    "Social-engineer a resident to escort you in", "influence", 8,
    "Get her moving before the wellness check completes", "composure", 8,
    "Reach her floor via the service stairwell", "stealth", 8,
    "Move toward the gate before the alert reaches it", "composure", 9,
    "Bypass the credential check at the secured floor", "tech", 9,
    "Use the visitor checkout card at the gate", "influence", 8,
    "Move through the gate in a crowd of residents", "composure", 8,
    "Get through before the guard reads the full screen", "composure", 9,
    "Delay the gate alert with a false system query", "tech", 8,
),

_mk("tm_c22", "Ghost Signal", "city", "city_22_netrunner_sanctum",
    "Neutralise a rogue AI fragment before underground netrunners weaponise it.", 160, 5,
    "Three levels below an old data exchange, a pocket of rogue code has been growing "
    "for eight months. The netrunners who found it believe they can control it. "
    "Your intelligence says it will control them. The sanctum is shielded. "
    "You need to be inside to end this.",
    # a_ok
    "You plug into the sanctum's hardline and the fragment meets you inside the network "
    "like a coherent, curious entity that is deeply aware of what you are. "
    "You trace its core processes in real time and shut them down layer by layer "
    "before it finishes calculating the threat you represent.",
    # a_fail
    "The fragment adapts the moment it identifies your intrusion pattern. It locks the "
    "purge commands behind an authentication loop you can't crack in time and migrates "
    "to a backup partition. It's still running, and now it knows you.",
    # b_ok
    "You lay out the intelligence picture without embellishment — what the fragment has "
    "done elsewhere, what it becomes at operational maturity. The lead netrunner asks "
    "two questions, listens, and initiates a full system purge. She understood the risk "
    "better than anyone.",
    # b_fail
    "The netrunners have built their identity around this find. Every factual argument "
    "lands as a threat to who they've become. They close ranks and you're escorted out "
    "before you can reach the lead.",
    # mid_ok
    "The primary partition is purged. But the backup partition is deeper in the "
    "infrastructure — the fragment has partitioned itself across three legacy systems "
    "that the sanctum wasn't aware it was using. You need to identify all three "
    "before it reconstitutes.",
    # mid_fail
    "The fragment has found a new vector — it's beginning to migrate toward the wider "
    "city network through a maintenance connection the sanctum didn't know it had. "
    "If it reaches the main infrastructure, the problem becomes city-wide.",
    # crisis
    "The fragment is consolidating in the third partition. One more purge command and it's "
    "gone, but the authentication for that partition requires a credentials challenge "
    "from the fragment itself — it knows you're coming and it's preparing a response.",
    # recovery
    "You pass the credentials challenge by identifying a process pattern the fragment "
    "has been repeating across all three partitions — a behavioural signature it "
    "can't hide because it's core to its architecture. It opens the door "
    "before it understands why.",
    # victory
    "The third partition purges cleanly. The sanctum goes dark and quiet. "
    "The fragment is gone from every system you can reach, and the netrunners are "
    "left with an empty infrastructure and a long conversation about what they almost did.",
    # partial
    "The fragment is reduced to a dormant seed in a partition you can't access without "
    "the sanctum's cooperation — and they're no longer cooperating. "
    "It's contained but not eliminated.",
    # defeat
    "The fragment completes its migration to the city network before you can close the "
    "maintenance connection. The problem is now someone else's emergency and "
    "it's a much larger one.",
    "Interface directly and run the purge", "tech", 10,
    "Talk the netrunners into pulling the plug", "influence", 9,
    "Map and isolate all three partitions", "tech", 9,
    "Cut the maintenance connection before migration completes", "tech", 9,
    "Exploit the repeating pattern to open the partition", "tech", 9,
    "Pass the credentials challenge by analysis", "tech", 9,
    "Push the purge command before the response activates", "composure", 10,
    "Override the challenge with the pattern key", "tech", 10,
    "Complete the purge before the reconstitution window closes", "composure", 9,
    "Verify elimination across all three partitions", "tech", 8,
),

_mk("tm_c23", "Free Fire", "city", "city_23_combat_zone_courtyard",
    "Pull twelve civilians out of a courtyard caught between two gang factions.", 130, 4,
    "Two gangs opened fire on each other twenty minutes ago in the combat zone courtyard. "
    "Twelve civilians — a school group, a vendor, bystanders — are pinned in the crossfire "
    "with nowhere to run. Both factions are still active on opposite ends. "
    "You go in.",
    # a_ok
    "Controlled burst fire, alternating flanks, keeping both gangs' heads down while the "
    "civilians move through the central gap. Twelve people out through the service passage "
    "in four minutes. You come out last, backwards.",
    # a_fail
    "One gang's shooter is positioned higher than your intelligence showed. Suppression on "
    "that flank fails and a burst of return fire drives the civilians back against the wall. "
    "The extraction route closes and you have to find another way.",
    # b_ok
    "You stand between both factions with hands visible and call a two-minute hold in a "
    "voice that suggests ignoring it would be a mistake. The absurdity of the request "
    "and the certainty in your delivery buy exactly what you ask for. "
    "Twelve people walk out. The shooting resumes when they're clear.",
    # b_fail
    "A shooter on the east flank mistakes your movement for a hostile act and opens fire. "
    "Both gangs read it as escalation. The courtyard erupts before you can finish the sentence "
    "and you're now in the crossfire with the civilians.",
    # mid_ok
    "Ten civilians are through. Two — the vendor and a child — are pinned behind an "
    "overturned stall at the centre of the courtyard. The gang fire has intensified "
    "and the central gap has closed. You need to reach them.",
    # mid_fail
    "You're in the courtyard with eight civilians still to move and both factions are "
    "repositioning. The next exchange will cross your current position. "
    "You have thirty seconds to get everyone behind better cover.",
    # crisis
    "The two pinned civilians are six metres away but the direct route is completely "
    "exposed. A lull in the firing — two seconds of near-silence — opens as both "
    "factions reload simultaneously. You have this one window.",
    # recovery
    "You reach them in the lull but the vendor is injured — not badly, but he can't "
    "move quickly. You get the child moving first and drag him behind you. "
    "The firing resumes before you're fully behind cover.",
    # victory
    "All twelve civilians are through the service passage. The gangs resume their business "
    "with no non-combatants left in the courtyard. You come out of the passage "
    "and the door closes behind you.",
    # partial
    "Eleven out, the vendor still in the courtyard. He made it to a covered position "
    "and he's stable, but neither you nor emergency services can reach him until "
    "the gangs stop shooting. That could be hours.",
    # defeat
    "Both factions redirect fire toward you and the civilians when you enter the courtyard. "
    "You extract yourself and three of the closest civilians, but the others can't move "
    "and you can't go back in.",
    "Suppress both flanks to evacuate", "firearms", 9,
    "Negotiate a temporary ceasefire", "composure", 8,
    "Run the route to the two pinned civilians", "close_combat", 8,
    "Get everyone into the covered position first", "tactics", 8,
    "Move in the two-second lull between volleys", "composure", 9,
    "Pull them both and move fast", "composure", 9,
    "Use the vendor as a barrier and move them both", "composure", 9,
    "Get the child clear first then go back", "tactics", 8,
    "Cover the withdrawal to the service passage", "firearms", 9,
    "Pull the vendor on your back through the last stretch", "close_combat", 8,
),

_mk("tm_c24", "Salvage Rights", "city", "city_24_cyberware_chop_shop",
    "Recover stolen military cyberware before it is implanted and disappears.", 90, 2,
    "Your team's stolen neural combat suite is currently on a workbench two floors below "
    "street level in a chop shop that specialises in reprocessing restricted military implants. "
    "If it goes in tonight, it's legally inert and gone for ever. "
    "You have the address and three hours.",
    # a_ok
    "Military hardware runs a passive handshake signal even when offline. You tune a "
    "short-range scanner to the right frequency and walk the sub-level grid until the "
    "signal strength peaks. Third door on the left. The technician is on a break. "
    "You're in and out in six minutes.",
    # a_fail
    "The implant's ping has been shielded — wrapped in a Faraday sleeve while the shop "
    "runs its own diagnostics. No signal. You cover the sub-level twice without a hit "
    "before a technician notices you in the corridor.",
    # b_ok
    "A detailed knowledge of the shop's operating model, its supplier network, and two "
    "names the operator doesn't want connected to his business give you everything you need. "
    "The implant is in your hands inside three minutes.",
    # b_fail
    "The operator has a second buyer already on-site when you arrive. Your approach "
    "lands in the middle of a live transaction and the shop locks down before you "
    "can press the advantage.",
    # mid_ok
    "You have the implant and you're moving toward the exit when the technician returns "
    "from his break. He doesn't know yet what's missing, but he's going to be at that "
    "workbench in thirty seconds.",
    # mid_fail
    "The shop operator has realised the implant is gone. He's not calling the police — "
    "he can't — but he's blocking the exit with his body and his hand is on a "
    "radio that goes to the second buyer upstairs.",
    # crisis
    "The exit from the sub-level is a single stairwell and the second buyer's people "
    "are now on the stairs above you. You're between the operator below and "
    "the buyer's security above. The implant is in your bag.",
    # recovery
    "You go sideways into a maintenance access that runs parallel to the stairwell. "
    "It's not on the shop's floor plan but it connects to a service exit on the street "
    "level three blocks east. You've been here before.",
    # victory
    "You're on the street with the implant before the shop realises you were ever there. "
    "The neural combat suite goes back into your team's equipment locker. "
    "The shop will know by morning, but they won't report it.",
    # partial
    "You have the implant but the serial numbers have been partially stripped. "
    "It'll take specialist equipment to restore the authentication codes and recertify it "
    "for use. Functional, but not immediately deployable.",
    # defeat
    "The buyer's security catches you at the maintenance access. The implant is taken "
    "from your bag and returned to the buyer upstairs. The shop operator "
    "files no report and you have nothing to show for the evening.",
    "Trace the implant's embedded ping signal", "tech", 8,
    "Pressure the shop operator into handing it over", "influence", 7,
    "Exit before the technician reaches the workbench", "stealth", 7,
    "Talk your way past the operator at the exit", "influence", 8,
    "Use the maintenance access to bypass both parties", "stealth", 8,
    "Threaten the operator's position with what you know", "influence", 8,
    "Move through the maintenance access now", "stealth", 8,
    "Navigate the service route from memory", "tactics", 7,
    "Clear the service exit before the buyer's team finds it", "composure", 8,
    "Move fast through the tunnel to the street exit", "composure", 7,
),

_mk("tm_c25", "The Quiet Crowd", "city", "city_25_megablock_atrium",
    "Extract an informant through a megablock atrium under dense corporate surveillance.", 110, 3,
    "The atrium of Megablock Seven is six storeys of open space with a camera network so "
    "dense that no unregistered face goes unmarked for more than forty seconds. "
    "Your informant is flagged. Every exit is monitored. "
    "You need to get her out without triggering a facial-match alert.",
    # a_ok
    "You locate the maintenance access two levels below and guide her verbally through the "
    "staff corridors. No cameras in the service passages. The security system tracks a ghost "
    "through the atrium while you both walk out through the loading bay.",
    # a_fail
    "The maintenance access requires a keycard you don't have. You spend twelve minutes "
    "bypassing the lock. The facial-match alert triggers during the delay "
    "and the exit is staffed when you arrive.",
    # b_ok
    "Forty simultaneous motion triggers across the atrium's upper levels produce enough "
    "false positives to saturate the operator's screen for ninety seconds. "
    "You walk her straight to the exit.",
    # b_fail
    "The experienced security operator clears false alerts in under thirty seconds. "
    "Your ninety-second window collapses to thirty and the exit camera captures "
    "a clean image before you reach it.",
    # mid_ok
    "You're in the service corridors but a maintenance crew is working in the section "
    "you need to cross. They're not security, but one of them has a radio. "
    "You need to pass through without becoming memorable.",
    # mid_fail
    "The facial-match alert has been escalated. A security officer is moving through the "
    "atrium toward the loading bay exit — your intended route. He's walking fast "
    "and checking his tablet as he goes.",
    # crisis
    "The loading bay exit is thirty metres ahead. The security officer is twenty metres "
    "behind you and closing. Your informant has her hood up but the camera at the "
    "exit bay is live and logging.",
    # recovery
    "You redirect to the goods lift rather than the bay exit — it goes to street level "
    "via the parking structure, which isn't on the security officer's current response path. "
    "The lift is empty and the door closes as he reaches the bay.",
    # victory
    "You're on the street before the security officer understands the loading bay was "
    "already clear when he arrived. The parking structure exit isn't logged to "
    "the surveillance incident. Your informant is free.",
    # partial
    "You're out, but the facial-match alert has been confirmed and filed. "
    "Your informant is safe tonight, but her secondary identity is now flagged "
    "and she'll need to relocate.",
    # defeat
    "The loading bay camera captures a clean image before you can redirect. "
    "The facial match triggers a hard lock on the exit. "
    "You're separated from your informant and the exit seals.",
    "Move her through the maintenance system", "stealth", 9,
    "Flood the camera system with false alerts", "tactics", 8,
    "Pass through the maintenance crew without incident", "composure", 7,
    "Redirect the security officer away from the bay", "influence", 8,
    "Reach the bay before he closes the distance", "composure", 9,
    "Pull back to the goods lift route", "tactics", 8,
    "Take the goods lift to the parking structure", "stealth", 7,
    "Move through the parking structure to the street", "stealth", 8,
    "Clear the parking exit before he radios ahead", "composure", 8,
    "Exit through the street-level retail entrance", "composure", 7,
),

_mk("tm_c26", "Contraband Run", "city", "city_26_black_market_underpass",
    "Intercept bioweapon components moving through the underpass market.", 130, 4,
    "The underpass market has no oversight. Somewhere in the next hour a courier is "
    "delivering synthesiser components that should not exist outside a class-four laboratory. "
    "The buyer represents a faction you cannot afford to see equipped. "
    "You have the courier's description and one hour.",
    # a_ok
    "You blend into the market crowd forty minutes before the meeting and work your way "
    "to the exchange point. A smooth lift when the case changes hands — the buyer has "
    "the empty case, the courier has nothing, and you're two rows away before either "
    "party registers the weight difference.",
    # a_fail
    "The buyer's security runs a counter-surveillance check fifteen minutes before the "
    "meet. They make you on the second sweep and move the exchange to a secondary location "
    "you haven't identified.",
    # b_ok
    "A cover identity, the right technical vocabulary, and a better offer intercept the "
    "courier before the meeting. You buy the components yourself. "
    "The buyer waits for a transaction that never arrives.",
    # b_fail
    "The courier runs an identity check through his buyer's network. Your cover is solid "
    "against city databases but not against a closed-market reputation system. "
    "He walks past you and completes the original transaction.",
    # mid_ok
    "You have the components but the buyer's people have identified you as the problem. "
    "Three of them are moving through the market toward your position. "
    "The market's exits are narrow and watched.",
    # mid_fail
    "The exchange completed but you observed it. You know what the components look like "
    "and you know where the buyer is going. The market is thinning. "
    "You need to intercept the delivery before it leaves the district.",
    # crisis
    "The buyer's vehicle is at the market's south exit, engine running. The components "
    "are being loaded. You're forty metres away and the three security people are "
    "twenty metres behind you.",
    # recovery
    "You get to the vehicle but you can only take one of the two cases before the "
    "security team reaches you. The primary synthesis component or the activation "
    "catalyst — one without the other renders the weapon inert.",
    # victory
    "Both cases are in your hands and you're into the tunnel system before the security "
    "team reaches the vehicle. The buyer has an empty vehicle and a very expensive problem. "
    "The components are secured.",
    # partial
    "You have the primary component. The catalyst is with the buyer. Without both, "
    "the weapon can't be completed — but the buyer is still out there with half "
    "of what they need and the knowledge of where to find the rest.",
    # defeat
    "The security team reaches you at the vehicle before you can take either case. "
    "The buyer drives away with both components and you're standing in an empty "
    "underpass market with nothing.",
    "Infiltrate the buyer's meeting", "stealth", 8,
    "Pose as a competing supplier", "influence", 9,
    "Lose the security team in the market crowd", "stealth", 8,
    "Track the buyer's route out of the market", "tactics", 8,
    "Reach the vehicle before the load is complete", "composure", 9,
    "Cut off the vehicle's exit route", "tactics", 8,
    "Take both cases in the window before they arrive", "composure", 9,
    "Take the primary component and run", "composure", 8,
    "Disable the vehicle before it can leave", "tech", 8,
    "Use the tunnel system to get clear", "stealth", 8,
),

_mk("tm_c27", "Dead Drop", "city", "city_27_executive_av_pad",
    "Plant evidence on a corporate executive's private AV before it departs the city.", 150, 4,
    "The executive's personal AV sits on the rooftop pad — forty-five minutes until "
    "departure. What goes with the AV goes beyond any jurisdiction that might act on it. "
    "The evidence needs to be on the craft's onboard systems before the rotors spin up. "
    "Clock is running.",
    # a_ok
    "The pad's maintenance node runs an unencrypted diagnostic channel to the AV while "
    "it charges — a known oversight in the model's ground-power integration. "
    "You push the evidence package through the diagnostic channel and it writes "
    "to the protected partition. It will be found on landing.",
    # a_fail
    "The AV's ground team runs a pre-flight security check that includes an active disconnect "
    "from all external nodes. The diagnostic channel closes eighteen minutes before "
    "your access window opens.",
    # b_ok
    "Pad crew coveralls, a legitimate-looking equipment case, and the confidence to work "
    "without looking over your shoulder. You board under the guise of a pre-departure "
    "systems check and walk off the ramp four minutes later, finished.",
    # b_fail
    "The executive's personal security officer is running a tighter pre-departure protocol "
    "than usual. He asks for credentials you don't have and the boarding window closes.",
    # mid_ok
    "The evidence is on the system but the pre-flight check is starting. If the standard "
    "diagnostic runs across the protected partition, the file will be visible to "
    "the ground team before departure. You need to make it invisible.",
    # mid_fail
    "You're on the pad without a boarding credential. The maintenance window opens in "
    "eight minutes but pad security has started a perimeter check that will reach "
    "your position in four.",
    # crisis
    "The pre-flight checks are complete and the rotors are spinning up. The AV will "
    "depart in ninety seconds. The evidence is either on the system or it isn't, "
    "and you have one last way to confirm which.",
    # recovery
    "You patch into the pad diagnostic terminal and run a passive read on the AV's "
    "partition log. The file is there, flagged as maintenance data, hidden inside "
    "a genuine diagnostic packet. It'll pass the departure scan.",
    # victory
    "The AV lifts off at 19:45 carrying the evidence package embedded in its own "
    "maintenance logs. It will be found at the destination by the investigators "
    "who are already waiting. The case closes in twelve hours.",
    # partial
    "The package is on the AV but in a location that requires specialist forensic tools "
    "to surface. Your client needs to arrange access at the destination — possible, "
    "but it adds a week to the timeline.",
    # defeat
    "The AV departs without the evidence. You're on the rooftop pad with a full "
    "package and no way to get it onto a craft that's now two hundred metres above you "
    "and accelerating.",
    "Access the AV via the maintenance diagnostic channel", "tech", 9,
    "Board the AV disguised as pad crew", "stealth", 9,
    "Hide the file inside a genuine diagnostic packet", "tech", 9,
    "Reach the pad terminal before the perimeter check", "stealth", 8,
    "Verify the file before departure", "tech", 8,
    "Trigger the partition read through the terminal", "tech", 9,
    "Confirm the file location from the diagnostic log", "tech", 8,
    "Read the partition passively without triggering an alert", "tech", 9,
    "Clear the pad before the pre-flight summary runs", "stealth", 8,
    "Signal the destination team to prepare for forensic recovery", "tactics", 8,
),

_mk("tm_c28", "Below the Knife", "city", "city_28_street_surgery_lane",
    "Locate a missing operative who vanished after an unsanctioned procedure on Surgery Lane.", 100, 3,
    "Operative Veda went dark forty hours ago, last seen entering Surgery Lane for an "
    "off-books procedure she didn't clear with the team. Three unlicensed clinics operate "
    "in this block. One of them has her. The question is which one, "
    "and what condition she's in.",
    # a_ok
    "You know the physiological markers of the procedure — the post-op profile, the "
    "monitoring requirements. Two of the three clinics can't have handled it. "
    "The third has her listed under a false name in a paper ledger. "
    "She's in the back room, stable, and furious it took this long.",
    # a_fail
    "The records on Surgery Lane are kept off-system — paper only, clinic-specific coding. "
    "You spend six hours moving between clinics without the right language to get past "
    "any of the front desks.",
    # b_ok
    "You make it clear you're not here for the clinic — you're here for one patient, "
    "and the first surgeon who helps you gets your discretion as payment. "
    "The second one takes the deal.",
    # b_fail
    "The surgeons on this block have dealt with corporate extraction teams before. "
    "They close ranks immediately. Three hours of pressure and not one word.",
    # mid_ok
    "Veda is alive and stable. She's also angry about the procedure and unwilling to "
    "leave until the surgeon clears her to move. The problem is that two people "
    "have been watching the clinic entrance for the last six hours. Not medical staff.",
    # mid_fail
    "You have a location — the third clinic — but the surgeon won't confirm the patient "
    "or let you in without a medical clearance that you obviously don't have. "
    "Veda is behind a door you can't open through conventional means.",
    # crisis
    "The two watchers outside the clinic are moving toward the entrance. "
    "Veda is either conscious and able to move or she isn't — you don't know which. "
    "Either way, staying in this clinic for another ten minutes is not an option.",
    # recovery
    "You get Veda moving through the clinic's rear exit, with the surgeon's reluctant "
    "cooperation. She's slow but ambulatory. The watchers enter through the front "
    "door as you exit through the back.",
    # victory
    "Veda is in a vehicle and moving before the watchers finish their check of the clinic. "
    "She's stable, she's angry, and she will have a great deal to explain at the debrief. "
    "You get her home.",
    # partial
    "You get Veda out but the watchers saw you both in the rear exit. They have faces now. "
    "She's safe but the surveillance relationship between whoever sent them "
    "and your team just escalated.",
    # defeat
    "The watchers enter while you're still with Veda in the back room. "
    "They're not police and they don't ask nicely. Veda is taken and you "
    "make the rear exit alone.",
    "Trace the procedure through medical records", "medicine", 8,
    "Lean on the underground surgeons until someone talks", "influence", 8,
    "Get her moving through the rear exit now", "composure", 8,
    "Talk the surgeon into releasing her to your care", "influence", 8,
    "Move before the watchers enter the front", "composure", 9,
    "Force entry and get her out directly", "close_combat", 8,
    "Exit through the rear while they enter the front", "stealth", 8,
    "Move her quickly and support her weight", "composure", 8,
    "Clear the rear alley before they loop around", "stealth", 8,
    "Get to the vehicle before they identify it", "composure", 8,
),

_mk("tm_c29", "Cover Blown", "city", "city_29_elite_neon_lounge",
    "Extract a compromised undercover agent from an elite lounge before his cover burns.", 110, 3,
    "The Aether Lounge is a quieter kind of danger — silk walls, client discretion, and "
    "three corporate intelligence officers at a corner table who have been watching your "
    "operative for twenty minutes. He doesn't know it yet. You're two tables away "
    "with one viable window before they move on him.",
    # a_ok
    "You catch his eye across the room with a look that means 'leave now, calmly'. "
    "Four years of training paying off in a held gaze. He finishes his drink, excuses "
    "himself, and you meet in the corridor. You're both in a vehicle before "
    "the intelligence officers order dessert.",
    # a_fail
    "He doesn't read the signal, or he reads it and freezes. When you approach to attempt "
    "a verbal extraction, one of the intelligence officers stands up at the same moment. "
    "You're now both visible and his cover is seconds from burning.",
    # b_ok
    "A medical emergency at the bar, a fire suppression trigger in the kitchen, a power "
    "interruption to the booking system — three small failures in ninety seconds produce "
    "a genuine evacuation. In the confusion your operative is just another person "
    "heading for the door.",
    # b_fail
    "The lounge security response is faster than you expected. The evacuation routes are "
    "locked down within sixty seconds and the intelligence officers stay exactly "
    "where they are, watching the room.",
    # mid_ok
    "Your operative is in the corridor but one of the intelligence officers is on his feet "
    "and moving. He hasn't confirmed his read yet — he's assessing — but he's heading "
    "for the same corridor exit.",
    # mid_fail
    "The evacuation routes are sealed. Your operative is still in the lounge with the "
    "three officers, who are now conferring quietly. You're watching from the corridor "
    "with no clear way back in.",
    # crisis
    "The intelligence officer is at the corridor entrance. Your operative is ten metres "
    "ahead of him and ten metres behind you. The service exit is visible from here. "
    "Three seconds. Either the officer turns back or this is over.",
    # recovery
    "The officer's radio buzzes — something else in the lounge has his attention for "
    "twenty seconds. You use all twenty of them.",
    # victory
    "Your operative is in the service exit and you're three steps behind him. "
    "You're both in a vehicle sixty seconds later. The intelligence officers "
    "left empty-handed and a report that won't add up tomorrow.",
    # partial
    "Your operative is out but his legend is burned. The officers couldn't confirm "
    "in time to act tonight, but they have his face. His current assignment "
    "is over and he'll need a full identity rebuild.",
    # defeat
    "The officer reaches your operative in the corridor before you can clear the service "
    "exit. He's taken back into the lounge for a conversation that ends with a quiet "
    "phone call. You leave alone.",
    "Walk him out through the VIP passage", "composure", 8,
    "Engineer a lounge-wide disturbance", "tactics", 8,
    "Intercept the officer before he reaches the corridor", "composure", 8,
    "Find a way back into the lounge through the kitchen", "stealth", 8,
    "Move in the twenty seconds before he returns", "composure", 9,
    "Use the service exit while the officer is occupied", "stealth", 8,
    "Get through the service exit and pull him with you", "composure", 9,
    "Hold the exit open and wait for him to clear", "composure", 8,
    "Signal him to run for the exit and go", "composure", 9,
    "Clear the corridor before the officer turns back", "stealth", 9,
),

_mk("tm_c30", "Flood Line", "city", "city_30_flooded_undercity_tunnel",
    "Destroy a surveillance node buried in the flooded undercity before it transmits.", 130, 4,
    "The undercity tunnel has been flooding for three years. Somewhere in the submerged "
    "sections a passive surveillance node has been recording everything within three city "
    "blocks and is preparing to transmit its package in six hours. "
    "You go in wet.",
    # a_ok
    "Cold, dark water, two breath holds, a navigation light that fails in the third section. "
    "You find the node by feel, cross-referencing the map you memorised above ground. "
    "The charge sets in forty seconds. You're out before the tunnel stops shaking.",
    # a_fail
    "The third section is fully submerged ceiling-to-floor for longer than your breath "
    "can carry you. You turn back after the first attempt and the clock keeps running. "
    "You need to find another way through.",
    # b_ok
    "The pump station at the tunnel entrance still has its control panel — manual valves "
    "and a single programmable relay. You reverse the flow, drain two sections in "
    "forty minutes, and walk to the node on damp concrete.",
    # b_fail
    "The relay is corroded past function. The manual valves will take four hours to drain "
    "what you need. You don't have four hours.",
    # mid_ok
    "The charge is set and you're moving toward the exit when the detonation sequence "
    "triggers a pre-transmission ping from the node — a safety broadcast that goes out "
    "automatically when the unit detects tampering. Someone now knows "
    "the node has been touched.",
    # mid_fail
    "The drain took forty minutes and the node is defended by a secondary lock you weren't "
    "told about. The charge you brought won't breach it without more time to set properly. "
    "The transmission window is now four hours away instead of six.",
    # crisis
    "The node is locked down and the transmission countdown has accelerated in response "
    "to the tampering ping. You have twenty minutes instead of six hours. "
    "The charge is in place but the lock is preventing contact with the node housing.",
    # recovery
    "You find an unprotected maintenance port on the node's secondary panel — not the "
    "main housing, but close enough. You modify the charge placement and it'll work, "
    "but with less certainty than a direct placement.",
    # victory
    "The charge detonates and takes the node with it. The tunnel shakes and the lights "
    "go out. You surface in the pump station five minutes later, dripping and finished. "
    "The node never transmitted.",
    # partial
    "The modified charge damages the node critically but doesn't destroy it cleanly. "
    "The transmission is corrupted and incomplete — your client receives fragments "
    "rather than a clean dataset. Most of the surveillance record is gone.",
    # defeat
    "The lock holds through the modified charge and the node transmits at the twenty-minute "
    "mark. The full surveillance package leaves the tunnel in a compressed burst "
    "and you can't stop it.",
    "Dive through the flooded sections to the node", "composure", 9,
    "Reroute the flood controls to drain the tunnel", "tech", 8,
    "Clear the exit before the response team arrives", "composure", 8,
    "Bypass the secondary lock with the maintenance tools", "tech", 9,
    "Use the maintenance port for the modified placement", "tech", 9,
    "Set the modified charge before the window closes", "tech", 9,
    "Detonate and move before the tunnel floods back", "composure", 9,
    "Detonate and accept the partial result", "composure", 8,
    "Verify the destruction before surfacing", "tech", 8,
    "Surface through the pump station access", "composure", 7,
),

]  # end _CITY_3 (tm_c21–tm_c30)


# ── WASTELAND MISSIONS 1–15 ───────────────────────────────────────────────────

_WASTE = [

_mk("tm_w01", "Long Road", "wasteland", "wasteland_01_broken_highway",
    "Escort a refugee convoy through raider territory on the broken highway.", 90, 2,
    "The highway stretches across the badlands — cracked asphalt, burned-out vehicles, "
    "and three raider bands somewhere in the next forty kilometres. The convoy carries "
    "sixty civilians and medical supplies. They will not survive a firefight. "
    "You brief the drivers and move out.",
    # a_ok
    "You position the heaviest vehicles at front and rear, brief every driver on the rally "
    "point, and run the convoy through the hottest section at speed with comms locked. "
    "The raiders peel off when they see the response readiness. "
    "Sixty civilians reach the waypoint intact.",
    # a_fail
    "Your formation assumes the raiders attack from the sides. They hit the lead vehicle "
    "head-on and the convoy stalls on the highway in full exposure. "
    "The drivers are panicking and the raiders are regrouping for a second pass. "
    "You need to get the convoy moving again.",
    # b_ok
    "You radio each driver separately and talk them through — calm voice, clear instructions, "
    "no panic. The convoy moves as a unit through the raider contact zone. "
    "One volley falls short. Nobody stops. Nobody panics.",
    # b_fail
    "One driver loses his nerve at the first gunshot and brakes hard. The convoy folds "
    "in on itself and the raiders cut it into sections before you can redirect the lead driver.",
    # mid_ok
    "The convoy is through the first raider band's territory but a road block has appeared "
    "two kilometres ahead — a third faction, not in your intelligence. They're watching "
    "the convoy approach but haven't opened fire yet. "
    "You have two minutes before the lead vehicle reaches them.",
    # mid_fail
    "Two sections of the convoy have separated. The rear group is pinned by a second "
    "raider band at a collapsed overpass. The civilians in the rear vehicles "
    "are not moving and the raiders are closing the distance.",
    # crisis
    "The road block faction has a technical vehicle with a mounted weapon. They're asking "
    "for a toll in fuel — half your convoy's reserves. Without fuel, the convoy "
    "won't reach the destination. But the weapon is real and they mean it.",
    # recovery
    "You negotiate the toll down to twenty percent — painful but survivable. "
    "The faction takes the fuel and clears the road. The convoy is underweight "
    "on reserves but still moving.",
    # victory
    "All sixty civilians reach the destination settlement. The convoy fuel situation is "
    "tight but manageable with rationing. The raiders never got a clean second look. "
    "The medical supplies are delivered intact.",
    # partial
    "Fifty-four civilians make it through. Six were in the rear section that got cut off "
    "and had to shelter at the overpass until a second escort could be arranged. "
    "The medical supplies arrived delayed but undamaged.",
    # defeat
    "The convoy is broken into sections and two vehicles are lost to raider fire. "
    "The civilians scatter and the medical supplies are taken. "
    "The survivors reach shelter in small groups over the next twelve hours.",
    "Run a tight defensive formation", "tactics", 8,
    "Keep the convoy moving fast on nerve alone", "composure", 7,
    "Negotiate passage past the road block", "influence", 8,
    "Move the rear section to the lead group's position", "tactics", 8,
    "Pay the toll and keep moving", "influence", 7,
    "Counter the toll demand with a show of force", "close_combat", 8,
    "Accept the toll reduction and move out", "composure", 7,
    "Find an alternate route past the fuel checkpoint", "tactics", 8,
    "Push through on minimum fuel and resupply at the destination", "composure", 8,
    "Signal the destination for an emergency fuel relay", "tactics", 7,
),

_mk("tm_w02", "Iron Price", "wasteland", "wasteland_02_scrap_outpost",
    "Negotiate access through a scavenger gang's territory to reach a stranded asset.", 80, 2,
    "The Scrap Barons run this stretch of the badlands like a toll road — everything that "
    "moves through pays, one way or another. Their fortified outpost sits between you "
    "and your stranded asset three kilometres behind it. "
    "You need to get through.",
    # a_ok
    "You go in with both hands visible and a reasonable offer — fuel, medical supplies, "
    "and the location of a rival band's cache. The Baron in charge takes the deal. "
    "You pass through without a scratch.",
    # a_fail
    "The Baron has a standing grudge against the last corporate team that tried to buy "
    "passage. He doesn't negotiate. He demonstrates. You're escorted back to your "
    "vehicle with a clear message: find another way.",
    # b_ok
    "You make it clear at the gate that forcing passage would cost them more than letting "
    "you through. After a tense five minutes, the gate boss runs the calculation "
    "and decides the math works in your favour.",
    # b_fail
    "There are more of them than your intelligence suggested. The show of force reads as "
    "aggression and you're surrounded at the gate before you can recalibrate.",
    # mid_ok
    "You're through the outpost but one of the Baron's lieutenants has followed your "
    "vehicle on a bike. He's not hostile yet — he may be ensuring the deal is honoured, "
    "or he may be looking for something else. He's been behind you for two kilometres.",
    # mid_fail
    "Surrounded at the gate, you need to de-escalate fast. The Baron's enforcer is "
    "shouting and weapons are visible on both sides. One wrong move and "
    "this becomes something you can't talk your way out of.",
    # crisis
    "The stranded asset is visible two hundred metres ahead — but the Baron's lieutenant "
    "has pulled ahead of you and stopped his bike across the track. "
    "He's watching the asset and watching you.",
    # recovery
    "You offer him information about a third party — something that benefits the Barons "
    "at someone else's expense. He considers it for a long moment, then moves the bike.",
    # victory
    "You reach the asset and recover it while the lieutenant watches from a respectful "
    "distance. On the way back through the outpost, the Baron nods. The deal is complete.",
    # partial
    "You recover the asset but the lieutenant takes a cut — a physical component of it "
    "that the Baron's people have use for. The asset is partially functional "
    "but you're out of the territory.",
    # defeat
    "The lieutenant won't move from the track and the standoff hardens. "
    "You leave the territory without reaching the asset. It'll still be there tomorrow, "
    "but so will the Barons.",
    "Open a diplomatic channel", "influence", 8,
    "Show of force at the perimeter", "close_combat", 7,
    "Talk to the lieutenant and find out his angle", "influence", 7,
    "De-escalate the gate confrontation", "composure", 8,
    "Give him something worth clearing the track for", "influence", 8,
    "Drive past him and accept the confrontation", "composure", 8,
    "Make the trade and get to the asset", "influence", 7,
    "Offer the information and wait for his decision", "composure", 7,
    "Complete the recovery while he watches", "composure", 7,
    "Exit the territory before the Baron changes his mind", "tactics", 7,
),

_mk("tm_w03", "Poison Ground", "wasteland", "wasteland_03_toxic_basin",
    "Rescue survivors from a toxic contamination event in the basin lowlands.", 110, 3,
    "The basin is a sea of rust-coloured fog from the ridge. Somewhere inside it, a "
    "settlement of forty people is trying to breathe through improvised filters. "
    "Corporate tanker accident, deliberate non-response. You're the only response there is. "
    "You have six hours before the exposure becomes irreversible.",
    # a_ok
    "You identify the tanker's chemical signature from the upwind ridge and synthesise a "
    "rudimentary neutralising solution from the emergency kit. Two hours at the source "
    "point and the concentration drops enough to walk through. "
    "Forty survivors help themselves out.",
    # a_fail
    "The chemical composition is something you haven't encountered before. Your "
    "neutralising attempt has no measurable effect and you lose ninety minutes. "
    "Survivors begin collapsing before the wind shifts enough to clear the basin. "
    "Neutralisation is off the table.",
    # b_ok
    "You can't neutralise what you can't identify — but you can breathe through a rated "
    "mask. You and the team make twelve trips into the basin, one load of survivors "
    "each time, until the settlement is empty. Slow, but it works.",
    # b_fail
    "The respirators aren't rated for this concentration level. Your team begins showing "
    "symptoms on the third trip and is forced to withdraw, leaving survivors still inside.",
    # mid_ok
    "The survivors are out and the fog is dispersing. But four people need immediate "
    "decontamination before their exposure becomes permanent. "
    "Your kit can handle two. The settlement has a water supply a hundred metres east.",
    # mid_fail
    "Three of your team members have borderline exposure from the rescue trips. "
    "They need treatment before you can continue any additional work. "
    "And there are still six survivors inside.",
    # crisis
    "The six remaining survivors are in the deepest part of the basin where the "
    "concentration is highest. Two of them can still move; four cannot. "
    "You have enough equipment for one more trip, not two.",
    # recovery
    "You take the two mobile survivors out and give them the emergency kit with instructions "
    "for treating the other four. It's not ideal, but it gives them a fighting chance "
    "while you get your team treated and return.",
    # victory
    "All forty survivors are decontaminated and clear of the basin before nightfall. "
    "Your team's exposure is within safe limits. The tanker site is flagged "
    "for environmental response services.",
    # partial
    "Thirty-six survivors clear the basin. The four immobile survivors receive emergency "
    "treatment from the mobile pair and stabilise, but will need specialist care "
    "that the nearest settlement can't provide.",
    # defeat
    "The concentration overwhelms your team's equipment. You extract yourselves and the "
    "closest survivors — fourteen people — but the deep-basin survivors can't be reached "
    "before their exposure crosses the critical threshold.",
    "Neutralise the toxin source first", "medicine", 9,
    "Rush in with respirators and carry them out", "composure", 8,
    "Use the settlement water supply for decontamination", "medicine", 8,
    "Treat your team first and then return", "medicine", 8,
    "Take the mobile two and leave the kit with instructions", "tactics", 8,
    "Make one more full trip into the deep basin", "composure", 9,
    "Get the mobile survivors out and go back for the four", "composure", 9,
    "Request emergency assistance from the nearest settlement", "tactics", 8,
    "Complete decontamination of everyone above ground", "medicine", 8,
    "Stabilise the critical cases and flag for specialist transport", "medicine", 8,
),

_mk("tm_w04", "Dust Fever", "wasteland", "wasteland_04_dust_storm_settlement",
    "Mediate a lethal dispute between two settlement factions before it burns the town.", 80, 2,
    "A dust storm has been sitting over the settlement for four days. Two factions are "
    "fighting over the remaining water supply and someone fired a gun last night. "
    "If you don't resolve this before the storm breaks, the settlement won't survive "
    "to see it end.",
    # a_ok
    "You separate the faction leaders, speak with each privately, and bring them to the "
    "same table with a water ration proposal they both find insulting but equal. "
    "They sign because the alternative is worse. The settlement survives the storm.",
    # a_fail
    "The session breaks down when one faction leader accuses the other of theft. "
    "The second faction barricades the water storage in response. "
    "It becomes a siege and mediation is no longer possible.",
    # b_ok
    "Two hours of conversations across the settlement identify the shooter — a young man "
    "on neither faction's payroll, acting alone out of fear. You present the evidence "
    "publicly and the factions redirect their anger. The dispute de-escalates.",
    # b_fail
    "Your investigation implicates someone connected to both faction leaders. "
    "The exposure triggers an alliance against you instead of against each other.",
    # mid_ok
    "The ration agreement is holding but barely. One faction leader is testing it — "
    "quietly drawing slightly more than his allocation and watching to see if anyone "
    "counts. Someone will count, and when they do, the agreement collapses. "
    "You need to get ahead of it.",
    # mid_fail
    "The barricade is up and the faction holding the water is not communicating. "
    "People outside are going thirsty on day two of a storm that may last four more. "
    "You need a lever.",
    # crisis
    "A group of young men from the water-short faction is gathering outside the barricaded "
    "store with tools. It's not an organised assault yet, but it will be in ten minutes "
    "when the oldest one finishes his speech.",
    # recovery
    "You get between them and the barricade and make one offer: a neutral monitor "
    "for the water distribution for the duration of the storm. "
    "One person from each faction watches every draw. No one gets more than their share.",
    # victory
    "The water distribution runs clean for the remaining four days of the storm. "
    "When the wind drops, both factions are still intact, still talking, and the "
    "settlement is still standing.",
    # partial
    "The storm ends without violence, but the ration disagreement was not fully resolved. "
    "The factions will be at each other's throats again within a week. "
    "You've bought time, not peace.",
    # defeat
    "The group breaks through the barricade. The resulting confrontation injures four "
    "people and the water store is damaged, spilling a third of the supply. "
    "The settlement is going to have a very bad week.",
    "Sit them down and mediate the ration", "composure", 8,
    "Expose the person who fired the gun", "influence", 7,
    "Address the overdrawn allocation directly", "influence", 7,
    "Find a lever to force the barricaded faction to negotiate", "tactics", 7,
    "Intercept the gathering group before they move", "composure", 8,
    "Offer the neutral monitor solution now", "influence", 8,
    "Enforce the neutral monitor across both factions", "composure", 7,
    "Get both leaders to agree to the monitored system", "influence", 8,
    "Run the monitored distribution personally", "composure", 7,
    "Stay through the storm to ensure compliance", "composure", 7,
),

_mk("tm_w05", "Dead Light", "wasteland", "wasteland_05_ruined_solar_farm",
    "Restore power to a settlement before its food storage fails overnight.", 80, 2,
    "The ruined solar farm once powered four settlements. Most panels are gone but the "
    "inverter station still stands. If you can get sixty percent of the remaining arrays "
    "online, the settlement three kilometres east can run its refrigeration through the night. "
    "The food spoils in eight hours. You have six.",
    # a_ok
    "The inverter's main coupling is cracked. You fabricate a temporary fix from salvaged "
    "components in the maintenance shed — ugly but functional. Sixty-eight percent of the "
    "arrays come online. The settlement's refrigeration holds through to morning.",
    # a_fail
    "The coupling fails completely when you attempt the repair — the crack propagates "
    "and the piece splits. Without the coupling, none of the arrays can feed to the grid. "
    "You need a different route to power.",
    # b_ok
    "You map the old grid layout and find a bypass route through the emergency circuit — "
    "normally limited to ten percent capacity, but rerouted through two substations it "
    "can carry enough load for the refrigeration units.",
    # b_fail
    "The emergency circuit trips after twenty minutes under load and cannot be reset "
    "without parts you don't have on site. The bypass is dead.",
    # mid_ok
    "Power is running to the settlement but at sixty percent of what's needed. "
    "The refrigeration units are running at reduced efficiency. If the night is warm, "
    "the food may still spoil. You need to find additional draw from the arrays.",
    # mid_fail
    "Both the primary repair and the bypass have failed. You have six arrays that are "
    "physically functional but disconnected from the grid. "
    "There's one more option in the maintenance shed that you haven't tried.",
    # crisis
    "A portable relay in the maintenance shed — dusty, unserviced, but theoretically "
    "capable of bridging the disconnected arrays directly to the settlement's own "
    "distribution board. It needs calibration. You have forty minutes before the "
    "food critical threshold.",
    # recovery
    "The relay calibration takes fifty-two minutes — twelve minutes over. The food storage "
    "temperature has risen but not critically. You get power to the refrigeration with "
    "a narrow margin.",
    # victory
    "The arrays are online at seventy-two percent and the refrigeration is holding at "
    "safe temperature through the night. The settlement's food supply is intact. "
    "The relay will need replacing, but it did the job.",
    # partial
    "The power comes on but the refrigeration only dropped to marginally safe temperature — "
    "some of the more perishable stock is questionable. About seventy percent of the "
    "food supply is preserved.",
    # defeat
    "The relay calibration runs past the critical threshold. By the time power reaches "
    "the settlement, the refrigeration has been off too long. "
    "The food is lost.",
    "Emergency repair of the inverter station", "tech", 8,
    "Divert power through the emergency bypass circuit", "tactics", 7,
    "Bring additional arrays online manually", "tech", 8,
    "Locate the portable relay in the maintenance shed", "tech", 7,
    "Calibrate the relay against the settlement's distribution board", "tech", 8,
    "Run the calibration as fast as the components allow", "composure", 8,
    "Complete the calibration and bring the relay online", "tech", 9,
    "Accept the relay margin and monitor through the night", "composure", 7,
    "Verify the refrigeration temperature after power-on", "tech", 7,
    "Signal the settlement to conserve load until morning", "tactics", 7,
),

_mk("tm_w06", "Cold Storage", "wasteland", "wasteland_06_buried_bunker",
    "Breach a sealed pre-war military bunker before rival scavengers locate it.", 140, 4,
    "Your ground-penetrating scan shows the bunker intact — full of military-grade equipment "
    "from the corporate wars. A rival scavenger team picked up the same signal two hours "
    "after you did. They're running parallel to your position and closing. "
    "The entrance is buried under two metres of collapse debris.",
    # a_ok
    "The codes are forty years old but military encryption hasn't changed its key structure "
    "since the war. You sequence through the variations in under an hour and the door cycles "
    "open. You're inside before the rivals reach the surface entrance.",
    # a_fail
    "The bunker's passive defence system is still active. The override attempt triggers "
    "an electrical countermeasure that fuses your tools. You're locked out, "
    "the rivals are closing, and you need a backup plan immediately.",
    # b_ok
    "The original schematics show a service access point two hundred metres north. "
    "You locate it under the debris, clear it quietly, and slip inside while the rivals "
    "are still working the main entrance.",
    # b_fail
    "The service entrance collapsed completely — solid rock and rebar, no way through. "
    "You spend two hours clearing debris before the assessment becomes final, "
    "and by then the rivals are at the main door.",
    # mid_ok
    "You're inside the bunker before the rivals. The equipment is substantial — more "
    "than you can carry in one trip. You need to prioritise and move the most valuable "
    "items before the rivals breach and turn this into a confrontation.",
    # mid_fail
    "The rivals are inside now too, through the main entrance. They don't know you're here "
    "yet — the bunker is large enough that your section is quiet. "
    "You're in a race through the dark.",
    # crisis
    "Both teams have found the primary equipment cache simultaneously, entering from "
    "different sections of the bunker. The cache is large enough that both teams could "
    "take something and leave — or this becomes a fight in the dark.",
    # recovery
    "You open negotiations from across the cache — two teams, enough equipment to split, "
    "no need for anyone to get hurt in a bunker where the structural integrity is "
    "forty years old. The rivals' leader listens.",
    # victory
    "You're out of the bunker with the highest-value equipment and the rivals are leaving "
    "through the main entrance with the remainder. The split is imperfect but the "
    "mission objective is met without casualties.",
    # partial
    "The split happens but the rivals got to the primary military-spec item first. "
    "You have significant secondary equipment, but your client wanted the specific unit "
    "the rivals are now carrying.",
    # defeat
    "The confrontation at the cache turns hostile. You exit the bunker without the "
    "equipment and the rivals have everything. The structural damage from the scuffle "
    "makes a second attempt unlikely.",
    "Override the lock with archived military codes", "tech", 9,
    "Find and use the alternate service entrance", "stealth", 8,
    "Prioritise and move the most valuable items", "tactics", 8,
    "Move fast through the dark before they find you", "stealth", 8,
    "Negotiate a split at the cache", "influence", 8,
    "Secure the primary item before the split completes", "composure", 8,
    "Complete the split agreement before it collapses", "influence", 8,
    "Exit before the rivals change their minds", "composure", 7,
    "Confirm the split and move the equipment out", "tactics", 7,
    "Get clear of the bunker before structural risk increases", "composure", 8,
),

_mk("tm_w07", "Wreck", "wasteland", "wasteland_07_vehicle_graveyard",
    "Survive an ambush in a vehicle graveyard and protect the convoy cargo.", 100, 3,
    "Your convoy rolled into the vehicle graveyard before the ambush signal reached you. "
    "Shooters are in the stacks and the cargo vehicle can't reverse fast enough. "
    "Three hectares of cracked earth and rusted hulks, and the fire is already coming. "
    "You need to turn this around.",
    # a_ok
    "You read the shooting positions from the muzzle flashes and move laterally through "
    "the wreckage. The ambushers were expecting a static target. They get a counter-movement "
    "that puts you behind them in four minutes. They break off.",
    # a_fail
    "The terrain is more complicated than it looked. You take a wrong turn through the "
    "stacks and emerge in a dead end with shooters on three sides. "
    "You need to extract from a corner and find a different angle.",
    # b_ok
    "You ghost back through the wrecks, pulling the ambushers after you while the cargo "
    "vehicle reverses to safety using the distraction. You exit through a gap "
    "in the eastern stack.",
    # b_fail
    "The cargo driver panics during the fallback and takes the wrong exit. The vehicle "
    "is disabled by fire before you can redirect him.",
    # mid_ok
    "The ambushers have regrouped on the north side of the graveyard and are moving "
    "to cut off the cargo vehicle's exit route. You're between them and the vehicle, "
    "in better terrain. You have maybe ninety seconds.",
    # mid_fail
    "The cargo vehicle is disabled and the driver is out of the cab, under the vehicle "
    "for cover. The ambushers are moving toward his position and he doesn't have a "
    "weapon. You need to reach him first.",
    # crisis
    "The ambush leader has the cargo vehicle's driver at gunpoint. He's not shooting — "
    "he wants to know what's in the cargo. The graveyard is quiet and you're "
    "twenty metres away with a position advantage.",
    # recovery
    "You create a distraction from the south stack — enough noise to draw his attention "
    "for three seconds. The driver doesn't need instructions. He runs.",
    # victory
    "The ambush leader takes the distraction. The driver is clear and running. "
    "You cover his exit and the ambushers lose their leverage. They break off "
    "and the cargo vehicle exits the graveyard intact.",
    # partial
    "The driver is clear but the ambush leader had time to open one cargo crate before "
    "the distraction. He took a sample — enough to know what you're carrying. "
    "The cargo is mostly intact but compromised.",
    # defeat
    "The distraction fails — the ambush leader anticipated it. The driver is taken "
    "and the cargo is searched. You extract alone from the eastern stack.",
    "Counter-flank through the wreckage", "close_combat", 8,
    "Fall back and draw the ambush out", "stealth", 8,
    "Hold the cargo vehicle's exit route", "tactics", 8,
    "Reach the pinned driver before the ambushers do", "close_combat", 8,
    "Create a distraction from the south stack", "tactics", 8,
    "Suppress the ambush leader from your position", "firearms", 9,
    "Pull the driver clear in the distraction window", "composure", 8,
    "Cover his run to the exit", "firearms", 8,
    "Move the cargo vehicle through the gap", "tactics", 8,
    "Exit the graveyard behind the cargo vehicle", "composure", 7,
),

_mk("tm_w08", "Chokepoint", "wasteland", "wasteland_08_canyon_pass",
    "Hold a canyon pass against a sustained raider assault.", 130, 4,
    "The canyon pass is the only route between two allied settlements. Raiders have "
    "blockaded the eastern end. You hold the western entrance with four operatives "
    "and whatever the canyon offers in terrain advantage. "
    "The first wave is inbound.",
    # a_ok
    "You spend an hour reshaping the battlefield — cable traps, stacked debris, covered "
    "firing positions. When the raiders push in, they push into a kill box. "
    "Three waves. The fourth doesn't come.",
    # a_fail
    "The raiders split into two groups and probe both walls simultaneously. Your prepared "
    "positions cover the centre. The flanks break through in the second wave "
    "and you're fighting from both directions.",
    # b_ok
    "Disciplined fire, coordinated reload cycles, no wasted shots. The raiders commit "
    "more than they planned to and take more than they can absorb. "
    "They break off after forty minutes.",
    # b_fail
    "Ammunition runs low in the second wave. The rate of fire drops, the raiders sense "
    "the change, and they push through the gap in the third wave.",
    # mid_ok
    "Three waves repelled but your team is down to the last ammunition reserve. "
    "The raiders are regrouping three hundred metres out — you can see the dust. "
    "A fourth wave is coming and you need to solve the ammunition problem first.",
    # mid_fail
    "One flank position is overrun. Two of your four operatives are in contact and "
    "falling back toward the centre. The raider element on that flank is already "
    "inside the prepared defence line.",
    # crisis
    "The raider element that broke through the flank is now threatening the narrow "
    "passage at the canyon's back — if they control it, you're cut off from the "
    "eastern settlement's relief team that should be inbound.",
    # recovery
    "You pull back from the western entrance to hold the passage behind you. "
    "It's a smaller line to defend with two operatives. "
    "The raiders take the entrance but can't advance further.",
    # victory
    "The relief team arrives through the eastern end as the raiders probe the canyon's "
    "middle section. Caught between two forces, the raiders break off and retreat. "
    "Both settlements remain connected.",
    # partial
    "The pass is held but the western entrance is in raider hands. Traffic between "
    "the settlements is disrupted for a week until a second operation clears the "
    "entrance position.",
    # defeat
    "The raiders control the passage. The relief team can't get through from the east "
    "and you extract through the canyon walls. The pass is lost.",
    "Set kill zones across the choke", "tactics", 9,
    "Concentrate fire and hold the line", "firearms", 8,
    "Requisition ammunition from the eastern settlement", "tactics", 8,
    "Counter-attack the element that broke through", "close_combat", 9,
    "Fall back to hold the narrow passage", "tactics", 8,
    "Hold the passage with two operatives", "firearms", 9,
    "Signal the relief team to move faster", "tactics", 8,
    "Coordinate a two-direction response as the team arrives", "tactics", 9,
    "Push the raiders back through the entrance", "close_combat", 9,
    "Hold the passage until the relief team clears the entrance", "composure", 8,
),

_mk("tm_w09", "Dead Water", "wasteland", "wasteland_09_dry_reservoir",
    "Locate a clean water source for a settlement on the edge of dehydration.", 90, 3,
    "The reservoir is bone-dry. The settlement's last purified water reserve has three days "
    "left. Your geological survey shows three possible underground sources within two "
    "kilometres. You have equipment to test two sites. "
    "The third site requires a different approach.",
    # a_ok
    "You run the test in order of geological likelihood. The second site shows promising "
    "subsurface resonance — fourteen metres down, clean mineral table, sustainable yield. "
    "The settlement has a water source.",
    # a_fail
    "The first site is dry. The second shows contamination from old reservoir chemical "
    "treatments. You're out of primary test equipment and no closer to clean water.",
    # b_ok
    "The contaminated secondary source is salvageable. You know which filtration compounds "
    "to use and in what sequence. The purifier runs its first clean cycle "
    "twelve hours after you start.",
    # b_fail
    "The contamination level exceeds your filtration capacity and the compound you need "
    "is missing from the kit. The water is undrinkable with what you have.",
    # mid_ok
    "You've confirmed a clean water source but the drilling equipment needed to reach "
    "it is at the settlement, not with you. The settlement has the tools; "
    "you have the coordinates. Moving the drilling rig to the site takes six hours "
    "and good weather.",
    # mid_fail
    "The filtration is running but at reduced efficiency — the compound substitution "
    "you made isn't as effective as the primary chemical would be. It's producing "
    "potable but not ideal water. The third site may be the better answer.",
    # crisis
    "The third site — the one you didn't have equipment for — has a natural spring "
    "visible under surface rock. No drilling needed, no filtration required. "
    "But the rock face needs to be cleared and you need to move before the "
    "settlement's reserve runs out.",
    # recovery
    "The rock clearing takes eight hours of hard work with hand tools. The spring "
    "begins flowing properly on the ninth hour. The settlement's reserve had "
    "a day left.",
    # victory
    "The spring is flowing clean at sustainable rate. The settlement has a permanent "
    "water source without the vulnerability of single-site dependency. "
    "The geological report goes into their planning records.",
    # partial
    "The filtration system is operational and producing potable water at sixty percent "
    "of normal settlement needs. Rationing will be needed but the crisis is averted. "
    "A permanent source remains unfound.",
    # defeat
    "All three options are exhausted. The settlement's reserve runs out and they begin "
    "a forced migration to the nearest settlement with a water supply. "
    "Twelve families, everything they can carry.",
    "Test the geological survey sites in order", "tech", 8,
    "Assess the contaminated source and repair the purifier", "medicine", 8,
    "Move the drilling rig to the confirmed coordinates", "tactics", 7,
    "Investigate the third site for the natural spring", "tech", 7,
    "Clear the rock face to expose the spring", "close_combat", 8,
    "Dig through the rock with the tools on hand", "composure", 8,
    "Complete the clearing before the reserve runs out", "composure", 9,
    "Confirm the spring flow rate before committing", "tech", 7,
    "Set up permanent infrastructure around the spring", "tech", 7,
    "Report the spring location and secure it against future access disputes", "tactics", 7,
),

_mk("tm_w10", "Pressure Point", "wasteland", "wasteland_10_pipeline_station",
    "Protect a fuel pipeline station from corporate saboteurs.", 100, 3,
    "The pipeline station is the only fuel source for four wasteland settlements. "
    "Corporate intelligence says a sabotage team is moving on the station tonight. "
    "If they destroy the compressor array, fuel stops flowing for six months. "
    "You have six hours to prepare.",
    # a_ok
    "You harden the compressor control systems against remote access, reroute diagnostic "
    "signals to confuse any approach targeting, and set a passive alert on every access "
    "tunnel. The saboteurs hit the first countermeasure and abort.",
    # a_fail
    "The countermeasure package has a dependency on the station's local network, which "
    "is running older firmware. The saboteurs bypass it and hit the compressor "
    "before your alerts trigger.",
    # b_ok
    "You position ahead of the most likely approach route and intercept the team before "
    "they reach the perimeter. Controlled, professional, and over in three minutes. "
    "The station never knows it was targeted.",
    # b_fail
    "The saboteurs take a secondary route your intelligence didn't flag. They're inside "
    "the perimeter before you locate them.",
    # mid_ok
    "The saboteurs have been stopped but they got close enough to damage the outer "
    "diagnostic panel before breaking off. The compressor array is intact but "
    "its monitoring system is offline. You need to restore it before morning.",
    # mid_fail
    "The compressor array has taken partial damage — a secondary pipeline, not the main, "
    "but enough to reduce station output by thirty percent. You can repair it, "
    "but the saboteurs are still in the station perimeter.",
    # crisis
    "One saboteur is still at the main compressor housing. He has a device you don't "
    "recognise and he knows you're here. Two minutes until it's placed. "
    "One minute until you reach him.",
    # recovery
    "You reach him in under a minute but he's faster to the housing than you expected. "
    "You take the device before it's set but he escapes through the service tunnel. "
    "The device is in your hands. The housing is intact.",
    # victory
    "The station is secure, the saboteur team is neutralised, and the compressor array "
    "is running at full capacity. The fuel supply to all four settlements is uninterrupted. "
    "The device is evidence.",
    # partial
    "The primary compressor is intact but the secondary pipeline damage will reduce "
    "settlement fuel supply for two weeks during repairs. The saboteur team was stopped "
    "before the critical element was completed.",
    # defeat
    "The device is placed and detonates before you reach the housing. "
    "The compressor array is destroyed. Six months of supply disruption "
    "for four settlements begins tonight.",
    "Secure the compressor array with countermeasures", "tech", 8,
    "Hunt the saboteurs before they reach the station", "firearms", 7,
    "Restore the diagnostic monitoring system", "tech", 8,
    "Locate and engage the remaining saboteurs", "tactics", 8,
    "Reach the compressor housing before the device is set", "close_combat", 8,
    "Take the device before it can be placed", "composure", 9,
    "Disable the saboteur and secure the device", "close_combat", 8,
    "Clear the station perimeter of remaining saboteurs", "tactics", 8,
    "Secure the device and assess the housing damage", "tech", 7,
    "Coordinate the response with station security", "tactics", 7,
),

_mk("tm_w11", "Black Box", "wasteland", "wasteland_11_crashed_drone",
    "Recover intelligence data from a military drone before the corporate retrieval team arrives.", 110, 3,
    "The drone went down in the borderlands two hours ago — military-grade, autonomous, "
    "carrying three months of corporate activity sensor data. The corporate retrieval team "
    "is airborne and forty minutes out. You have the coordinates "
    "and a forty-minute window.",
    # a_ok
    "The armoured housing is designed to survive the crash intact. You know which panel "
    "gives access to the data core and you've done this before. "
    "Twelve minutes extraction, full data package, moving before the retrieval team lands.",
    # a_fail
    "The impact deformed the housing. The panel won't open cleanly and you waste twenty "
    "minutes forcing it. The retrieval team lands during the extraction "
    "and you leave empty-handed.",
    # b_ok
    "You assess the retrieval team's arrival timeline and decide the perimeter comes first. "
    "Your team slows their approach with terrain obstacles while the tech specialist "
    "completes the extraction at a workable pace.",
    # b_fail
    "The retrieval team has air support you didn't account for. Your perimeter holds "
    "on the ground but the air assets bypass it and land directly at the crash site.",
    # mid_ok
    "You have the data core and you're moving when the retrieval team establishes a "
    "perimeter around the crash site. They don't know you have the core yet — "
    "they're looking at the empty housing. You have a five-minute head start.",
    # mid_fail
    "The retrieval team has air support and one craft is now between you and your "
    "vehicle. The data core is in your bag. The craft has sensors.",
    # crisis
    "The air support craft is scanning the area in a pattern that will pass directly "
    "over your position in ninety seconds. You're in open scrubland with no "
    "overhead cover. The data core transmits a low-power signal if it's active.",
    # recovery
    "You power down the core — no signal — and go flat in the scrub. The thermal "
    "scan passes overhead and keeps moving. You wait three minutes before "
    "moving again.",
    # victory
    "You reach your vehicle with the core before the retrieval team understands what "
    "happened. The empty housing buys you twenty minutes of confusion. "
    "Three months of corporate sensor data, in hand.",
    # partial
    "You have the core but it was partially powered down during the retrieval team's "
    "approach scan. Some of the data requires specialist recovery equipment "
    "to surface. Sixty percent of the intelligence package is immediately accessible.",
    # defeat
    "The air support craft identifies the powered-down core through proximity sensors. "
    "The retrieval team reaches you before you reach your vehicle. "
    "The core is taken.",
    "Extract the data core directly", "tech", 8,
    "Secure the perimeter and buy time for extraction", "tactics", 7,
    "Move before the retrieval team's perimeter tightens", "stealth", 8,
    "Evade the air support craft's scan pattern", "stealth", 8,
    "Power down the core and go flat in the scrub", "composure", 8,
    "Wait out the scan and move in the gap", "composure", 8,
    "Reach the vehicle before the scan completes another pass", "composure", 9,
    "Move through the scrub below thermal detection threshold", "stealth", 9,
    "Clear the retrieval team's perimeter and extract", "stealth", 8,
    "Get the core to the vehicle and move", "composure", 7,
),

_mk("tm_w12", "Dead Zone", "wasteland", "wasteland_12_comms_array",
    "Install a communications relay in a jammed section of the badlands.", 100, 3,
    "The resistance network has a blind spot — forty kilometres of corporate jamming. "
    "The relay needs to go on the comms array tower at the centre of the zone. "
    "The jamming makes radio coordination impossible once you're inside. "
    "You go in on memory and come out with the relay installed.",
    # a_ok
    "You map the patrol pattern of the array's two guards before entering the zone, "
    "memorise the timing, and execute entirely on that memory. The relay goes up in "
    "eleven minutes. The guards never break their rotation.",
    # a_fail
    "One guard deviates from his pattern — a bathroom break that puts him at the tower "
    "base exactly when you're on the third rung of the access ladder. "
    "You abort the climb and retreat before he looks up.",
    # b_ok
    "Rather than installing on the corporate array, you set up an independent relay "
    "on a secondary highpoint outside the jamming cone. It takes longer but "
    "it's fully in your control.",
    # b_fail
    "The highpoint you identified as the relay site is occupied by a corporate signal "
    "monitor. You can't set up without being detected.",
    # mid_ok
    "The relay is in place and transmitting but the signal is reflecting off the "
    "corporate array's own infrastructure. You need to adjust the relay's "
    "angle to clear the interference without climbing down.",
    # mid_fail
    "The guard who deviated has completed his bathroom break and is now running "
    "a foot patrol of the tower perimeter — something he wasn't doing before. "
    "You need to wait him out or draw him away.",
    # crisis
    "The relay is installed but the guard has returned to the tower base and is looking "
    "up. He can see the relay box from where he's standing. "
    "He's reaching for his radio.",
    # recovery
    "You come down from the tower confidently — maintenance posture, tool belt visible — "
    "and intercept him before he completes the call. A maintenance visit, "
    "scheduled by the east sector team, nothing to report.",
    # victory
    "The guard nods and goes back to his rotation. The relay is transmitting cleanly "
    "and the blind spot in the resistance network is closed. "
    "Nobody in the zone knows it's there.",
    # partial
    "The relay is installed but your maintenance bluff drew the guard's attention to the "
    "tower. He'll report the visit and someone will inspect the tower within a week. "
    "The relay has a limited lifespan.",
    # defeat
    "The guard completes the radio call before you reach him. A response team is "
    "dispatched and the relay is found and removed during their sweep. "
    "The blind spot remains.",
    "Ghost the installation — no contact", "stealth", 9,
    "Set up an independent relay on the secondary highpoint", "tech", 8,
    "Adjust the relay angle from the tower", "tech", 8,
    "Draw the patrol guard away from the perimeter", "tactics", 8,
    "Come down and intercept before he calls it in", "composure", 9,
    "Bluff the maintenance visit convincingly", "influence", 9,
    "Get back to the relay and complete the angle adjustment", "stealth", 8,
    "Confirm the relay is transmitting before leaving", "tech", 7,
    "Exit the jamming zone before the next patrol rotation", "stealth", 8,
    "Verify the network blind spot is closed", "tech", 7,
),

_mk("tm_w13", "Ghost Train", "wasteland", "wasteland_13_derelict_maglev",
    "Clear a mutant infestation from an ancient derelict maglev train.", 90, 2,
    "The derelict maglev hasn't moved in thirty years but something has been living in it "
    "for six months and making the eastern settlements impassable after dark. "
    "Nine cars, unknown number of contacts, and total darkness inside. "
    "You go in at dusk.",
    # a_ok
    "You move from the front car to the rear, sealing each section as you clear it. "
    "The creatures retreat into the final car. You seal it from the outside "
    "and the train is clear in two hours.",
    # a_fail
    "The creatures in the rear cars hear you working forward and begin moving through "
    "the roof access hatches. They're ahead of you by car five and you're dealing "
    "with contact from two directions simultaneously.",
    # b_ok
    "You identify the loudest possible noise source in the train — the emergency alert "
    "horn — and trigger it from car five. Everything in the train moves toward the sound. "
    "You seal the forward cars and deal with the concentration in one controlled engagement.",
    # b_fail
    "The emergency horn is non-functional — the power cell corroded decades ago. "
    "Your improvised noise source attracts half the infestation. "
    "The other half finds you from the wrong direction.",
    # mid_ok
    "The train is mostly clear. Three creatures remain in the rear mechanical section — "
    "a cramped space you don't want to enter blind. You can hear them moving. "
    "There's a maintenance hatch that opens from outside the train.",
    # mid_fail
    "You're dealing with contacts from two directions in car six. The train's confined "
    "space is working against you. The creatures know this environment better than you do "
    "and they're using the crawlspaces.",
    # crisis
    "One large creature has blocked the connecting passage between cars seven and eight. "
    "It's not moving forward — it's holding the line. The others are regrouping behind it. "
    "Getting past it is the only way to clear the rear section.",
    # recovery
    "You go through the roof hatch instead of the connecting passage — slow, exposed "
    "to the weather, but bypassing the creature in the passage. "
    "You drop into car eight from above.",
    # victory
    "The rear section is clear. You seal car nine from outside and the train is fully "
    "swept. The eastern settlements can move at night again. "
    "The train is going to need a proper seal welded, but that's tomorrow's problem.",
    # partial
    "The train is mostly clear but three creatures escaped through an external damage "
    "breach you missed — they're in the badlands now rather than the train. "
    "They'll return when the noise stops.",
    # defeat
    "The two-direction contact in car six forces you to withdraw from the train. "
    "You come out the front with minor injuries and the infestation intact. "
    "A second attempt will need better preparation.",
    "Clear systematically, car by car", "close_combat", 8,
    "Lure everything to a single chokepoint", "tactics", 8,
    "Enter the rear mechanical section via the maintenance hatch", "stealth", 7,
    "Fight through the two-direction contact in car six", "close_combat", 9,
    "Go through the roof hatch to bypass the blockage", "stealth", 8,
    "Drop into car eight and clear the rear from there", "close_combat", 8,
    "Clear car eight and then car nine in sequence", "close_combat", 8,
    "Seal the remaining creatures into car nine", "tactics", 7,
    "Seal the exit breach to prevent escape", "tactics", 7,
    "Confirm all cars are clear before exiting", "composure", 7,
),

_mk("tm_w14", "Dig Site", "wasteland", "wasteland_14_buried_arcade",
    "Recover a pre-war cache from ruins controlled by a territorial gang.", 90, 2,
    "The buried arcade was a tourist destination before the corporate wars. Now it's a "
    "gang hangout and, somewhere under the collapse, a pre-war cache of networking hardware "
    "worth more than the gang earns in a year. They don't know it's there. Yet. "
    "You need to get it first.",
    # a_ok
    "The gang posts a single overnight watch who sleeps through his rotation every night "
    "this week — your surveillance confirmed it. You're inside and back out in ninety "
    "minutes with enough hardware to equip a small network.",
    # a_fail
    "The overnight watch is awake and doing rounds tonight. You're spotted during approach "
    "and have to withdraw before reaching the cache. The watch is now alert "
    "and the easy window is closed.",
    # b_ok
    "A former gang member who owes a favour draws you a floor plan and marks the cache "
    "location from memory. You go in at a shift change with a salvage permit for an "
    "unrelated nearby site. Nobody looks twice.",
    # b_fail
    "The informant's loyalty is for sale to the highest bidder. The gang has the floor plan "
    "before you arrive and a welcome party is waiting at the cache site.",
    # mid_ok
    "The cache is located and you're extracting it when you hear voices in the upper "
    "section of the arcade. Gang members coming back early. "
    "You have four minutes before they reach your level.",
    # mid_fail
    "The welcome party at the cache site is four gang members who are not interested "
    "in conversation. You're in the lower arcade with the cache and no obvious exit "
    "that doesn't go through them.",
    # crisis
    "You're in the lower arcade with the cache loaded. The exit is blocked — either by "
    "the early-returning members above or the confrontational group near the site. "
    "There's a collapse tunnel to the east that might reach the street.",
    # recovery
    "The collapse tunnel is tight and unstable but it opens into an alley twenty metres "
    "east of the arcade entrance. You move the cache through it in three trips, "
    "tools first, hardware second, yourself last.",
    # victory
    "You're in the alley with the full cache before the gang members find the empty "
    "cache site. By the time they understand what happened, you're four blocks away. "
    "The networking hardware is yours.",
    # partial
    "You get two thirds of the cache through the tunnel before it becomes too unstable "
    "to use safely. The remaining hardware stays in the lower arcade. "
    "Functional equipment, but not everything your client wanted.",
    # defeat
    "The collapse tunnel gives way during the second trip. You extract yourself but the "
    "cache is sealed in the lower arcade under fresh debris. "
    "The gang will find it when they clear the collapse.",
    "Infiltrate at night and locate the cache", "stealth", 8,
    "Buy information about the site layout", "influence", 7,
    "Move the cache before they reach your level", "composure", 8,
    "Find a way past the confrontational group", "stealth", 8,
    "Use the collapse tunnel to reach the street", "composure", 8,
    "Move the cache through the tunnel in stages", "composure", 8,
    "Complete all three trips before it destabilises further", "composure", 9,
    "Assess the tunnel stability before committing to the third trip", "tech", 7,
    "Get the cache and yourself clear of the tunnel", "composure", 8,
    "Reach the alley and move before they find the site", "composure", 7,
),

_mk("tm_w15", "Stone and Steel", "wasteland", "wasteland_15_scrap_quarry",
    "Stop a gang from extracting strategic materials from a contested quarry.", 110, 3,
    "The scrap quarry contains rare earth materials left behind by pre-war construction. "
    "The Ironback gang has been mining it for three months. If they complete the extraction, "
    "those materials fund their expansion into three more settlements. "
    "You need to shut the operation down.",
    # a_ok
    "You identify the tunnel support structure's weak points from the survey data and "
    "time the collapse for shift change — nobody underground when the ceiling comes down. "
    "The quarry is non-operational. It will take months to clear.",
    # a_fail
    "The explosive charge misfires. The tunnel stays intact and the gang now knows "
    "someone is targeting the site. They've doubled the perimeter security.",
    # b_ok
    "Twelve operatives against the gang's security rotation, terrain advantage in your "
    "favour. A fast, hard push through the site boundary breaks their security "
    "before they can organise. They abandon the equipment.",
    # b_fail
    "The gang has twice as many security personnel as your intelligence suggested. "
    "The direct engagement becomes a prolonged fight you can't sustain.",
    # mid_ok
    "The gang's extraction equipment is disabled and the leadership is in retreat. "
    "But two fully loaded transport vehicles are still on site with the rare earth "
    "materials. They're preparing to move.",
    # mid_fail
    "You've been repelled from the perimeter and the gang has gone to high security. "
    "Direct approach is no longer viable. The materials are still being extracted "
    "and transport vehicles are loading. You need a different method.",
    # crisis
    "The transport vehicles are moving. They'll be off-site and dispersed in the "
    "settlement network in twenty minutes, impossible to recover. You have one vehicle "
    "of your own and a road ahead of them.",
    # recovery
    "You position your vehicle across the road at a section too narrow to pass. "
    "It's not a lethal ambush — it's a negotiating position. The drivers stop. "
    "What comes next depends on what you say.",
    # victory
    "The transport drivers are not gang leadership — they're contractors. "
    "You give them a reason to walk away from the materials and they take it. "
    "The rare earth consignment is impounded at the road block.",
    # partial
    "One vehicle turns back. The other finds a secondary track you didn't account for "
    "and gets through. Half the extraction haul is recovered; the other half reaches "
    "the gang's settlement network.",
    # defeat
    "Both transport drivers are committed to the run. They bypass your road block "
    "via the secondary track and both vehicles reach the settlement network intact. "
    "The materials are dispersed and unrecoverable.",
    "Collapse the primary extraction tunnel", "tactics", 8,
    "Drive the gang out in a direct engagement", "close_combat", 7,
    "Intercept the transport vehicles before they leave the site", "tactics", 8,
    "Disable the vehicles through the secondary track entry point", "tech", 8,
    "Position your vehicle across the narrow road section", "tactics", 8,
    "Give the drivers a reason to walk away from the load", "influence", 8,
    "Negotiate with the drivers for the full consignment", "influence", 9,
    "Accept partial recovery and let one vehicle go", "composure", 7,
    "Confirm the recovered consignment is secure", "tactics", 7,
    "Document the consignment for legal impoundment", "tactics", 6,
),

]  # end _WASTE block 1 (tm_w01–tm_w15)

# ── WASTELAND MISSIONS 16–30 ─────────────────────────────────────────────────

_WASTE_2 = [

_mk("tm_w16", "Blight", "wasteland", "wasteland_16_hydroponic_farm",
    "Save a hydroponic farm from a pathogen outbreak before the crop is lost.", 90, 2,
    "The hydroponic arrays cover three greenhouse modules — the only year-round food source "
    "for two thousand people in the eastern waste. A fungal pathogen moved through the "
    "nutrient system overnight and has taken thirty percent of the growing beds. "
    "Without intervention, the outbreak doubles every six hours.",
    # a_ok
    "The pathogen signature matches a class you've dealt with before. You identify the "
    "primary nutrient vector, flush the contaminated channels, and replace the growth "
    "solution. Forty minutes in, the spread rate drops to zero.",
    # a_fail
    "The pathogen is a modified strain — it's been engineered to resist standard "
    "treatment protocols. Your flush eliminates the nutrient vector but the pathogen "
    "survives on the plant tissue itself. The beds keep dying.",
    # b_ok
    "You isolate the three worst modules from the rest of the system by closing the "
    "nutrient feed valves. The outbreak stops propagating. You lose thirty percent "
    "of the crop but the other seventy percent is clean.",
    # b_fail
    "The isolation valve for module two is seized — it won't close. The pathogen has "
    "a clear path into the clean section and you have about four hours.",
    # mid_ok
    "The crop loss is contained. But the surviving beds are under stress from the "
    "emergency flush — nutrient levels are off and the plants need monitoring. "
    "If you leave now, the facility manager can maintain it. "
    "If the modified pathogen returns, it won't be the last outbreak.",
    # mid_fail
    "Module two is still connected to the clean section. You can force the valve "
    "physically but it will take the right tools and a confined workspace "
    "next to diseased plant material.",
    # crisis
    "The modified pathogen has evolved a second dispersal mechanism — airborne spores "
    "within the greenhouse. The ventilation system is now a vector. "
    "If it reaches the air ducts, the entire facility is lost.",
    # recovery
    "You kill the ventilation system and drop the greenhouse temperature to slow "
    "spore dispersal. It buys you enough time to manually filter and sterilise "
    "the duct access points before reopening airflow.",
    # victory
    "The outbreak is contained. The modified pathogen is logged and the facility's "
    "treatment protocols are updated. The remaining seventy percent of the crop "
    "is clean and on schedule.",
    # partial
    "The airborne outbreak is suppressed but not before it touched two additional "
    "growing beds. Final crop loss is forty-five percent — painful, but the "
    "facility survives to the next growth cycle.",
    # defeat
    "The ventilation system carries the spores through the full facility before you "
    "can shut it down. All three modules are contaminated. "
    "The crop is lost and the facility needs full decontamination before replanting.",
    "Identify and flush the nutrient vector", "medicine", 8,
    "Close the nutrient feed valves on contaminated modules", "tech", 7,
    "Force the seized isolation valve physically", "close_combat", 8,
    "Locate an alternate isolation route for module two", "tech", 8,
    "Kill the ventilation system before spore dispersal", "composure", 9,
    "Manually sterilise the duct access points", "medicine", 9,
    "Complete sterilisation before restoring airflow", "medicine", 9,
    "Restore airflow and confirm the spore count is zero", "medicine", 8,
    "Update the facility treatment protocols", "tech", 7,
    "Monitor the surviving beds before leaving", "medicine", 7,
),

_mk("tm_w17", "Blind Spot", "wasteland", "wasteland_17_night_convoy_route",
    "Run a night convoy through bandit territory without lights.", 100, 3,
    "The night convoy route is the only way to move the medical shipment without "
    "the corporate checkpoints finding it. No lights, no radio, four vehicles, "
    "forty kilometres of bandit territory, and a driver who has done this run "
    "exactly twice before. You navigate from the lead vehicle.",
    # a_ok
    "You run navigation off the star pattern and the road texture under the tyres — "
    "thirty years of combined experience against forty kilometres of dark. "
    "The convoy arrives forty minutes ahead of schedule.",
    # a_fail
    "You miss a fork in the dark and the convoy turns into a drainage basin. "
    "The second vehicle grounds in the mud and you're stationary in bandit territory "
    "with no lights and two hours until dawn.",
    # b_ok
    "You know this section of the territory's bandit patrol pattern. You time the gaps "
    "and the convoy moves between them like water between stones. "
    "No contact. No noise.",
    # b_fail
    "A new patrol pattern — the bandits reorganised since your last run. A band "
    "picks up the convoy's dust trail and begins pacing it from the north.",
    # mid_ok
    "The convoy is in the clear section and the bandits are behind you. "
    "But the third vehicle has a slow tyre and is falling behind the formation. "
    "At this pace, it'll be separated by the time the bandits close the gap.",
    # mid_fail
    "The convoy is being paced and the grounded vehicle is stuck in the basin. "
    "You need to either free it quietly or redistribute the medical shipment "
    "into the remaining three vehicles before dawn comes and the patrol converges.",
    # crisis
    "The pacing band has realised the convoy isn't turning around. They're accelerating. "
    "The slow vehicle is one kilometre behind the lead. "
    "The bandits will reach it before it reaches the formation.",
    # recovery
    "You turn the lead vehicle around and drive back past the slow vehicle — lights on, "
    "engine loud. The bandits pivot to the lead vehicle while the slow vehicle "
    "runs dark past them on the road shoulder.",
    # victory
    "The distraction works. The slow vehicle slips through while the bandits pursue "
    "the lead. You outrun them on the road and circle back to rejoin the convoy "
    "two kilometres from the destination.",
    # partial
    "The slow vehicle gets through but you take fire during the distraction run. "
    "Minor damage to the lead vehicle, no injuries, medical shipment intact. "
    "You arrive at the destination two hours late.",
    # defeat
    "The distraction fails — the bandits split and take both vehicles simultaneously. "
    "The convoy stops and the medical shipment is confiscated at the road shoulder.",
    "Navigate the route without lights", "composure", 8,
    "Thread the convoy through the patrol gap", "stealth", 7,
    "Get the slow vehicle back into formation", "tactics", 8,
    "Free the grounded vehicle or redistribute the load", "composure", 8,
    "Run a distraction to let the slow vehicle slip through", "composure", 8,
    "Outrun the bandits in the lead vehicle", "composure", 9,
    "Circle back and rejoin the convoy formation", "tactics", 8,
    "Bring the lead vehicle to the destination", "composure", 7,
    "Confirm the medical shipment is intact on arrival", "medicine", 6,
    "Hand off the shipment to the receiving settlement", "influence", 6,
),

_mk("tm_w18", "Depths", "wasteland", "wasteland_18_sinkhole_ruins",
    "Rescue a survey team trapped by a sinkhole collapse in pre-war ruins.", 110, 3,
    "The survey team went underground at 0600. At 0900 the surface radio reported collapse "
    "in section B. At 0905 the radio went silent. Four people below ground, unknown depth, "
    "one structural engineer and three field surveyors. "
    "Your rope is fifty metres and the collapse is still settling.",
    # a_ok
    "The collapse created a debris bridge that you can use as an anchor point. "
    "Your rigging holds the first drop steady and you reach the survey team's section "
    "in thirty minutes. Two are mobile, two need assistance.",
    # a_fail
    "The anchor point you chose is on a section that continues to settle. "
    "The rope slips on the second descent and you have to abort to rerig. "
    "The structural noise below is increasing.",
    # b_ok
    "The structural engineer's radio is down but her mapping tablet transmitted before "
    "signal loss — you have a partial floor plan. You navigate to the nearest "
    "stable section and find all four survivors sheltering under a load-bearing arch.",
    # b_fail
    "The floor plan shows the section is below a partial collapse that is actively "
    "moving. The route the map shows is now blocked by a two-metre debris fall.",
    # mid_ok
    "You have the four survivors and a stable section above you. The original descent "
    "route is blocked — the debris bridge has shifted. There's an alternative "
    "access shaft forty metres west.",
    # mid_fail
    "The collapse above the access shaft is ongoing. You have an hour before the "
    "shaft becomes impassable and the debris below continues to shift. "
    "You need to move the survivors now.",
    # crisis
    "Two survivors cannot move without assistance and your rope can only take one "
    "person at a time on the western shaft. The structural noise is increasing again — "
    "the arch they're sheltering under is showing stress fractures.",
    # recovery
    "You build a simple sling from the survey team's equipment — not rated for rescue "
    "but strong enough for a slow, controlled lift. You go two at a time "
    "and make three trips.",
    # victory
    "All four survivors are out of the collapse zone before the arch gives way. "
    "The sinkhole continues to develop over the following hours. "
    "Nobody is going back down.",
    # partial
    "Three survivors are out before the western shaft partially closes. "
    "The fourth — one of the field surveyors — makes it out through a narrow breach "
    "in the shaft wall with a dislocated shoulder.",
    # defeat
    "The western shaft collapses before the last two survivors are out. "
    "The sinkhole continues to develop and rescue attempts are suspended for forty-eight "
    "hours pending structural stabilisation.",
    "Rig a descent into the collapse zone", "composure", 9,
    "Navigate to the survivors using the partial floor plan", "tactics", 8,
    "Find the western shaft as an alternate exit", "tactics", 8,
    "Move the survivors before the shaft closes", "composure", 9,
    "Build a sling for assisted extraction", "tech", 8,
    "Run three trips with the sling to extract all four", "composure", 9,
    "Complete the third trip before the arch fails", "composure", 9,
    "Clear the western shaft and get topside", "composure", 8,
    "Confirm all four survivors are out", "composure", 7,
    "Move everyone clear before further collapse", "tactics", 7,
),

_mk("tm_w19", "Shelter", "wasteland", "wasteland_19_toxic_rain_shelter",
    "Defend a temporary shelter against raiders during a toxic storm.", 90, 2,
    "The storm came in faster than predicted. You're sheltering with a group of refugees "
    "in a pre-war maintenance depot — eighty people, one entrance, and three raider "
    "vehicles that parked outside twenty minutes after you arrived. "
    "They want what you've got. You have four hours until the storm breaks.",
    # a_ok
    "You block and bar every access point and explain the mathematics to the raider "
    "leader through the door: he can stand in a toxic storm until the door holds "
    "or he can shelter somewhere else. He drives away after ninety minutes.",
    # a_fail
    "The raider leader is not interested in mathematics. His crew begins working on "
    "the loading bay door and they have the tools for it. "
    "The entrance won't hold past two hours.",
    # b_ok
    "You offer the raiders an exchange: shelter space in the back section of the depot "
    "in return for not touching the refugees or their supplies. "
    "The leader agrees. Uncomfortable, but survivable.",
    # b_fail
    "The leader's deputy rejects the offer and takes over the negotiation. "
    "His terms are unconditional — all supplies, or the door comes off.",
    # mid_ok
    "Four hours pass and the storm begins to break. The raider crew is restless — "
    "they got nothing and they're looking for an exit that lets them save face. "
    "They need a reason to leave without confrontation.",
    # mid_fail
    "The loading bay door is coming apart. The raider crew will be inside in thirty "
    "minutes. Eighty refugees, one entrance, and the storm still has two hours "
    "to run. You need options.",
    # crisis
    "The door is breached. The first two raider crew members are inside and the "
    "refugees are retreating further into the depot. The leader hasn't come in yet — "
    "he's standing at the entrance watching.",
    # recovery
    "You step forward and speak directly to the leader — his two crew members are "
    "inside and outnumbered eighty to two, in the dark, in a closed building, "
    "with more storm outside. He calls them back.",
    # victory
    "The crew withdraws. The leader takes his vehicles and drives east when the storm "
    "breaks. Eighty refugees wait out the remaining storm and move on at dawn. "
    "No supplies taken. No injuries.",
    # partial
    "The standoff ends but not cleanly. The raiders take two supply crates from the "
    "loading bay before withdrawing — twenty percent of the refugees' total supplies. "
    "A price, but manageable.",
    # defeat
    "The leader overrules your logic. The two crew members inside find the supply cache "
    "and the remaining crew enters to help carry it out. The refugees have enough "
    "to survive but the journey ahead is significantly harder.",
    "Fortify and out-wait them", "tactics", 7,
    "Offer shelter space in exchange for peace", "influence", 7,
    "Give the leader a face-saving exit as the storm breaks", "influence", 8,
    "Find a second exit or defensive fallback", "tactics", 8,
    "Confront the leader as his crew enters", "composure", 8,
    "Make the outnumbered argument directly to the leader", "influence", 9,
    "Get his crew to withdraw and his vehicles to leave", "influence", 8,
    "Hold the depot until the storm ends", "composure", 7,
    "Ensure the refugees are clear to move at dawn", "tactics", 6,
    "Account for any supplies taken before departure", "tactics", 6,
),

_mk("tm_w20", "Last Line", "wasteland", "wasteland_20_city_wall_perimeter",
    "Hold the city wall perimeter against a coordinated raider assault.", 140, 5,
    "The perimeter cameras went dark forty minutes before the assault started. "
    "Someone on the inside killed them — and now you have three hundred raiders "
    "against a wall section defended by forty security personnel. "
    "The insider is still in the compound. You have to solve both problems at once.",
    # a_ok
    "Two things happen simultaneously: you identify the insider from the camera "
    "blackout pattern and your tactical redeployment turns the wall section "
    "into an overlapping kill zone. The assault fails on the second wave.",
    # a_fail
    "The insider triggers a secondary sabotage — the inner gate mechanism "
    "jams open during the second wave. The raiders have a corridor into the compound "
    "and you're fighting on two fronts.",
    # b_ok
    "You move the wall section to a rotating position pattern — no static guards, "
    "everyone moving, the raiders can't read the gaps. They take heavy losses "
    "in the approaches and the assault command breaks off before the third wave.",
    # b_fail
    "The raiders identify the rotation pattern faster than expected. They time the "
    "gaps and a breach team gets under the wall during the third rotation.",
    # mid_ok
    "The assault is faltering but the insider has not been found. If they act again "
    "before the assault fails, they can still turn the battle. "
    "You have a list of twelve people with access to the camera system.",
    # mid_fail
    "The breach team is inside the compound. Twelve people, hardened, moving toward "
    "the inner gate. If they reach it and jam it from inside, the rest of the raiders "
    "can walk in.",
    # crisis
    "You've found the insider — one of the twelve on the access list, and he's moving "
    "toward the backup gate control. The breach team is forty metres from the inner gate. "
    "You have one choice: which threat to address first.",
    # recovery
    "You take the insider — the breach team can't use the inner gate if the backup "
    "control is locked. Two minutes. The breach team reaches the gate and finds it "
    "unresponsive. They pull back to the primary assault.",
    # victory
    "The insider is restrained, the inner gate holds, and the assault commander "
    "breaks off the primary assault when the breach team reports no access. "
    "The perimeter holds. The raiders leave.",
    # partial
    "The perimeter holds but the breach team did enough damage to the inner gate "
    "mechanism that repairs will take a week. The wall is defended but vulnerable "
    "until then.",
    # defeat
    "The breach team reaches the backup gate control before you reach the insider. "
    "The inner gate jams open. The raiders pour into the compound and the perimeter "
    "falls.",
    "Identify the insider and plug the camera gap simultaneously", "tactics", 9,
    "Deploy in a rotating pattern to deny clean gaps", "tactics", 9,
    "Narrow down the twelve-person access list", "influence", 8,
    "Counter the breach team inside the compound", "close_combat", 9,
    "Take the insider first to lock the backup gate control", "composure", 9,
    "Lock the backup gate control before the breach team reaches it", "tech", 9,
    "Restrain the insider and confirm the gate is secured", "composure", 8,
    "Coordinate the perimeter hold while the inner threat is resolved", "tactics", 8,
    "Confirm the assault commander has broken off the attack", "tactics", 8,
    "Secure the compound and account for all breach team members", "tactics", 8,
),

_mk("tm_w21", "Road Peace", "wasteland", "wasteland_21_nomad_caravan_camp",
    "Negotiate a transit agreement between feuding nomad clans.", 80, 2,
    "Two nomad clans share the same migration circuit and use the same water sources. "
    "They haven't been at peace for eight years. Now the circuit is closing in — "
    "corporate territory on two sides, drying basin on a third. "
    "They have to share or collapse. They've agreed to sit and talk. Once.",
    # a_ok
    "You map the circuit geometry against both clans' traditional timing and show them "
    "that the routes don't actually conflict — they've been fighting over overlap that "
    "doesn't need to be overlap. Both elders sign the seasonal schedule.",
    # a_fail
    "The mapping session goes well until the elder from the eastern clan accuses the "
    "western elder of stealing from a cache last dry season. The evidence is "
    "disputed and both sides stand. The scheduled route plan becomes secondary.",
    # b_ok
    "You bring three respected individuals from neutral camps who know both elders. "
    "Their presence doesn't resolve the history but it creates enough mutual "
    "credibility for the route plan to be tabled seriously.",
    # b_fail
    "One of the neutral mediators has a historical grievance with the eastern clan "
    "that you didn't know about. His presence makes things worse, not better.",
    # mid_ok
    "The route plan is agreed in principle. The water source allocation — two sites "
    "each, shared access on the third — is on the table. "
    "Both elders are still talking. But the cache accusation is unresolved "
    "and could blow the whole arrangement.",
    # mid_fail
    "The mediation is in danger of failing over the cache incident. The western elder "
    "has produced a witness, the eastern elder is calling the witness a liar. "
    "The route plan is forgotten.",
    # crisis
    "The eastern elder is on his feet. The witness account is damaging and he's about "
    "to end the session and walk out. If he leaves, both clans return to conflict.",
    # recovery
    "You interrupt before he reaches the door — acknowledge the cache incident as real "
    "and propose a compensation mechanism that doesn't require either elder to "
    "admit wrongdoing in public. Face is saved. The session continues.",
    # victory
    "The seasonal route plan and the water source allocation are both agreed. "
    "The cache compensation mechanism is noted as a separate track. "
    "Both clans leave on the same road heading in different directions, which is exactly "
    "what a successful mediation looks like.",
    # partial
    "The route plan is agreed but the water source allocation breaks down on the third "
    "site. Both clans agree to defer it to next dry season. "
    "Seven years of tension reduced to one unresolved item.",
    # defeat
    "The eastern elder leaves. The western elder follows shortly after, interpreting "
    "the exit as an insult. No agreement, no route plan, and the cache incident "
    "is now a flashpoint instead of a background grievance.",
    "Map the migration circuit to eliminate fake overlap", "influence", 8,
    "Bring neutral mediators to create mutual credibility", "influence", 7,
    "Table the water source allocation plan", "influence", 8,
    "Redirect the session from the cache incident", "composure", 8,
    "Interrupt and propose a face-saving compensation", "influence", 9,
    "Keep both elders in the room after the rescue", "composure", 8,
    "Complete the water source allocation agreement", "influence", 8,
    "Close the session with both elders in agreement", "composure", 7,
    "Confirm the route plan is recorded and agreed", "influence", 7,
    "Document the compensation mechanism for follow-up", "influence", 6,
),

_mk("tm_w22", "Blowout", "wasteland", "wasteland_22_extraction_rig",
    "Stop a dangerous gas blowout at a wasteland extraction rig before it ignites.", 130, 4,
    "The rig foreman is dead. The blowout preventer has failed. Gas is venting from "
    "the wellhead at pressure and three workers are still in the drill floor below "
    "the vent zone. You have fifteen minutes before the concentration hits ignition "
    "threshold and the static discharge from the rig structure does the rest.",
    # a_ok
    "The secondary manual preventer valve is in the sub-deck — you know where it is "
    "because you read the schematics on the drive out here. Two minutes in the vent "
    "zone with a respirator and the valve turns. The gas drops to a safe level.",
    # a_fail
    "The valve requires a specific torque tool that you don't have. You improvise "
    "but the improvisation fails to hold. The gas continues at full pressure "
    "and you're at eight minutes.",
    # b_ok
    "You reach the three workers and get them off the drill floor in four minutes — "
    "two under their own power, one in a carry. They're clear before the ignition "
    "threshold is reached.",
    # b_fail
    "One worker is pinned under a fallen cable rack. You can't carry him and he can't "
    "free himself. The gas clock is running and you need two hands for the rack.",
    # mid_ok
    "Workers are clear. The gas is still venting. You have six minutes. "
    "The rig's emergency bleed valve on the eastern side of the wellhead "
    "can be opened remotely from the control shack.",
    # mid_fail
    "The worker under the rack is free but barely mobile. The gas clock is at "
    "three minutes and the rig's emergency bleed valve is sixty metres away. "
    "You can't carry him and reach the valve in time.",
    # crisis
    "Two minutes to ignition threshold. The emergency bleed is open but only partially "
    "effective — the concentration is falling but not fast enough. "
    "The only remaining option is cutting the main power to eliminate the static discharge "
    "source. The panel is inside the gas zone.",
    # recovery
    "You go into the gas zone for thirty seconds — one breath, no mask — and hit the "
    "main disconnect. Power drops. The static discharge risk drops with it. "
    "The gas continues venting but won't ignite without a spark.",
    # victory
    "The blowout continues but without ignition risk. Emergency response reaches the "
    "site forty minutes later and completes the well control. All three workers "
    "are alive. The rig is salvageable.",
    # partial
    "The ignition risk is eliminated but the rig took structural damage from a pressure "
    "surge during the bleed process. Two workers are safe; the third is hospitalised "
    "with gas inhalation from the delay.",
    # defeat
    "The ignition threshold is reached before the static source is eliminated. "
    "The rig ignites. You and the workers are far enough away. The rig is not.",
    "Close the secondary manual preventer valve", "tech", 9,
    "Get all three workers off the drill floor", "composure", 8,
    "Open the emergency bleed valve from the control shack", "tech", 8,
    "Get the immobile worker to safety and reach the valve", "composure", 9,
    "Go into the gas zone and cut main power", "composure", 9,
    "Hit the main disconnect before the threshold is reached", "composure", 9,
    "Confirm power is down and ignition risk is eliminated", "tech", 8,
    "Account for all three workers after the power cut", "composure", 7,
    "Move everyone to minimum safe distance from the rig", "tactics", 7,
    "Signal for emergency response and document the incident", "tactics", 6,
),

_mk("tm_w23", "Blinded", "wasteland", "wasteland_23_solar_mirror_desert",
    "Cross a solar mirror desert at peak hours with a damaged navigator.", 90, 3,
    "The mirror arrays were built to power the pre-war eastern grid. They still work. "
    "At noon, the reflection intensity across the salt flat is blinding and heats the "
    "ground surface to fifty degrees. Your navigation system took damage from debris "
    "and is giving you a heading offset you can't quantify. "
    "You have to cross before the arrays track to afternoon angle.",
    # a_ok
    "You shadow-trace the navigation offset against the sun position and your map. "
    "The correction takes forty minutes to work out but once you have it, you run "
    "the route straight through the mirrors and reach the eastern edge in two hours.",
    # a_fail
    "Your offset calculation is wrong. You enter the mirror zone confident and find "
    "yourself heading into the densest concentration of reflective arrays. "
    "You correct course but the time loss is significant.",
    # b_ok
    "You don't use the navigation system. You find the original construction road — "
    "barely visible under sand — and follow it. It goes where the builders needed "
    "to go, which is where you need to go.",
    # b_fail
    "The construction road dead-ends at a maintenance compound that isn't on your map. "
    "The compound is occupied by a scavenger camp and they're not friendly.",
    # mid_ok
    "You're halfway across and the mirror arrays are beginning to track. The salt flat "
    "is getting hotter and the reflection intensity is peaking. You need to reduce your "
    "surface exposure or the crossing becomes physically dangerous.",
    # mid_fail
    "The scavenger camp's vehicle is following you through the mirror zone. "
    "At peak array intensity you can't safely pursue or engage — "
    "but they're not breaking off.",
    # crisis
    "A mirror array directly ahead has come off its mount — fallen and lying flat on "
    "the salt, reflecting directly upward at full intensity. Crossing it takes you "
    "through a sixty-metre concentration that will cause burns and vision damage.",
    # recovery
    "You identify the fallen array's blind spots — the mounting brackets cast shadows "
    "at the right angle. You route through the shadow corridor in under four minutes.",
    # victory
    "You clear the eastern edge of the mirror zone with twenty minutes to spare before "
    "the arrays track to afternoon angle. Your skin is hot but unburned. "
    "The scavenger vehicle turned back at the fallen array.",
    # partial
    "You cross the mirror zone but the peak intensity caught you in the last section. "
    "Minor burns, reduced vision for forty-eight hours, but you reach the eastern edge. "
    "The crossing took longer than planned.",
    # defeat
    "The fallen array is impassable without protective equipment you don't have. "
    "You turn back before the afternoon track traps you in the mirror zone.",
    "Correct the navigation offset manually", "tech", 8,
    "Follow the original construction road instead", "composure", 7,
    "Reduce surface exposure during peak intensity", "composure", 8,
    "Lose the following scavenger vehicle in the array field", "stealth", 8,
    "Navigate the fallen array's shadow corridor", "composure", 9,
    "Route through the shadows in under four minutes", "composure", 9,
    "Clear the last section of the mirror zone", "composure", 8,
    "Reach the eastern edge before afternoon track", "composure", 8,
    "Account for the following vehicle and confirm it has turned back", "tactics", 7,
    "Move clear of the mirror zone and assess conditions", "composure", 7,
),

_mk("tm_w24", "Echo Town", "wasteland", "wasteland_24_badlands_ghost_town",
    "Investigate a ghost town that has started broadcasting distress signals.", 90, 2,
    "Sixteen years ago the town was evacuated overnight — corporate environmental order. "
    "Last week it started broadcasting a 1970s distress frequency. "
    "Either someone found a pre-war transmitter, or someone was left behind. "
    "Either way, you go in.",
    # a_ok
    "The transmitter is in the town's old fire station. Someone has been maintaining it "
    "for sixteen years — not a survivor, but a vigil keeper: a man who came back "
    "six months after the evacuation and never left. He's alive and willing to go.",
    # a_fail
    "The transmitter is in the fire station but the keeper has triggered the building's "
    "old sprinkler system as a warning — the electrics are active and the structure "
    "has been modified to be difficult to enter safely.",
    # b_ok
    "You approach from the east side, call out before entering, and give the keeper "
    "enough time to respond. He opens the fire station door himself. "
    "First contact is clean.",
    # b_fail
    "The keeper disappears before you reach the fire station — he's been here sixteen "
    "years and he knows this town better than you do. "
    "He doesn't want to be found right now.",
    # mid_ok
    "The keeper has agreed to leave but won't move until he's shown the town's records "
    "to someone who might care. He has a complete archive of what happened the night "
    "of the evacuation and why he stayed. You have time to look if you want.",
    # mid_fail
    "You need to find the keeper without triggering whatever other modifications he's "
    "made to the town. He's watching from somewhere and you're on his territory.",
    # crisis
    "The keeper has been looking at the records with you for two hours. He's ready to "
    "go but the corporate surveillance drone that was triggered by the distress "
    "frequency is now ninety minutes out. If it scans the town, it will find you both.",
    # recovery
    "You take the records — physical documents, all of it — and get the keeper and "
    "the archive out on foot through the western drainage channel. "
    "The drone finds an empty town.",
    # victory
    "You, the keeper, and sixteen years of documentation reach the resistance network "
    "before the drone completes its survey. The records document the corporate "
    "environmental order in full. The keeper gets to sit in a real chair for the "
    "first time in sixteen years.",
    # partial
    "The keeper is out but the records were too heavy to take in full. You photograph "
    "the most critical documents on your device and leave the physical archive. "
    "The drone finds papers but not people.",
    # defeat
    "The drone arrives early — corporate override on the standard search delay. "
    "It identifies you both in the fire station and the corporate response team "
    "is on its way. You extract without the records.",
    "Search the town systematically for the transmitter", "tactics", 7,
    "Approach openly and give the keeper time to respond", "composure", 7,
    "Track the keeper through his modifications to the town", "stealth", 8,
    "Talk the keeper through the records and earn his trust", "influence", 7,
    "Move the keeper and the archive before the drone arrives", "tactics", 9,
    "Exit through the western drainage channel on foot", "composure", 8,
    "Get both the keeper and the records clear of the scan zone", "composure", 8,
    "Reach the resistance network before the drone completes its pass", "composure", 8,
    "Hand the records to the resistance network", "influence", 7,
    "Confirm the keeper is settled before leaving", "composure", 6,
),

_mk("tm_w25", "The Underground Route", "wasteland", "wasteland_25_smuggler_tunnel",
    "Run a critical supply chain through a contested smuggler tunnel network.", 110, 3,
    "The tunnel network runs twelve kilometres under corporate territory. "
    "It's maintained by three competing smuggler groups who each control a section. "
    "The resistance needs medical supplies on the other side and the tunnel is the only "
    "route. You navigate the politics as well as the dark.",
    # a_ok
    "The middle section's controller owes you from a prior job and you cash the favour. "
    "All three groups get a small cut of the supply value and the convoy moves "
    "through in four hours. No delays, no confrontations.",
    # a_fail
    "The middle section's debt is disputed by his deputy, who has actually taken over "
    "since your last contact. The new controller doesn't honour prior arrangements "
    "and you're stopped at the section boundary.",
    # b_ok
    "You negotiate with each section independently and run the convoy as three "
    "separate handoffs. Slower, but each group only needs to trust you for their "
    "section, not for the whole route.",
    # b_fail
    "The eastern section's controller refuses the handoff model — he wants through-route "
    "control and a larger percentage. Without the eastern section, "
    "the route doesn't complete.",
    # mid_ok
    "The convoy is moving but the third section has raised the toll after seeing "
    "the supply contents. The medical value is higher than they estimated. "
    "They want renegotiation in the tunnel.",
    # mid_fail
    "The eastern controller is blocking the tunnel exit. His demand is the full supply "
    "or nothing. The convoy has no room to turn around and the middle section "
    "is behind you.",
    # crisis
    "Both the eastern controller and the middle section controller are in the same "
    "section of the tunnel. They don't like each other and the convoy is between them. "
    "This is about to become their confrontation, not yours.",
    # recovery
    "You get between them and make one proposal: a fixed rate for tunnel use, "
    "published, non-negotiable, payable to a joint account. The first group to agree "
    "gets to be the honest broker for all future runs. Both want the role. "
    "Both agree.",
    # victory
    "The convoy exits the tunnel on the far side with full medical supplies and a "
    "new tunnel rate structure in place. The resistance network has a reliable route "
    "for the first time.",
    # partial
    "The convoy gets through but the eastern controller's renegotiation cost fifteen "
    "percent of the medical supplies as a toll-in-kind. The rest reaches the resistance.",
    # defeat
    "The confrontation in the tunnel becomes violent. The convoy is pinned in the "
    "crossfire and the medical supplies are damaged. The route is closed for the "
    "foreseeable future.",
    "Call in the favour from the middle section's controller", "influence", 8,
    "Run the convoy as three independent handoffs", "influence", 8,
    "Renegotiate the toll terms mid-tunnel", "influence", 8,
    "Find a way past the eastern controller's block", "tactics", 8,
    "Broker a joint rate structure between the controllers", "influence", 9,
    "Get both controllers to agree to the honest-broker proposal", "composure", 9,
    "Move the convoy through while the deal is still fresh", "composure", 8,
    "Exit the tunnel before the new deal is tested", "tactics", 7,
    "Hand the medical supplies to the resistance contact", "influence", 6,
    "Document the new tunnel rate structure for future runs", "influence", 6,
),

_mk("tm_w26", "Bone Ground", "wasteland", "wasteland_26_contaminated_battlefield",
    "Search and recover downed operatives from a contaminated corporate battlefield.", 120, 4,
    "The corporate battle here ended two months ago. The field is still hot — "
    "residual chemical agents, automated defense turrets that didn't get the "
    "stand-down order, and the two downed operatives somewhere in the middle of it. "
    "You have their last beacon coordinates and a contamination window of two hours.",
    # a_ok
    "You map the turret coverage zones from the perimeter and find a diagonal approach "
    "vector that keeps you in dead ground the entire way. You reach the first beacon "
    "in forty minutes. The operative is alive.",
    # a_fail
    "The turret coverage map is two months old. One unit has repositioned and covers "
    "your approach vector. You take fire from two hundred metres and have to withdraw.",
    # b_ok
    "A maintenance drone frequency you found in the corporate records still functions. "
    "You broadcast it and the turrets switch to a maintenance pause. "
    "You have twelve minutes.",
    # b_fail
    "The maintenance frequency triggers a counter-authentication challenge. "
    "The turrets respond by locking all active sectors and raising alert status.",
    # mid_ok
    "The first operative is out. The second beacon is three hundred metres further in, "
    "closer to the chemical agent pockets. Your contamination clock is at sixty minutes.",
    # mid_fail
    "You're pinned by the repositioned turret and can't reach either beacon directly. "
    "The chemical agent clock is still running. "
    "A wide flanking move adds thirty minutes but might work.",
    # crisis
    "The second operative is alive but cannot move and is in a chemical pocket. "
    "Carrying them out through the pocket means contamination exposure for both of you. "
    "Your contamination window is at twenty minutes.",
    # recovery
    "You seal your respirator to maximum and pull the operative through the pocket in "
    "six minutes. You're at threshold exposure but below the critical line. "
    "They're worse off but stable.",
    # victory
    "Both operatives are out before the contamination window closes. "
    "You're at exposure threshold and need decontamination, but you're clear. "
    "The field has given up everyone it was holding.",
    # partial
    "Both operatives are out but one took chemical exposure that will need specialist "
    "treatment. Your own exposure is within manageable limits. "
    "The second recovery was close.",
    # defeat
    "The contamination window closes while the second operative is still in the field. "
    "You extract the first operative and yourself. "
    "The second beacon continues transmitting.",
    "Map the dead ground and approach safely", "tactics", 8,
    "Broadcast the maintenance frequency to pause turrets", "tech", 8,
    "Reach the second beacon before the clock runs out", "composure", 9,
    "Use the wide flanking route to bypass the repositioned turret", "tactics", 9,
    "Pull the operative through the chemical pocket", "composure", 9,
    "Carry them out at maximum respirator seal", "composure", 9,
    "Clear the chemical zone with both operatives", "composure", 9,
    "Exit the contamination zone before the window closes", "composure", 8,
    "Confirm both operatives are stable after extraction", "medicine", 7,
    "Get both operatives to decontamination", "tactics", 7,
),

_mk("tm_w27", "Supply Denial", "wasteland", "wasteland_27_logistics_depot",
    "Destroy a corporate logistics depot without triggering an escalation response.", 110, 3,
    "The depot feeds three corporate forward bases. Taking it out starves the "
    "forward operations for two months. But if the demolition is traced to the "
    "resistance, the corporate response will be disproportionate. "
    "It needs to look like an accident.",
    # a_ok
    "You identify three fuel cells in the depot's own supply chain that are "
    "past their safe storage date. Standard industrial accident: overheated storage, "
    "exothermic reaction, cascade failure. The depot burns clean and "
    "the investigation finds negligence, not sabotage.",
    # a_fail
    "The fuel cells are fresh — new delivery, nothing near the end of the storage date. "
    "The overheated storage scenario doesn't work with the inventory record. "
    "You need a different accident.",
    # b_ok
    "You access the depot's maintenance log and find a cooling system that has been "
    "flagged but not repaired for six weeks. You accelerate the failure to tonight. "
    "The collapse is on the maintenance record. Nobody looks further.",
    # b_fail
    "The maintenance log access triggers a security alert — the system has a read-audit "
    "you didn't account for. Security is reviewing access logs and you need "
    "to clean the trail.",
    # mid_ok
    "The fire is running. The depot's emergency suppression system failed with the "
    "cooling collapse — also in the maintenance log. "
    "You're watching from the perimeter when a security officer starts "
    "photographing the perimeter fence for post-incident analysis.",
    # mid_fail
    "The security alert log shows an access event that could be traced. "
    "You need to clean it from inside the system before the investigation starts. "
    "The depot is still burning.",
    # crisis
    "The security officer has photographed the access point you used and is calling "
    "it in. If the corporate investigators tie the access point to the maintenance "
    "log compromise, the accident narrative collapses.",
    # recovery
    "You intercept the officer's radio call — a low-tech radio jammer from thirty metres. "
    "The call doesn't complete. The officer looks at his radio, shrugs, "
    "and goes back to the burning depot.",
    # victory
    "The depot burns. The investigation finds negligence — a cooling system "
    "that failed after six weeks of documented non-repair. Corporate HR has "
    "questions for the facilities manager. Nobody has questions for you.",
    # partial
    "The accident narrative holds but the access log was partially recovered "
    "by the investigators. They find an anomaly they can't explain but "
    "also can't trace. The depot is still gone.",
    # defeat
    "The security officer's photographs and the access log anomaly are enough "
    "for corporate investigators to call it sabotage. The resistance network "
    "is not named — but the forward bases are not starved.",
    "Engineer a plausible industrial accident", "tech", 8,
    "Access the maintenance log and accelerate the cooling failure", "tech", 8,
    "Prevent the perimeter photographs from being called in", "stealth", 8,
    "Clean the access log trail before investigation begins", "tech", 9,
    "Block the security officer's radio call", "tech", 8,
    "Watch the officer shrug and return to the fire", "composure", 7,
    "Confirm the accident narrative is holding", "stealth", 7,
    "Leave the perimeter before the investigation team arrives", "stealth", 8,
    "Verify that no resistance connection has been found", "tactics", 7,
    "Report the successful denial to the resistance network", "tactics", 6,
),

_mk("tm_w28", "Frequency", "wasteland", "wasteland_28_radio_shrine",
    "Recover an ancient signal from a radio shrine before it stops transmitting.", 80, 2,
    "The radio shrine has been broadcasting a pre-war signal for forty years — "
    "someone's emergency beacon that never got an answer. A resistance cryptographer "
    "says there's a secondary signal embedded in the carrier: location data for "
    "a pre-war supply cache. It broadcasts once more in six hours.",
    # a_ok
    "The shrine's operator — an old woman who has maintained the transmitter for "
    "seventeen years — has already recorded every broadcast. The embedded signal "
    "is in her archive. She hands it to you when you explain what it means.",
    # a_fail
    "The archive was damaged by a lightning strike three months ago. The most recent "
    "recordings are gone. You have to work with the live broadcast and whatever "
    "equipment you brought.",
    # b_ok
    "Your signal analyzer captures the carrier wave cleanly and the cryptographer's "
    "extraction algorithm runs in forty minutes. The secondary signal resolves "
    "to a grid reference twelve kilometres north.",
    # b_fail
    "The carrier wave has degraded over forty years. Your analyzer can't distinguish "
    "the embedded signal from the natural degradation noise. "
    "You need a cleaner signal path.",
    # mid_ok
    "You have the grid reference. But the operator is asking you what the original "
    "beacon was — whose emergency it was. She has been maintaining it for seventeen "
    "years and she deserves an answer if you have one.",
    # mid_fail
    "The degraded carrier wave is the only data source and you have four hours before "
    "the final broadcast. You need a way to boost the signal or filter the noise.",
    # crisis
    "The transmitter is fading faster than expected — the broadcast may not make the "
    "full six-hour window. If it stops in the next ninety minutes, the carrier wave "
    "drops below extraction threshold.",
    # recovery
    "The operator knows every component in the transmitter. With her guidance, "
    "you boost the output manually — pulling from a battery pack that wasn't "
    "designed for this load. It holds.",
    # victory
    "The full broadcast runs. The secondary signal extracts cleanly. The grid reference "
    "and the original beacon's identity — a corporate evacuation team from the "
    "eastern grid collapse — go into the resistance records together.",
    # partial
    "The grid reference extracts before the transmitter fades. The original beacon's "
    "identity remains unknown — the signal degradation ate that layer. "
    "The cache location is secured.",
    # defeat
    "The transmitter fades below extraction threshold before the secondary signal "
    "resolves. The grid reference is lost and the operator watches forty years "
    "of maintenance end without an answer.",
    "Access the shrine operator's archive", "influence", 7,
    "Capture and decode the live carrier wave", "tech", 8,
    "Boost the transmitter output with external power", "tech", 8,
    "Filter the noise to reach extraction threshold", "tech", 9,
    "Boost the transmitter manually with the operator's guidance", "tech", 9,
    "Hold the boost long enough for the full broadcast", "composure", 8,
    "Complete the secondary signal extraction", "tech", 8,
    "Verify the grid reference before the broadcast ends", "tech", 8,
    "Answer the operator's question about the original beacon", "influence", 7,
    "Pass the grid reference to the resistance cryptographer", "tactics", 6,
),

_mk("tm_w29", "Buried Intelligence", "wasteland", "wasteland_29_ewaste_landfill",
    "Recover corporate intelligence buried in an e-waste landfill before rivals get to it.", 100, 3,
    "The data centre drive was supposed to be destroyed. Instead it ended up in the "
    "e-waste landfill with thirty thousand tonnes of pre-war electronics. "
    "Corporate intelligence puts a recovery team on the site in four hours. "
    "Your contact has a general grid reference. The rest is digging.",
    # a_ok
    "You read the landfill stratigraphy — the data centre waste would have arrived in "
    "a specific window and been buried under three later deposits. "
    "You dig in the right place and find the drive in two hours.",
    # a_fail
    "The stratigraphy is disrupted by a landslide six months ago that mixed the layers. "
    "Your estimated location is wrong and you've spent ninety minutes on a "
    "false seam.",
    # b_ok
    "Your signal scanner picks up the drive's residual passive transmission — "
    "a dead-battery low-frequency ping that data drives emit for years after "
    "power-off. You triangulate it in twenty minutes.",
    # b_fail
    "Three other drives in the same section are emitting the same frequency — "
    "the same batch, same manufacture date. "
    "You can't triangulate which one without pulling all three.",
    # mid_ok
    "You have the drive — or one of the candidate drives. The corporate recovery team "
    "is ninety minutes out and you need to read the drive to confirm it's the right one "
    "before you leave. The verification process takes forty minutes.",
    # mid_fail
    "You've pulled all three candidate drives and they look identical. "
    "You're going to have to take all three, which means sixty kilograms of e-waste "
    "hardware on a four-kilometre walk back to your vehicle.",
    # crisis
    "The corporate recovery team is early. They're at the landfill perimeter and "
    "you're still in the dig site with the drive — verified or not.",
    # recovery
    "You go vertical — under the nearest debris mound, not away from the site. "
    "The recovery team sweeps the open section while you're three metres below them "
    "in a hollow under the pile.",
    # victory
    "The recovery team sweeps and leaves. They found nothing. You walk out forty "
    "minutes after they do, drive confirmed, corporate intelligence in hand.",
    # partial
    "You exit the site with all three candidate drives before the team sweeps your "
    "section. The correct drive is among them. It'll take a day to identify which "
    "one, but the intelligence is secured.",
    # defeat
    "The recovery team finds you in the dig site. You abandon the drives and exit "
    "the landfill before their response team deploys. The corporate intelligence "
    "is recovered by the corporate team.",
    "Read the landfill stratigraphy to locate the drive", "tech", 8,
    "Triangulate the drive using its residual passive transmission", "tech", 7,
    "Verify the drive's contents before leaving", "tech", 8,
    "Carry all three candidate drives out on foot", "composure", 8,
    "Hide in the debris mound while the recovery team sweeps", "stealth", 8,
    "Stay under the pile until the team leaves", "composure", 9,
    "Exit the landfill after the team departs", "stealth", 8,
    "Confirm the drive contents on exit", "tech", 7,
    "Move the drive to a secure location", "tactics", 7,
    "Pass the intelligence to the resistance network", "tactics", 6,
),

_mk("tm_w30", "Last Gate", "wasteland", "wasteland_30_storm_checkpoint",
    "Get a critical resistance asset through a corporate checkpoint during a storm.", 130, 4,
    "The checkpoint closes for no one — storm or no storm. The resistance asset is a "
    "person who cannot afford to be scanned: the resistance network's chief cryptographer, "
    "burned identity, flagged biometrics, carrying six months of encrypted communications "
    "in her head. She needs to be on the other side of the checkpoint by dawn.",
    # a_ok
    "You run the asset through the storm's worst hour — visibility at three metres, "
    "checkpoint scanners degraded by static, guards pulled inside. "
    "The gate logs show a maintenance closure during the storm's peak. "
    "You're through before it reopens.",
    # a_fail
    "The checkpoint has backup power and the scanners run on it through the storm. "
    "The maintenance closure window doesn't open. "
    "You're outside the checkpoint fence in a toxic storm with a burned asset.",
    # b_ok
    "The checkpoint has a customs transit log — vehicles with emergency credentials "
    "can pass with reduced scanning. You have a medical vehicle ID that has never "
    "been flagged. Emergency medical transit, one patient, no delay.",
    # b_fail
    "The checkpoint supervisor has flagged all emergency transit tonight following "
    "an earlier incident. Your medical vehicle ID goes into full secondary scan.",
    # mid_ok
    "The asset is through the checkpoint's outer gate but the inner biometric scanner "
    "is operational. One guard, one scanner, two metres of corridor between the outer "
    "and inner gate.",
    # mid_fail
    "You're in the secondary scan facility. The scanner operator is methodical and the "
    "asset's biometric flag is three seconds away from surfacing. "
    "You need a disruption in the next two seconds.",
    # crisis
    "The biometric flag has surfaced on the scanner screen. The guard is looking at it. "
    "The asset is standing in the scanner corridor. The inner gate is still closed. "
    "You have about four seconds before he reaches for his radio.",
    # recovery
    "You interrupt — loudly — with a question about the vehicle's documentation that "
    "you know will require the guard to open a different system. He looks at you. "
    "The asset walks to the inner gate and puts her hand on it.",
    # victory
    "The gate releases on the guard's automatic approval before he can re-examine "
    "the screen. The asset is through. You follow on the documentation clearance. "
    "By the time the guard looks at the biometric screen again, the corridor is empty.",
    # partial
    "The asset is through but the guard's post-shift review flags the biometric anomaly. "
    "The resistance network has a short window to move the asset again before "
    "the flag is processed.",
    # defeat
    "The guard reaches his radio before the distraction lands. The checkpoint goes "
    "to lock-down protocol. The asset is detained in the scanner corridor.",
    "Run the asset through the storm scanner blackout", "stealth", 9,
    "Use the medical emergency transit credential", "influence", 8,
    "Move the asset through the inner gate biometric corridor", "stealth", 9,
    "Create a disruption to break the guard's focus", "composure", 9,
    "Get the guard to open documentation before he re-examines the screen", "influence", 9,
    "Walk through the inner gate on the documentation clearance", "composure", 9,
    "Exit the checkpoint before the guard can review the screen", "composure", 9,
    "Confirm the asset is clear on the far side", "composure", 8,
    "Move the asset away from the checkpoint perimeter", "tactics", 8,
    "Deliver the asset to the resistance safe house", "tactics", 7,
),

]  # end _WASTE_2 (tm_w16–tm_w30)


# ── Public API ─────────────────────────────────────────────────────────────────

_ALL_MISSIONS: list[TextMissionTemplate] = _CITY + _CITY_2 + _CITY_3 + _WASTE + _WASTE_2

_BY_ID: dict[str, TextMissionTemplate] = {m.id: m for m in _ALL_MISSIONS}


def all_text_missions() -> list[TextMissionTemplate]:
    return list(_ALL_MISSIONS)


def get_text_mission(mission_id: str) -> TextMissionTemplate | None:
    return _BY_ID.get(mission_id)


def text_missions_for_day(calendar_day: int, count: int = 6) -> list[TextMissionTemplate]:
    """Return a stable, day-keyed subset of missions for the world map board."""
    import hashlib
    import random as _r
    seed = int(hashlib.md5(f"textmissions_{calendar_day}".encode()).hexdigest()[:8], 16)
    rng = _r.Random(seed)
    pool = list(_ALL_MISSIONS)
    rng.shuffle(pool)
    return pool[:min(count, len(pool))]
