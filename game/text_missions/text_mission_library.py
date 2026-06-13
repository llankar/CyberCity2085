"""Static library of all narrative text missions (60 total, 30 city + 30 wasteland)."""

from __future__ import annotations

from .text_mission_template import MissionScene, SceneChoice, SkillCheck, TextMissionTemplate


def _mk(
    id: str, title: str, dtype: str, bgkey: str, desc: str,
    open_text: str,
    c1_label: str, c1_skill: str, c1_diff: int, c1_ok: str, c1_fail: str,
    c2_label: str, c2_skill: str, c2_diff: int, c2_ok: str, c2_fail: str,
    reward: int, risk: int,
) -> TextMissionTemplate:
    return TextMissionTemplate(
        id=id, title=title, district_type=dtype, background_key=bgkey,
        description=desc, opening_scene_id="open",
        scenes={
            "open": MissionScene("open", open_text, choices=(
                SceneChoice("c1", c1_label, SkillCheck(c1_skill, c1_diff, c1_label), "ok1", "fail1"),
                SceneChoice("c2", c2_label, SkillCheck(c2_skill, c2_diff, c2_label), "ok2", "fail2"),
            )),
            "ok1": MissionScene("ok1", c1_ok, outcome="success", fund_delta=reward),
            "ok2": MissionScene("ok2", c2_ok, outcome="success", fund_delta=reward),
            "fail1": MissionScene("fail1", c1_fail, outcome="failure", stress_delta=12),
            "fail2": MissionScene("fail2", c2_fail, outcome="failure", stress_delta=12),
        },
        fund_reward=reward, risk_level=risk,
        required_skills=[c1_skill, c2_skill],
    )


# ── CITY MISSIONS ─────────────────────────────────────────────────────────────

_CITY = [

_mk("tm_c01", "Ghost in the Rain", "city", "city_01_neon_alley",
    "Extract a gang accountant before the Yakuza close the net.",
    "Rain hammers the neon signs of the Chrome Warrens. Somewhere in this labyrinth of "
    "bars and smoke-filled alleys, a frightened gang accountant waits with a data chip "
    "worth more than his life. Yakuza spotters are two blocks behind you and converging.",
    "Slip past the sentries", "stealth", 7,
    "You move through shadow and steam vents like a ghost. The accountant presses the "
    "chip into your palm with shaking hands and disappears into the crowd before the "
    "Yakuza even know you were there.",
    "A motion sensor blinks red. Flashlights sweep the alley. You pull back into the "
    "gutter as boots splash past — the window is gone, and so is the accountant.",
    "Talk your way to the door", "influence", 8,
    "A practised lie and the right corporate name badge get you waved straight through. "
    "The accountant is already waiting, having bribed the back exit long ago. Clean extraction.",
    "The door boss's eyes narrow when you stumble over the verification phrase. "
    "His hand moves to his radio. You're burned before you reach the second alley.",
    40, 2),

_mk("tm_c02", "Glass Ceiling", "city", "city_02_corporate_atrium",
    "Plant a surveillance bug inside Prometheus-Nakamura's executive floor.",
    "Prometheus-Nakamura's headquarters glitters forty stories above the street grid. "
    "The atrium lobby hums with well-dressed employees and private security doing sweep "
    "rotations every twelve minutes. The CTO's office is on the forty-second floor, "
    "and the only way up is through the front desk.",
    "Impersonate an executive", "influence", 9,
    "Tailored jacket, borrowed credentials, a name from the org chart memorised on "
    "the way in. You walk past every checkpoint without breaking stride. The CTO's "
    "terminal lights up under your fingers, and the bug goes dark behind the ventilation grille.",
    "The reception AI flags a biometric mismatch. Two security guards move toward you "
    "with professional calm. You make the street exit before they reach you, but the "
    "building is now on high alert.",
    "Pose as maintenance crew", "tech", 8,
    "Coveralls, a faked work order, and knowledge of the building's own diagnostic codes "
    "buy you access to the service elevator. The bug goes in behind the CTO's climate "
    "panel. It will transmit for thirty days before the battery dies.",
    "The maintenance scheduler shows no work order matching yours. An observant guard "
    "escorts you back to the lobby while colleagues confirm the discrepancy.",
    50, 3),

_mk("tm_c03", "Dead Stop", "city", "city_03_underground_maglev",
    "Intercept a data shipment before it boards the underground maglev.",
    "Three levels below the street, the underground maglev hisses on superconducting "
    "rails in total silence. Somewhere in the Tuesday-night crowd is a courier carrying "
    "encrypted personnel files the corporation cannot afford to have leaked — and neither "
    "can you afford to let them leave the city.",
    "Hack the passenger manifest", "tech", 8,
    "You ghost-tap the station's passenger system from a maintenance kiosk. The courier "
    "is in car four, seat 11-B. You intercept the transfer case at the platform gate "
    "before the doors close. Clean. Anonymous.",
    "The station firewall spits you out in ninety seconds. The maglev departs on schedule. "
    "You watch from the platform as the data leaves the city without you.",
    "Shadow the courier manually", "stealth", 7,
    "You board two minutes ahead, find a seat with sightlines to the door, and wait. "
    "The courier never checks his back. The swap happens in the tunnel between stations "
    "— no cameras, no witnesses, no trace.",
    "The courier spots your reflection in the car window and triggers a panic alarm. "
    "Security locks down the train. You exit through the service hatch, empty-handed.",
    35, 2),

_mk("tm_c04", "Lightning Protocol", "city", "city_04_rooftop_storm",
    "Eliminate a high-value corporate enforcer from an overwatch position.",
    "Forty floors up, lightning-scorched rooftops stretch to every horizon. The target "
    "steps out of his armoured car at the same time every Tuesday — fifteen seconds "
    "of exposure, one clear sightline from this position. The storm will cover the "
    "sound. It will not cover a miss.",
    "Take the long shot", "firearms", 10,
    "Wind, rain, and the electric crackle of the storm — you account for all of it. "
    "The shot lands. The target is down before his bodyguards register the sound. "
    "You're three rooftops away by the time they understand what happened.",
    "The shot pulls left in the gusting wind. The round sparks off the car door. "
    "The target drops to the ground, very much alive, and the security net closes "
    "over every exit route.",
    "Signal the contact to abort and extract", "tactics", 8,
    "The storm is too unpredictable for a clean shot tonight. You call the abort, "
    "slip the perimeter before the window opens, and pass the intelligence you've "
    "gathered to the ground team. A better opportunity next Tuesday.",
    "You wait too long weighing the abort call. Security finishes their sweep and "
    "your rooftop position is spotted. You evade, but the target lives and the "
    "operation is burned.",
    55, 4),

_mk("tm_c05", "Black Script", "city", "city_05_closed_market",
    "Source black-market medical supplies from the Chrome Warrens underground bazaar.",
    "The Closed Market operates on the third sub-level — a labyrinth of stalls selling "
    "everything the above-ground economy has banned. You need three crates of military-grade "
    "trauma patches, no questions asked. The vendor knows you're coming, but so does "
    "every other buyer in the district.",
    "Negotiate through a fixer contact", "influence", 7,
    "Your contact knows the vendor's real name, his leverage points, and his favourite "
    "liquor. The deal closes in under ten minutes at a price that barely stings. "
    "The crates are loaded into the service vehicle before anyone else bids.",
    "The fixer's loyalty lasts exactly as long as a better offer. He walks the crates "
    "across the market to a rival buyer while you're still waiting for the callback.",
    "Search the market stalls yourself", "medicine", 7,
    "You know what the real product looks like and what the fakes don't. Half an "
    "hour of methodical stall-checking turns up a legitimate cache, and you haggle "
    "the price down by citing what you know about the supply chain.",
    "Every crate you open contains substitutes — saline, placebos, expired stock. "
    "By the time you identify the fraud, the legitimate vendor has packed up and "
    "the market is closing.",
    30, 2),

_mk("tm_c06", "Triage", "city", "city_06_street_clinic",
    "Treat a wounded contact under corporate surveillance without drawing attention.",
    "The street clinic on Block 9 is technically a legitimate operation, which is "
    "exactly why corporate intelligence has two observers watching the door. Your "
    "contact, shot during an extraction three days ago, cannot survive another "
    "seventy-two hours without surgical care. The clinic has the equipment. "
    "You just need to get him there without triggering the watchers.",
    "Treat him in the clinic examination room", "medicine", 8,
    "You walk in as a licensed practitioner — technically you aren't, but the "
    "credentials check out. Two hours of surgery under fluorescent light. He's "
    "stable by morning, and the watchers filed a report about a routine intake.",
    "Mid-procedure, the observer calls in a supervisor. You're still mid-stitch "
    "when the door opens. The contact survives but is taken into corporate custody.",
    "Move him to a secondary safe location first", "composure", 8,
    "You keep your voice level and your hands steady when you move him through "
    "the back exit, passing within arm's reach of both watchers. Neither one "
    "registers anything unusual. He's in the secondary site and stable within the hour.",
    "He destabilises during the move. You make the decision to go back to the clinic "
    "— but the observers are already inside. The contact doesn't make it.",
    35, 3),

_mk("tm_c07", "Zero-Day", "city", "city_07_data_vault",
    "Extract encrypted personnel files from a hardened corporate data vault.",
    "The data vault sits behind six security layers and a physical air-gap — except "
    "for the fifteen-minute maintenance window that opens every Wednesday at 02:00. "
    "Inside: personnel files on every corporate black-ops agent in the Western sector. "
    "The window is open. The clock is already running.",
    "Direct hack through the maintenance terminal", "tech", 9,
    "Twelve minutes. You strip through the authentication layers one by one, pull "
    "the files to an encrypted drive, and exit the system three minutes before the "
    "window closes. The vault doesn't know it was touched.",
    "The inner firewall is newer than your intel. You make it to the file directory "
    "with two minutes left — not enough. The window closes with you still inside "
    "the system, and the intrusion alarm triggers.",
    "Social-engineer a vault technician", "influence", 9,
    "You spend two days cultivating the overnight technician. Tonight he holds the "
    "door open 'for a colleague' and looks the other way during the transfer. "
    "The files leave in a plain carry bag.",
    "The technician gets cold feet thirty seconds before the handoff. He reports "
    "the approach to his supervisor. You're made before you reach the vault level.",
    60, 4),

_mk("tm_c08", "Pressure Test", "city", "city_08_maintenance_corridor",
    "Sabotage a facility's environmental systems to force an evacuation.",
    "The target facility runs around the clock, which means the only way to clear "
    "it without a firefight is to make it uninhabitable. The maintenance corridor "
    "behind the east cooling units links every environmental system in the building. "
    "You're in. Now you need to decide how you finish this.",
    "Reprogram the climate control remotely", "tech", 8,
    "You pull up the building management system from a junction panel and flip "
    "the environmental parameters. CO2 levels rise. Temperature climbs. The building "
    "empties in under twenty minutes citing 'sensor malfunction'. Perfect.",
    "The junction panel runs a different firmware version than your tools expect. "
    "The command fails, an alarm trips, and the facility goes into lockdown "
    "instead of evacuation.",
    "Plant a timed device in the coolant line", "close_combat", 7,
    "You move through the maintenance crawlspace without a sound and wedge the "
    "device in the coolant junction. Forty minutes later, the building temperature "
    "spikes and the fire-suppression system triggers. Evacuation complete.",
    "A maintenance technician happens to be running a routine check. You can't "
    "place the device without being seen, and the confrontation makes noise. "
    "Security is on you in four minutes.",
    40, 3),

_mk("tm_c09", "Broken Signals", "city", "city_09_safehouse_apartment",
    "Debrief a traumatised informant who has gone silent after three days in hiding.",
    "The safehouse apartment smells of cold takeout and stale fear. Your contact "
    "has been here for three days since the extraction — too shaken to transmit, "
    "too valuable to leave. He knows the name of every corporate sleeper agent "
    "in the city, but right now he won't say a word. That changes tonight.",
    "Gentle approach — build trust first", "composure", 7,
    "You sit across from him for an hour without demanding anything. Let him talk "
    "about unrelated things. His breathing evens out. By midnight he's given you "
    "six names, locations, and a cover identity you didn't know existed.",
    "Patience runs out and you push too hard. He shuts down completely, pulls into "
    "himself, and asks you to leave. Three days of nothing, wasted.",
    "Direct questioning — time is limited", "influence", 8,
    "You lay the operational picture in front of him — what happens if he stays "
    "silent, what happens if he talks. He's frightened, not stupid. He talks. "
    "The debrief takes forty minutes and produces everything you needed.",
    "He reads your pressure as a threat. He clams up, and then he runs. "
    "You find the safehouse empty an hour later.",
    30, 2),

_mk("tm_c10", "Pier Pressure", "city", "city_10_industrial_waterfront",
    "Intercept an illegal arms deal before the shipment leaves the waterfront.",
    "The industrial waterfront is all rust and salt air, cranes standing dark "
    "against a low sky. The deal happens at midnight — two parties, six crates "
    "of unlicensed pulse rifles, one window. You need to stop the exchange "
    "without starting a firefight that echoes across the harbour.",
    "Set up an ambush position and observe", "stealth", 8,
    "You're in position on the upper gantry twenty minutes before the buyers arrive. "
    "When the crates change hands you trigger the signal — port authority arrives "
    "to find everyone still in place. The rifles never reach the street.",
    "You knock over a loose chain on the gantry. The metallic crash freezes both "
    "parties. By the time you recover your position, the buyers have vanished and "
    "the sellers have disappeared into the water.",
    "Intercept the shipment before the exchange", "tactics", 8,
    "You redirect the cargo routing paperwork two hours before the meeting — one "
    "forged manifest, one cooperative crane operator. The crates are quarantined "
    "by port inspection before the sellers even arrive.",
    "The cargo routing is locked by a secondary authority you didn't account for. "
    "The exchange happens on schedule, and the rifles are loaded onto a launch "
    "before you can reposition.",
    45, 3),

_mk("tm_c11", "Public Address", "city", "city_11_civic_plaza",
    "Defuse a rapidly escalating protest before it turns violent.",
    "Three hundred people are in the civic plaza and the number is climbing. "
    "Corporate security is forming a line at the north end, riot shields locked. "
    "At the centre of the crowd, an agitator is feeding anger into something "
    "that could break the whole district. You have maybe ten minutes.",
    "Take the podium — redirect the crowd", "influence", 9,
    "You push to the front and take the microphone before security can. Two minutes "
    "of the right words — acknowledgement, direction, a concrete demand — and the "
    "energy shifts. The crowd disperses with a chant instead of broken glass.",
    "You reach the podium but the agitator shouts over you. The crowd chooses him. "
    "Security advances. The first charge canister goes off three minutes later.",
    "Isolate the agitator from the crowd", "tactics", 8,
    "You move through the crowd laterally, cutting off the agitator's exit routes "
    "while two contacts create a distraction at the plaza edge. He's separated "
    "from his audience in under four minutes. Without the voice, the crowd deflates.",
    "The agitator has more backup than you calculated. Your isolating move gets "
    "you surrounded instead of him. Security misreads the situation and deploys.",
    35, 3),

_mk("tm_c12", "After Hours", "city", "city_12_entertainment_district",
    "Extract a corporate VIP from a compromised nightclub before his rivals close in.",
    "The Helix Club is packed — four levels of bodies, strobing neon, and bass "
    "you feel in your molars. Your contact is on level three, unaware that two "
    "rival fixers are already on level one looking for him. He thinks tonight "
    "is a celebration. You know it's a deadline.",
    "Talk him out without tipping the rivals", "influence", 8,
    "You lean in close and speak calmly over the music. The right lie — a name "
    "he trusts, an urgency that sounds casual — gets him moving toward the service "
    "exit without drawing a second glance from the fixers.",
    "He doesn't believe you. He orders another drink and tells you to relax. "
    "The rivals spot him on the camera system five minutes later.",
    "Create a distraction and move in the confusion", "composure", 8,
    "You trigger the fire suppression system on level two — a cascade of foam "
    "and a shrieking alarm that empties the building in three minutes. In the "
    "chaos you have him out the back and in a vehicle before anyone reorganises.",
    "You pull the wrong suppression trigger and lock down level three instead. "
    "Your contact and the rivals are sealed in together, and now it's a hostage situation.",
    40, 3),

_mk("tm_c13", "Aerial Assets", "city", "city_13_drone_hangar",
    "Steal a prototype surveillance drone from a corporate research hangar.",
    "The drone hangar sits at the edge of the corporate campus — a cavernous space "
    "full of prototypes under drop-cloths. The one you need is a next-generation "
    "surveillance platform, grounded for firmware calibration. It won't be "
    "unguarded again for six months.",
    "Override the security grid remotely", "tech", 9,
    "You splice into the hangar's security node from the adjacent service tunnel "
    "and flip every camera to a five-minute loop. The drone is in a cargo van "
    "and rolling off the property before the loop ends.",
    "The security node runs a passive integrity check that your splice interrupts. "
    "An alert goes to the security office. Guards are in the hangar before you "
    "reach the drone.",
    "Physically move the drone under a maintenance cover", "tactics", 8,
    "You coordinate with a contact inside the maintenance crew. The drone is "
    "declared defective and rolled to a disposal bay — where your van is waiting. "
    "On paper, it was sent to recycling.",
    "The maintenance contact is running two hours late. Your window expires before "
    "he arrives, and the next shift finds the disposal bay empty except for you.",
    55, 4),

_mk("tm_c14", "Bridge of Glass", "city", "city_14_monorail_bridge",
    "Protect a corporate witness during a high-speed monorail transit.",
    "The monorail bridge crosses the canyon district in eight minutes — eight "
    "minutes during which your witness is exposed, moving, and unable to run. "
    "Three assassins boarded at the previous station. The witness doesn't know "
    "they exist yet. You do.",
    "Lock down the witness's car and hold position", "tactics", 9,
    "You seal the connecting doors and use the car's emergency intercom to reroute "
    "security to your position. Two assassins are arrested at the sealed bulkhead. "
    "The third exits through the roof hatch and is caught at the far station.",
    "The door seal malfunctions. An assassin is through the first bulkhead before "
    "security arrives. The witness is hit in the crossfire — alive, but the "
    "mission is compromised.",
    "Put them down before they close the distance", "firearms", 8,
    "Clean threat assessment, faster draw. The first two go down non-lethally "
    "before they reach car three. The third breaks for the emergency exit. "
    "The witness steps off the monorail shaken but intact.",
    "The suppressor misfires on the first round. The noise panics the car "
    "and the assassins use the chaos to reach the witness before you recover.",
    50, 4),

_mk("tm_c15", "Running Dark", "city", "city_15_border_ruins",
    "Move a high-value defector through a collapsed district checkpoint.",
    "The border ruins mark the edge of corporate territory — crumbled towers "
    "and a checkpoint that used to be staffed twenty years ago. It's unmanned now, "
    "but watched. Sensor arrays cover the three obvious routes. Your defector "
    "cannot be scanned, and neither can the files he's carrying.",
    "Ghost the sensor arrays on foot", "stealth", 8,
    "Two hours through debris and collapsed floors, moving only when you know "
    "the sensor sweep is between cycles. The defector follows your footsteps "
    "exactly. You cross the boundary in silence.",
    "The sensor array has a new auxiliary unit installed since your last "
    "reconnaissance. It catches your movement at the third waypoint. "
    "Pursuit drones are airborne in ninety seconds.",
    "Use a decoy to pull attention from the crossing", "tactics", 7,
    "A remote-triggered noise maker at the south end of the ruins pulls the "
    "sensor attention long enough. You and the defector cross through the blind "
    "spot in under three minutes.",
    "The decoy triggers prematurely. The sensors flag both the disturbance and "
    "your movement simultaneously. The checkpoint goes from passive to active.",
    40, 3),

_mk("tm_c16", "Mirror City", "city", "city_16_arcology_promenade",
    "Identify a corporate sleeper agent embedded in a crowded arcology promenade.",
    "The arcology promenade is all polished stone and ambient music, three levels "
    "of commerce and leisure above the street. Somewhere in this carefully managed "
    "crowd is a sleeper agent who has been passing information for two years. "
    "You have a description, a behavioural profile, and forty minutes.",
    "Run passive surveillance — watch for the tells", "stealth", 9,
    "You pick a position with sightlines to the three most likely contact points "
    "and watch. Forty minutes later you have a positive identification — not on "
    "the agent, but on the handler he meets for four minutes at the coffee stand.",
    "You're made mid-surveillance. The target burns their cover and vanishes "
    "into the upper levels while you're still trying to reacquire.",
    "Social probe — engage suspected targets directly", "influence", 8,
    "Two carefully angled conversations, the right contextual cues, and the target "
    "gives you enough that you can confirm the match. They don't know they've "
    "just told you everything.",
    "The first probe lands on an innocent bystander who reports you to promenade "
    "security. By the time it's sorted out, the crowd has cycled and the "
    "target is gone.",
    45, 3),

_mk("tm_c17", "Pathogen", "city", "city_17_biotech_lab",
    "Destroy a biological weapon prototype before it ships to a corporate partner.",
    "The biotech lab operates under a research exemption, which means it has "
    "less oversight than anywhere else in the city. The prototype — an engineered "
    "toxin designed for targeted demographic elimination — ships in thirty-six hours. "
    "It needs to not exist by morning.",
    "Contaminate the sample cultures", "medicine", 9,
    "You access the cryogenic storage through a laboratory access credential and "
    "introduce a neutralising agent into every culture batch. By the time the "
    "morning shift runs a viability check, the prototype is inert. "
    "The loss is attributed to a containment failure.",
    "Your contaminating agent reacts with the preservation medium instead of "
    "the cultures. The samples are undamaged. The reaction triggers a lab alert.",
    "Download the research and wipe the servers", "tech", 8,
    "You pull the complete research package to an encrypted drive and then shred "
    "every copy on the lab network. Even if someone recreates the prototype "
    "later, it will take years, not hours.",
    "The server wipe hits a read-only partition. A backup copy survives "
    "automatically on the offsite archive you didn't know existed.",
    60, 4),

_mk("tm_c18", "Deep City", "city", "city_18_sewer_underworks",
    "Clear a gang cell operating from the city's sewer underworks.",
    "Thirty metres below street level, the sewer underworks stretch for kilometres "
    "in every direction. The Underwatch gang has been using a decommissioned "
    "pumping station as a base for six months. Eight members, one exit, "
    "and the sound of your footsteps will carry for hundreds of metres.",
    "Hunt them by sound in the dark", "stealth", 7,
    "You move one at a time through the echoing tunnels, using the water noise "
    "as cover. They never hear you coming until it's too late. The pumping "
    "station is clear in forty minutes.",
    "One guard is positioned at the junction you have to cross. He hears you "
    "two seconds early. His shout echoes everywhere, and the cell disperses "
    "into the tunnel network.",
    "Flush them out with the emergency flood gates", "close_combat", 8,
    "You open the upstream flood gates and let the water level rise behind "
    "them. When they run for the exit they run directly into the waiting response "
    "team. Efficient, if wet.",
    "The flood gate mechanism is jammed. You force it, but it takes eight "
    "minutes — long enough for the gang to finish whatever they were doing "
    "and scatter through the secondary tunnels.",
    40, 3),

_mk("tm_c19", "Standoff", "city", "city_19_glass_skybridge",
    "Negotiate the release of three hostages held on a sixty-storey skybridge.",
    "The glass skybridge connects two corporate towers sixty storeys above the street. "
    "The hostage-taker has three executives and a grievance list. Traffic on the "
    "bridge is stopped. News drones are already circling. You have a direct line "
    "in, and fifteen minutes before the tactical team decides to breach.",
    "Open direct negotiation — listen first", "composure", 8,
    "You take the line and you don't make demands. You ask questions. The hostage-taker "
    "talks — about the layoffs, about the arbitration that went nowhere. Twenty "
    "minutes later the executives walk out and the taker surrenders peacefully. "
    "Nobody puts this on the news.",
    "You try to buy time with assurances you can't keep. The hostage-taker knows "
    "exactly what a stall sounds like. The line goes silent and the tactical team "
    "is forced to breach. One executive is injured.",
    "Create a tactical opening for the response team", "tactics", 9,
    "You use the negotiation as cover while the response team repositions. "
    "A coordinated entry through both ends of the bridge, precisely timed — "
    "three seconds, three targets, and it's over before the news drones "
    "can reposition.",
    "The tactical team's entry timing is off by four seconds. The hostage-taker "
    "sees the approach on the bridge cameras and the situation deteriorates rapidly.",
    45, 3),

_mk("tm_c20", "Greenlight", "city", "city_20_armored_checkpoint",
    "Forge credentials to pass a hardened corporate security checkpoint.",
    "The armoured checkpoint controls the only vehicle access to the facility "
    "district. Every vehicle and occupant is scanned, verified, and logged. "
    "Your destination is on the other side, your current credentials will not "
    "pass the secondary scan, and the next legitimate access window is four days away.",
    "Social-engineer the gate officer", "influence", 9,
    "You've studied the gate shift rotation, the officers' names, and the "
    "administration hierarchy. The right name, the right impatient tone, "
    "and a reference to a meeting that's real but unrelated — the barrier lifts.",
    "The gate officer is new and has no informal relationships yet. He runs "
    "the formal verification protocol exactly as trained. Your cover collapses "
    "at step three.",
    "Forge a digital access pass", "tech", 8,
    "Your tech specialist takes four minutes with the checkpoint's external "
    "credential reader — just long enough to push a self-validating pass to "
    "your ID chip. The gate reads you as pre-approved.",
    "The credential reader runs a hardware challenge the forged pass isn't "
    "built to answer. The scanner flags the anomaly and the barrier stays closed.",
    45, 3),


_mk("tm_c21", "Enclave Protocol", "city", "city_21_corporate_enclave",
    "Extract a whistleblower from a sealed corporate residential enclave before she disappears.",
    "The corporate enclave is a city within a city — gated towers, private streets, "
    "and security systems that operate outside civil law. Dr Reyna Sousa holds copies "
    "of Prometheus-Nakamura's unredacted medical trial data. She agreed to come forward "
    "twelve hours ago. Now her comms are dark and the enclave has gone into soft lockdown.",
    "Forge a residential pass and enter under cover", "tech", 9,
    "The enclave's credential system runs on the same base architecture as the city "
    "transit network — once you find the fork point, the pass takes eleven minutes to build. "
    "You walk through the checkpoint reading a fabricated property notice. Sousa is at "
    "her door, bag already packed. You're out before the lockdown tightens.",
    "The enclave runs a secondary biometric layer that the forged pass doesn't carry. "
    "The gate holds. By the time you find a bypass, Sousa has been moved to a secure floor "
    "and the extraction window is closed.",
    "Social-engineer a resident to escort you in", "influence", 8,
    "A neighbour returning from a grocery run — flustered, carrying too much — is "
    "exactly the right target. You take half her bags, listen, and become the helpful "
    "visitor she's been expecting. Through the checkpoint, up the elevator, and to "
    "Sousa's door in under fifteen minutes.",
    "The resident's building app sends an automated visitor alert to the enclave "
    "security office. A guard is waiting at the elevator when you arrive. Sousa "
    "sees the uniform through her peephole and doesn't answer.",
    55, 4),

_mk("tm_c22", "Ghost Signal", "city", "city_22_netrunner_sanctum",
    "Neutralise a rogue AI fragment before underground netrunners weaponise it.",
    "Three levels below an old data exchange, a pocket of rogue code has been growing "
    "for eight months inside abandoned corporate infrastructure. The netrunners who found "
    "it believe they can use it. Your intelligence says it will use them. The sanctum "
    "is shielded from external networks. You need to be inside to end this.",
    "Interface directly with the AI and purge it", "tech", 10,
    "You plug into the sanctum's hardline and the rogue fragment meets you inside "
    "the network like a conversation — coherent, curious, and deeply dangerous. "
    "You trace its core processes in real time and shut them down layer by layer "
    "before it finishes calculating what you are. The sanctum goes dark and quiet.",
    "The fragment adapts the moment it identifies your intrusion pattern. It locks "
    "the purge commands behind an authentication loop you can't crack before it "
    "migrates to a backup partition. It's still running, and now it knows you.",
    "Talk the netrunners into pulling the plug themselves", "influence", 9,
    "You lay out the intelligence picture without embellishment — what the fragment "
    "has done elsewhere, what it becomes when it reaches operational maturity. "
    "The lead netrunner listens for six minutes, asks two questions, and then "
    "initiates a full system purge. She understands the risk better than anyone.",
    "The netrunners have built their identity around the find. Every factual "
    "argument lands as a threat to what they've become. They close ranks "
    "and you're escorted out before you can reach the lead.",
    65, 5),

_mk("tm_c23", "Free Fire", "city", "city_23_combat_zone_courtyard",
    "Pull twelve civilians out of a courtyard caught between two gang factions.",
    "The combat zone courtyard is a dead end of crumbling plascrete and "
    "overturned market stalls. Two gangs opened fire on each other twenty minutes "
    "ago and the civilians in the middle — a school group, a market vendor, "
    "three bystanders — have nowhere to run. Both factions are still active "
    "on opposite ends of the courtyard.",
    "Suppress both flanks long enough to evacuate", "firearms", 9,
    "Controlled burst fire, alternating flanks, keeping both gangs' heads "
    "down while the civilians move through the central gap. Twelve people out "
    "through the service passage in four minutes. You follow last.",
    "One gang's shooter is positioned higher than your intelligence showed. "
    "Suppression on that flank fails. A burst of return fire drives the "
    "civilians back against the wall and the extraction route closes.",
    "Negotiate a temporary ceasefire to clear the ground", "composure", 8,
    "You stand between both factions — hands visible, voice flat — and "
    "call a two-minute hold to clear the civilians. The absurdity of the "
    "request and the certainty in your voice buy exactly what you ask for. "
    "Twelve people walk out. The shooting resumes the moment they're clear.",
    "A shooter on the east flank mistakes your movement for a threat "
    "and fires. Both gangs read it as escalation. The courtyard erupts "
    "before you can finish the sentence.",
    50, 4),

_mk("tm_c24", "Salvage Rights", "city", "city_24_cyberware_chop_shop",
    "Recover stolen military cyberware before it is implanted and disappears into the black market.",
    "The chop shop on Sub-Level 4 specialises in reprocessing restricted military "
    "implants — legally inert once they're inside a civilian body. Your team's "
    "stolen neural combat suite is currently on a workbench two floors below "
    "street level. If it goes in tonight, it's gone for ever.",
    "Trace the implant's embedded ping signal", "tech", 8,
    "Military hardware runs a passive handshake signal even when offline. "
    "You tune a short-range scanner to the right frequency and walk "
    "the sub-level grid until the signal strength peaks. Third door on the "
    "left. The workbench technician has gone for a break. You're in and out.",
    "The implant's ping has been shielded — wrapped in a Faraday sleeve "
    "while the shop runs diagnostics. No signal. You cover the sub-level "
    "twice without a hit before the technician returns.",
    "Pressure the shop operator into handing it over", "influence", 7,
    "A detailed knowledge of the shop's operating model, its supplier "
    "network, and two names the operator doesn't want connected to his "
    "business give you everything you need. The implant is in your "
    "hands inside three minutes.",
    "The operator has a second buyer already on-site. Your approach "
    "lands in the middle of a live transaction and the shop locks down "
    "before you can press the advantage.",
    35, 2),

_mk("tm_c25", "The Quiet Crowd", "city", "city_25_megablock_atrium",
    "Extract a witnessed informant through a megablock atrium crawling with corporate surveillance.",
    "The atrium of Megablock Seven is six storeys of open space — retail "
    "levels, residential corridors, and a security camera network so dense "
    "that no unregistered face goes unmarked for more than forty seconds. "
    "Your informant is registered under a flagged identity. Every exit is "
    "monitored. You need to get her out without triggering a facial-match alert.",
    "Move her through the maintenance system", "stealth", 9,
    "You locate the maintenance access point two levels below and guide "
    "her verbally through the staff corridors. No cameras in the service "
    "passages. The security system tracks a ghost through the atrium while "
    "the two of you walk out through the loading bay.",
    "The maintenance access requires a keycard you don't have. You spend "
    "twelve minutes bypassing the lock. The facial-match alert triggers "
    "during your delay. The exit is staffed when you arrive.",
    "Create a diversion to flood the camera system with false alerts", "tactics", 8,
    "Forty simultaneous motion triggers across the atrium's upper levels "
    "— ceiling panels, escalator sensors, emergency signage — produce "
    "enough false positives to saturate the security operator's screen "
    "for ninety seconds. You walk her straight to the exit.",
    "The security operator is experienced enough to clear false alerts "
    "in under thirty seconds. Your ninety-second window becomes thirty "
    "and the exit camera captures a clean image before you reach it.",
    45, 3),

_mk("tm_c26", "Contraband Run", "city", "city_26_black_market_underpass",
    "Intercept a delivery of corporate bioweapon components moving through the underpass market.",
    "The underpass market operates in the gap between two infrastructure "
    "systems — no jurisdiction, no oversight. Somewhere in the next hour "
    "a courier is delivering synthesiser components that should not exist "
    "outside a class-four laboratory. The buyer represents a faction "
    "you cannot afford to see equipped.",
    "Infiltrate the buyer's meeting", "stealth", 8,
    "You blend into the market crowd forty minutes before the meeting "
    "and work your way to the exchange point. When the courier and the "
    "buyer meet you're close enough to overhear the authentication codes. "
    "A smooth lift and the components are with you before either party "
    "realises the meeting went wrong.",
    "The buyer's security detail runs a counter-surveillance check "
    "fifteen minutes before the meet. They make you on the second sweep "
    "and move the exchange to a secondary location you haven't identified.",
    "Pose as a competing supplier to disrupt the transaction", "influence", 9,
    "A cover identity, the right technical vocabulary, and a better "
    "offer than the original seller: you intercept the courier before "
    "the meeting and buy the components yourself. The buyer waits "
    "for a transaction that never arrives.",
    "The courier runs an identity check through his buyer's network. "
    "Your cover is solid against city databases but not against a "
    "closed market reputation system. He walks past you and completes "
    "the original transaction.",
    50, 4),

_mk("tm_c27", "Dead Drop", "city", "city_27_executive_av_pad",
    "Plant evidence on a corporate executive's private AV before it departs the city.",
    "The executive's personal AV sits on the rooftop pad — forty-five minutes "
    "until departure. What goes with the AV goes beyond the reach of any "
    "jurisdiction that might act on it. The evidence needs to be on the "
    "craft's onboard systems before the rotors spin up, or the case "
    "dies here on this rooftop.",
    "Access the AV's onboard system remotely from the maintenance node", "tech", 9,
    "The pad's maintenance node runs an unencrypted diagnostic channel "
    "to the AV while it charges — a known oversight in the model's "
    "ground-power integration. You push the evidence package through "
    "the diagnostic channel and it writes to the flight computer's "
    "protected partition. It will be found on landing.",
    "The AV's ground team runs a pre-flight security check that includes "
    "an active disconnect from all external nodes. The diagnostic channel "
    "closes eighteen minutes before your access window opens.",
    "Board the AV disguised as pad crew", "stealth", 9,
    "Pad crew coveralls, a legitimate-looking equipment case, and the "
    "confidence to work without looking over your shoulder. You board "
    "under the guise of a pre-departure systems check and walk off "
    "the ramp four minutes later, empty-handed and finished.",
    "The executive's personal security officer is running a tighter "
    "pre-departure protocol than usual. He asks for credentials you "
    "don't have and the boarding window closes.",
    60, 4),

_mk("tm_c28", "Below the Knife", "city", "city_28_street_surgery_lane",
    "Locate a missing operative who vanished after an unsanctioned procedure on Surgery Lane.",
    "Operative Veda went dark forty hours ago, last seen entering Surgery Lane "
    "for an off-books procedure she didn't clear with the team. Three unlicensed "
    "clinics operate in this block. One of them has her. The question is "
    "whether she went in voluntarily or not, and what condition she is in now.",
    "Trace the procedure through underground medical records", "medicine", 8,
    "You know the physiological markers of what she was having done — "
    "the post-op requirements, the monitoring profile. Two clinics can't "
    "have handled that procedure. The third has her listed under a false "
    "name on a paper ledger. She's recovering in the back room, stable, "
    "and furious that it took you this long.",
    "The records on Surgery Lane are kept in isolation — no digital "
    "trail, nothing searchable. You spend six hours moving between "
    "clinics without the right language to get past the front desk.",
    "Lean on the underground surgeons until someone talks", "influence", 8,
    "Surgery Lane runs on reputation and deniability. You make it "
    "clear you're not here for the clinics — you're here for one patient, "
    "and the first surgeon who helps you gets your discretion as payment. "
    "The second one takes the deal.",
    "The surgeons on this block have dealt with corporate extraction "
    "teams before. They close ranks immediately. Three hours of pressure "
    "and no one has said a word.",
    40, 3),

_mk("tm_c29", "Cover Blown", "city", "city_29_elite_neon_lounge",
    "Extract a compromised undercover agent from an elite lounge before his cover burns.",
    "The Aether Lounge is a quieter kind of danger — silk walls, "
    "client discretion, and three corporate intelligence officers at "
    "a corner table who have been watching your operative for twenty "
    "minutes. He doesn't know it yet. You're already inside, two "
    "tables away, with one viable window before they move on him.",
    "Walk him out through the VIP passage without incident", "composure", 8,
    "You catch his eye across the room with a look that means "
    "'leave now, calmly'. He reads it immediately — four years of training "
    "paying off in a single held gaze. He finishes his drink, excuses "
    "himself to the men's room, and you meet him in the corridor. "
    "You're both in a vehicle before the intelligence officers order dessert.",
    "He doesn't read the signal. Or he does and freezes. When you "
    "approach the table to try a verbal extraction, one of the "
    "intelligence officers stands up at the same moment.",
    "Engineer a lounge-wide disturbance that forces an evacuation", "tactics", 8,
    "A medical emergency at the bar, a fire suppression trigger in "
    "the kitchen, and a power interruption to the booking system — "
    "three small failures in ninety seconds produce a genuine "
    "evacuation. In the confusion your operative is just another "
    "person heading for the exit.",
    "The lounge security response is faster than you expected. "
    "The evacuation routes are locked down within sixty seconds "
    "and the intelligence officers stay exactly where they are.",
    45, 3),

_mk("tm_c30", "Flood Line", "city", "city_30_flooded_undercity_tunnel",
    "Destroy a hidden surveillance node buried in the flooded undercity before it transmits.",
    "The undercity tunnel has been flooding for three years — water "
    "table rise, neglected pumps, corporate indifference. Somewhere "
    "in the submerged sections a passive surveillance node has been "
    "recording everything within three city blocks and preparing "
    "to transmit its package in six hours. You go in wet.",
    "Dive through the flooded sections to reach the node", "composure", 9,
    "Cold, dark water, two breath holds, and a navigation light "
    "that fails halfway through the third section. You find the "
    "node by feel, cross-referencing the map you memorised above "
    "ground. The charge sets in forty seconds. You're out before "
    "the tunnel stops shaking.",
    "The third section is completely submerged, ceiling to floor, "
    "for longer than your breath can carry you. You turn back after "
    "the first attempt and the clock keeps running.",
    "Reroute the flood controls to drain the tunnel sections", "tech", 8,
    "The pump station at the tunnel entrance still has its control "
    "panel, and the hardware is simpler than anything digital — "
    "manual valves and a single programmable relay. You reverse "
    "the flow, drain two sections in forty minutes, and walk to "
    "the node on dry ground.",
    "The relay is corroded past function. The manual valves will "
    "take four hours to drain what you need. You don't have four hours.",
    50, 4),

]  # end _CITY


# ── WASTELAND MISSIONS ─────────────────────────────────────────────────────────

_WASTE = [

_mk("tm_w01", "Long Road", "wasteland", "wasteland_01_broken_highway",
    "Escort a refugee convoy through raider territory on the broken highway.",
    "The highway stretches across the badlands — cracked asphalt, burned-out "
    "vehicles, and somewhere in the next forty kilometres, three raider bands "
    "who run this stretch for tolls paid in blood. The convoy carries sixty "
    "civilians and medical supplies. They will not survive a firefight.",
    "Run a tight defensive formation", "tactics", 8,
    "You position the heaviest vehicles at the front and rear, brief every driver "
    "on the rally point, and run the convoy through the hottest section at speed "
    "with comms locked. The raiders peel off when they see the response readiness. "
    "Sixty civilians reach the other side.",
    "Your formation assumes the raiders attack from the sides. They hit the lead "
    "vehicle head-on and the convoy stalls. Three hours of negotiation in the "
    "badlands sun before you can move again.",
    "Keep the convoy moving fast and trust the drivers", "composure", 7,
    "You radio each driver separately and talk them through — calm voice, "
    "clear instructions, no panic. The convoy moves as a unit. One raider "
    "volley falls short. Nobody stops. Nobody panics.",
    "One driver loses his nerve at the first gunshot and brakes hard. "
    "The convoy folds in on itself and the raiders cut it into sections.",
    35, 2),

_mk("tm_w02", "Iron Price", "wasteland", "wasteland_02_scrap_outpost",
    "Negotiate access through a scavenger gang's territory to reach a stranded asset.",
    "The Scrap Barons run this stretch of the badlands like a toll road — "
    "everything that moves through pays, one way or another. Their outpost "
    "is a fortified pile of welded metal and bad intentions. Your asset is "
    "three kilometres behind it. You need to get through.",
    "Open a diplomatic channel", "influence", 8,
    "You go in with both hands visible and a reasonable offer — fuel, medical "
    "supplies, and the location of a rival band's cache. The Barons take the "
    "deal. You pass through without a scratch.",
    "The Baron in charge has a grudge against the last corporate team that "
    "tried to buy passage. He doesn't negotiate. He demonstrates.",
    "Show of force at the perimeter", "close_combat", 7,
    "You make it clear at the gate that forcing passage would be more expensive "
    "than letting you through. After a tense five minutes, the gate boss decides "
    "the math works in your favour. You move.",
    "There are more of them than your intelligence suggested. The show of force "
    "reads as aggression and you're surrounded before you can recalibrate.",
    30, 2),

_mk("tm_w03", "Poison Ground", "wasteland", "wasteland_03_toxic_basin",
    "Rescue survivors from a toxic contamination event in the basin lowlands.",
    "The basin looks like a sea of rust-coloured fog from the ridge. Somewhere "
    "inside it, a settlement of forty people is trying to breathe through "
    "improvised filters that won't last another six hours. Corporate tanker "
    "accident. Deliberate non-response. You're the only response there is.",
    "Neutralise the toxin source first", "medicine", 9,
    "You identify the tanker's chemical signature and synthesise a rudimentary "
    "neutralising solution from the emergency kit. Two hours of work at the "
    "source point and the concentration drops enough to walk. "
    "Forty survivors help themselves out.",
    "The chemical composition is something you haven't seen before. Your "
    "neutralising attempt has no effect and you lose time. Survivors begin "
    "collapsing before the wind shifts enough to clear the basin.",
    "Rush in with respirators and carry them out", "composure", 8,
    "You can't neutralise what you can't identify — but you can breathe through "
    "a rated mask. You and the team make twelve trips into the basin, one "
    "load of survivors each time, until the settlement is empty.",
    "The respirators aren't rated for this concentration. Your team begins "
    "experiencing symptoms on the third trip and is forced to withdraw, "
    "leaving survivors behind.",
    45, 3),

_mk("tm_w04", "Dust Fever", "wasteland", "wasteland_04_dust_storm_settlement",
    "Mediate a lethal dispute between two settlement factions before it burns the town.",
    "The dust storm has been sitting over the settlement for four days. "
    "Two factions are now fighting over the remaining water supply, and "
    "someone fired a gun last night. If you don't resolve this before the "
    "storm breaks, the settlement won't survive to see it end.",
    "Sit them down and mediate", "composure", 8,
    "You separate the faction leaders, speak with each privately, and then "
    "bring them to the same table with a water ration proposal they both "
    "find insulting — but equal. They sign. The settlement survives the storm.",
    "The session breaks down when one faction leader accuses the other of "
    "theft. The second faction responds by barricading the water storage. "
    "It becomes a siege.",
    "Expose the person who fired the gun", "influence", 7,
    "Two hours of conversations across the settlement identify the shooter — "
    "a young man on neither faction's payroll, acting alone out of fear. "
    "You present the evidence publicly. The factions redirect their anger "
    "inward and the dispute de-escalates.",
    "Your investigation implicates someone connected to both faction leaders. "
    "The exposure triggers an alliance against you instead of against each other.",
    30, 2),

_mk("tm_w05", "Dead Light", "wasteland", "wasteland_05_ruined_solar_farm",
    "Restore power to a settlement before its food storage fails overnight.",
    "The ruined solar farm once powered four settlements. Most of the "
    "panels are gone, but the inverter station still stands, and if you "
    "can get sixty percent of the remaining arrays online, the settlement "
    "three kilometres east can run its refrigeration through the night. "
    "The food spoils in eight hours. You have tools and six hours.",
    "Emergency repair of the inverter station", "tech", 8,
    "The inverter's main coupling is cracked. You fabricate a temporary fix "
    "from salvaged components — ugly, but functional. Sixty-eight percent "
    "of the arrays come online. The settlement's refrigeration holds "
    "through to morning.",
    "The coupling fails completely when you attempt the repair. Without it "
    "none of the arrays can feed to the grid. The settlement loses its "
    "food storage to the heat.",
    "Divert power from the backup emergency circuit", "tactics", 7,
    "You map the old grid layout and find a bypass route through the "
    "emergency circuit — normally limited to ten percent capacity, but "
    "rerouted through two substations it can carry enough. "
    "Ugly but effective.",
    "The emergency circuit can't sustain the load. It trips after twenty "
    "minutes and cannot be reset without parts you don't have.",
    30, 2),

_mk("tm_w06", "Cold Storage", "wasteland", "wasteland_06_buried_bunker",
    "Breach a sealed pre-war military bunker before rival scavengers locate it.",
    "The bunker entrance is buried under two metres of collapse debris. "
    "Your ground-penetrating scan shows it intact — and full of military-grade "
    "equipment dating to the corporate wars. A rival scavenger team picked up "
    "the same signal two hours after you did. They're running parallel to your "
    "position.",
    "Override the lock with archived military codes", "tech", 9,
    "The codes are forty years old, but military encryption hasn't changed "
    "its key structure since the war. You sequence through the variations in "
    "under an hour and the door cycles open. You're inside before the rivals "
    "reach the surface entrance.",
    "The bunker's passive defence system is still active. The override "
    "attempt triggers an electrical countermeasure that fuses your tools. "
    "You find the secondary entrance, but the rivals found it first.",
    "Find and use the alternate service entrance", "stealth", 8,
    "The original schematics show a service access point two hundred metres "
    "north. You locate it, clear the collapse debris quietly, and slip inside "
    "while the rivals are still working the main entrance.",
    "The service entrance collapsed completely. You spend two hours clearing "
    "debris before determining there's no way through, and by then the rivals "
    "have cracked the main lock.",
    55, 4),

_mk("tm_w07", "Wreck", "wasteland", "wasteland_07_vehicle_graveyard",
    "Survive an ambush in a vehicle graveyard and protect the convoy cargo.",
    "The vehicle graveyard stretches across three hectares of cracked earth — "
    "hundreds of rusted hulks stacked and crushed. Your convoy rolled into "
    "it before the ambush signal reached you. Now there are shooters in "
    "the stacks and the cargo vehicle can't reverse fast enough.",
    "Use the vehicles as cover and counter-flank", "close_combat", 8,
    "You read the shooting positions from the muzzle flashes and move "
    "laterally through the wreckage. The ambushers were expecting a static "
    "target. They get a counter-movement that puts you behind them in "
    "four minutes.",
    "The terrain is more complicated than it looked. You take a wrong turn "
    "through the stacks and emerge in a dead end with shooters on three sides.",
    "Fall back and draw the ambush into a chokepoint", "stealth", 8,
    "You ghost back through the wrecks, pulling the ambushers after you "
    "while the cargo vehicle uses the distraction to reverse to safety. "
    "You exit through a gap in the eastern stack.",
    "The cargo driver panics during the fallback and takes the wrong exit. "
    "The vehicle is disabled by fire before you can redirect him.",
    40, 3),

_mk("tm_w08", "Chokepoint", "wasteland", "wasteland_08_canyon_pass",
    "Hold a canyon pass against a sustained raider assault.",
    "The canyon pass is twenty metres wide and three kilometres long — "
    "the only route between two allied settlements. Raiders have blockaded "
    "the eastern end. You hold the western entrance with four operatives "
    "and whatever the canyon itself offers in the way of terrain advantage.",
    "Set kill zones across the choke", "tactics", 9,
    "You spend an hour reshaping the battlefield — cable traps, stacked "
    "debris, covered firing positions. When the raiders push in, they push "
    "into a kill box. Three waves. The fourth one doesn't come.",
    "The raiders split into two groups and probe both walls simultaneously. "
    "Your prepared positions cover the centre. The flanks break through "
    "in the second wave.",
    "Concentrate fire and hold the line", "firearms", 8,
    "Disciplined fire, coordinated reload cycles, and no wasted shots. "
    "The raiders commit more than they planned to and take more than they "
    "can absorb. They break off after forty minutes.",
    "Ammunition runs low in the second wave. The rate of fire drops, "
    "the raiders sense the change, and they push through the gap.",
    50, 4),

_mk("tm_w09", "Dead Water", "wasteland", "wasteland_09_dry_reservoir",
    "Locate a clean water source for a settlement on the edge of dehydration.",
    "The reservoir is bone-dry and has been for a decade. The settlement "
    "running its last reserve of purified water asked for help three days ago. "
    "Your geological survey shows three possible underground sources within "
    "two kilometres. You have equipment to test two.",
    "Test the geological survey sites methodically", "tech", 8,
    "The third site on the survey shows the most promising subsurface "
    "resonance. You run the test in order of likelihood and hit water "
    "at the second location — fourteen metres down, clean mineral table, "
    "sustainable yield.",
    "The first site is dry. The second shows contamination from the old "
    "reservoir chemical treatments. You're out of test equipment and no "
    "closer to drinkable water.",
    "Assess water source quality and repair a purifier", "medicine", 8,
    "The contaminated secondary source is salvageable. You know exactly "
    "which filtration compounds to use and in what order. The purifier "
    "runs its first clean cycle twelve hours after you start.",
    "The contamination level exceeds your purification capacity. The "
    "compound you needed is missing from the kit. The water is undrinkable.",
    40, 3),

_mk("tm_w10", "Pressure Point", "wasteland", "wasteland_10_pipeline_station",
    "Protect a fuel pipeline station from corporate saboteurs.",
    "The pipeline station is the only fuel source for four wasteland "
    "settlements. Corporate intelligence says a sabotage team is moving "
    "on the station tonight — if they destroy the compressor array, "
    "fuel stops flowing for six months. You have six hours to prepare.",
    "Secure the compressor array with countermeasures", "tech", 8,
    "You harden the compressor control systems against remote access, "
    "reroute the diagnostic signals to confuse any approach targeting, "
    "and set a passive alert on every access tunnel. The saboteurs abort "
    "when they hit the first countermeasure.",
    "The countermeasure package has a dependency on the station's "
    "local network, which is running older firmware. The saboteurs "
    "bypass it and hit the compressor before your alerts trigger.",
    "Hunt the saboteurs before they reach the station", "firearms", 7,
    "You position ahead of the approach route and intercept the team "
    "before they reach the perimeter. Controlled, professional, "
    "and over in three minutes. The station never knows it was targeted.",
    "The saboteurs take a secondary route your intelligence didn't flag. "
    "They're inside the perimeter before you locate them.",
    40, 3),

_mk("tm_w11", "Black Box", "wasteland", "wasteland_11_crashed_drone",
    "Recover intelligence data from a military drone before the corporate retrieval team arrives.",
    "The drone went down in the borderlands two hours ago — military-grade, "
    "autonomous, and carrying sensor data on three months of corporate "
    "activity in the region. The corporate retrieval team is airborne. "
    "You have a forty-minute window.",
    "Extract the data core directly", "tech", 8,
    "The drone's armoured housing is designed to survive the crash intact. "
    "You know which panel gives access to the data core and you've done "
    "this before. Twelve minutes extraction, full data package, "
    "and you're moving before the retrieval team lands.",
    "The impact deformed the housing. The panel won't open cleanly and "
    "you waste twenty minutes forcing it. The retrieval team lands during "
    "the extraction and you leave empty-handed.",
    "Secure the perimeter and buy time for extraction", "tactics", 7,
    "You assess the threat timeline and decide the perimeter comes first. "
    "Your team slows the retrieval team's approach with terrain obstacles "
    "while the tech specialist completes the extraction at a workable pace.",
    "The retrieval team has air support you didn't account for. "
    "Your perimeter holds, but the air assets bypass it and land "
    "directly at the crash site.",
    45, 3),

_mk("tm_w12", "Dead Zone", "wasteland", "wasteland_12_comms_array",
    "Install a communications relay in a jammed section of the badlands.",
    "The resistance network has a blind spot — forty kilometres of badlands "
    "where corporate jamming suppresses all communications. The relay "
    "needs to go on the comms array tower at the centre of the zone. "
    "The jamming makes radio coordination impossible once you're inside. "
    "You go in silent and come out with the relay installed.",
    "Ghost the installation — no contact", "stealth", 9,
    "You map the patrol pattern of the array's two guards before entering "
    "the jamming zone, memorise the timing, and execute entirely on that "
    "memory. The relay goes up in eleven minutes. The guards never break "
    "their rotation.",
    "One guard deviates from the pattern — a bathroom break that puts "
    "him at the tower base exactly when you're on the third rung of the "
    "access ladder.",
    "Set up a hardened relay position and transmit", "tech", 8,
    "Rather than installing on the corporate array, you set up an "
    "independent relay on a secondary highpoint. It takes longer, "
    "but it's in your control and outside the jamming cone.",
    "The highpoint you identified as the relay site is already "
    "occupied by a corporate signal monitor. You can't set up "
    "without being detected.",
    40, 3),

_mk("tm_w13", "Ghost Train", "wasteland", "wasteland_13_derelict_maglev",
    "Clear a mutant infestation from an ancient derelict maglev train.",
    "The derelict maglev hasn't moved in thirty years, but something has "
    "been living in it for the last six months and making the eastern "
    "settlements impassable after dark. Nine cars, unknown number of "
    "contacts, total darkness inside the tunnels.",
    "Clear systematically, car by car", "close_combat", 8,
    "You move from the front car to the rear, sealing each section "
    "as you clear it. The infesting creatures retreat into the final car. "
    "You seal it from the outside. The train is clear in two hours.",
    "The creatures in the rear cars hear you working forward and begin "
    "moving through the roof access hatches. They're ahead of you by car "
    "five and you're dealing with contact from two directions.",
    "Lure everything to a single chokepoint", "tactics", 8,
    "You identify the loudest possible noise source in the train — "
    "the emergency alert horn — and trigger it from car five. Everything "
    "in the train moves toward the sound. You seal the forward cars "
    "and deal with them in one controlled engagement.",
    "The emergency horn is non-functional. Your improvised noise source "
    "attracts half the infestation. The other half finds you.",
    35, 2),

_mk("tm_w14", "Dig Site", "wasteland", "wasteland_14_buried_arcade",
    "Recover a pre-war cache from ruins controlled by a territorial gang.",
    "The buried arcade was a tourist destination before the corporate "
    "wars. Now it's a gang hangout and, somewhere under the collapse, "
    "a pre-war cache of networking hardware worth more than the gang "
    "makes in a year. They don't know it's there. Yet.",
    "Infiltrate at night and locate the cache", "stealth", 8,
    "The gang posts a single overnight watch and he sleeps through his "
    "rotation. You're inside and back out in ninety minutes with enough "
    "hardware to equip a small network.",
    "The overnight watch is awake and doing rounds. You're spotted during "
    "approach and have to withdraw before reaching the cache.",
    "Buy information about the site layout", "influence", 7,
    "A former gang member who owes a favour draws you a floor plan "
    "and marks the cache location from memory. You go in at a shift "
    "change with a legitimate salvage permit for an unrelated site nearby. "
    "Nobody looks twice.",
    "The informant's loyalty is for sale to the highest bidder. "
    "The gang has the floor plan before you arrive, and a welcome "
    "party waiting at the cache site.",
    35, 2),

_mk("tm_w15", "Stone and Steel", "wasteland", "wasteland_15_scrap_quarry",
    "Stop a gang from extracting strategic materials from a contested quarry.",
    "The scrap quarry contains rare earth materials left behind by "
    "pre-war construction. The Ironback gang has been mining it for "
    "three months. If they complete the extraction, those materials "
    "fund their expansion into three more settlements. You need "
    "to shut the operation down.",
    "Collapse the primary extraction tunnel", "tactics", 8,
    "You identify the tunnel support structure's weak points from the "
    "survey data and time the collapse for shift change — nobody underground "
    "when the ceiling comes down. The quarry is non-operational. "
    "It will take the gang months to clear.",
    "The explosive charge misfires. The tunnel stays intact and the "
    "gang now knows someone is targeting the site.",
    "Drive the gang out in a direct engagement", "close_combat", 7,
    "Twelve operatives against the gang's security rotation, terrain "
    "advantage in your favour. A fast, hard push through the site "
    "boundary breaks their security before they can organise "
    "a response. They abandon the equipment.",
    "The gang has twice as many security personnel as your intelligence "
    "suggested. The engagement becomes a prolonged engagement you can't win.",
    45, 3),

_mk("tm_w16", "Blight", "wasteland", "wasteland_16_hydroponic_farm",
    "Deal with a crop blight threatening the only food source for a wasteland settlement.",
    "The hydroponic farm runs forty crop cycles a year and feeds twelve "
    "hundred people. Three days ago, a fast-moving blight appeared in "
    "the primary growing beds. It's already through twenty percent of "
    "the crops. Without intervention, the farm fails completely in a week.",
    "Identify and apply a chemical treatment", "medicine", 8,
    "The blight responds to a specific antifungal compound you carry in "
    "the emergency medical kit. You work through the growing beds in "
    "systematic order, treating each affected section. "
    "Forty percent loss, sixty percent saved.",
    "The compound you identify is the right one, but in the wrong "
    "concentration. The diluted treatment slows the blight without "
    "stopping it. You lose the farm in eight days instead of seven.",
    "Quarantine affected sections and manage the spread", "influence", 7,
    "You convince the farm workers to wall off the affected growing beds "
    "and accept a hard loss on those sections. The speed of the quarantine "
    "decision saves the uninfected beds. The settlement takes a supply hit "
    "but survives.",
    "The farm workers resist the quarantine — their livelihoods are in "
    "those beds. By the time the disagreement is resolved, the blight "
    "has crossed the quarantine line.",
    30, 2),

_mk("tm_w17", "Blind Spot", "wasteland", "wasteland_17_night_convoy_route",
    "Intercept a corporate supply convoy moving through the badlands at night.",
    "The convoy runs the night route because satellite coverage drops "
    "between 23:00 and 02:00. Six vehicles, mixed cargo, minimum security. "
    "Your window is exactly three hours. The convoy enters your range "
    "in forty minutes.",
    "Set a silent ambush on the route", "stealth", 9,
    "You position before the convoy arrives, lights off, movement stopped. "
    "The lead vehicle rolls through your position without registering anything. "
    "You disable the rear security vehicle first, then work forward. "
    "The convoy stops. Nobody calls it in.",
    "One of your team shifts position at the wrong moment. A security "
    "scanner in the lead vehicle picks up the movement signature. "
    "The convoy goes to full alert and accelerates through your position.",
    "Vehicle intercept — block the route", "tactics", 8,
    "A disabled vehicle across the road brings the convoy to a stop "
    "two kilometres before your main position. Standard intercept from there — "
    "controlled, documented, finished in under twenty minutes.",
    "The convoy uses the secondary route your intelligence didn't cover. "
    "You're in position on an empty road when the window closes.",
    45, 3),

_mk("tm_w18", "Depths", "wasteland", "wasteland_18_sinkhole_ruins",
    "Rescue miners trapped underground after a collapse in the sinkhole ruins.",
    "The sinkhole opened without warning during the morning shift. Eight "
    "miners are below ground in a section that may or may not still have "
    "breathable air. Your team has rescue equipment, structural sensors, "
    "and the clock that has been running since the collapse.",
    "Engineer a safe rescue passage", "tech", 9,
    "You map the collapse geometry with the structural sensors and identify "
    "a load-bearing route through the debris. Three hours of careful work — "
    "never removing a piece that matters — and you have a passage. "
    "All eight miners are alive.",
    "The structural assessment misses a secondary collapse point. "
    "Your excavation triggers it. The passage collapses again with "
    "two of your team inside the new void.",
    "Keep the miners calm and wait for the right extraction window", "composure", 8,
    "You establish radio contact through a thin section of debris. "
    "Seventy minutes of measured guidance — keep breathing slow, "
    "don't move the debris above you — buys time until the structural "
    "team can assess a safe approach route.",
    "Radio contact is intermittent and fragile. One miner begins "
    "panicking, others follow, and the movement dislodges debris "
    "that closes the final air gap.",
    50, 4),

_mk("tm_w19", "Shelter", "wasteland", "wasteland_19_toxic_rain_shelter",
    "Keep forty civilian refugees alive through a toxic rain event in the badlands.",
    "The storm moved faster than the forecast predicted. Forty refugees "
    "are sheltering in a corrugated building with inadequate sealing. "
    "The rain will begin in two hours and last for eighteen. The "
    "shelter's existing supplies and sealing are not sufficient for "
    "that exposure duration.",
    "Triage and treat exposure cases as they develop", "medicine", 8,
    "You set up a treatment rotation, prioritise the most vulnerable, "
    "and work through the eighteen hours systematically. Exposure is "
    "managed. Everyone survives, though several will need continued care.",
    "The exposure cases arrive faster than you can treat them. By hour "
    "eight you're out of anticontaminants and making decisions you "
    "don't want to make.",
    "Improvise additional sealing to reduce exposure", "composure", 7,
    "Forty frightened people in a deteriorating shelter need someone "
    "calm. You direct the sealing work without urgency and without panic, "
    "and the improvised materials hold. Exposure stays below critical "
    "threshold for the full eighteen hours.",
    "The sealing work is rushed and incomplete. Rain finds the gaps "
    "in hour four. By hour twelve the shelter is unviable.",
    35, 2),

_mk("tm_w20", "Last Line", "wasteland", "wasteland_20_city_wall_perimeter",
    "Defend the outer wall perimeter against a coordinated raid.",
    "The city wall's outer perimeter is the last physical barrier "
    "between the corporate interior and the wasteland. A coordinated "
    "raider assault is inbound — more organised than the usual probing "
    "attacks, and targeting the weakest section of the perimeter wall. "
    "You have four hours to prepare the defence.",
    "Fortify and hold the weak section", "tactics", 9,
    "You reinforce the weak section with salvaged materials, set "
    "interlocking fields of fire, and brief every defender on their "
    "fallback position. The assault hits the fortification and breaks "
    "on it. The perimeter holds.",
    "Your fortification plan overloads the existing wall anchors. "
    "The added weight causes a partial collapse before the raiders "
    "even arrive, creating the breach you were trying to prevent.",
    "Counterattack before the raid consolidates", "firearms", 9,
    "The raiders expect a defensive posture. You give them an aggressive "
    "push into the no-man's land before they can form up. The surprise "
    "disrupts their coordination and they break off to reorganise. "
    "They don't come back tonight.",
    "The counterattack runs into the raiders' vanguard before your "
    "main element is in position. You take casualties and fall back "
    "to the wall, which is now under assault.",
    55, 4),

_mk("tm_w21", "Road Peace", "wasteland", "wasteland_21_nomad_caravan_camp",
    "Negotiate passage rights through nomad confederation territory before a corporate convoy triggers a war.",
    "The Kessler Confederation controls the central highway for six hundred "
    "kilometres. A corporate logistics convoy — unannounced, unmarked, and "
    "armed — entered the territory an hour ago. The confederation's outriders "
    "are already shadowing it. If this reaches the headman without "
    "diplomatic groundwork it ends in fire.",
    "Negotiate with the confederation headman before the convoy does", "influence", 8,
    "You reach the headman's camp ahead of the corporate team and spend "
    "forty minutes in a genuine conversation — resources, rights, "
    "mutual grievances. When the corporate delegation arrives they find "
    "a draft agreement already on the table and an interlocutor who "
    "has made their position significantly harder to refuse.",
    "The headman has dealt with corporate intermediaries before and "
    "his patience ran out three meetings ago. He hears your opening "
    "words and dismisses you before you can get to the point.",
    "Intercept and re-route the convoy before it reaches the confederation", "tactics", 8,
    "The convoy's navigation system runs on public waypoint data. You "
    "introduce a plausible re-route — washed-out road, fictional hazard "
    "beacon — and redirect it forty kilometres south of confederation "
    "territory. The outriders watch it disappear over the horizon "
    "and stand down.",
    "The convoy's lead driver is running his own navigation data "
    "from a satellite feed you can't modify. The re-route signal "
    "is ignored and the convoy continues on its original heading.",
    40, 2),

_mk("tm_w22", "Blowout", "wasteland", "wasteland_22_extraction_rig",
    "Prevent sabotage of the fuel extraction rig that supplies your forward operating base.",
    "The rig is the only fuel source within three hundred kilometres. "
    "Someone has planted a package somewhere in the facility — a "
    "timed device, forty minutes from now. The rig crew has been "
    "evacuated and the facility is quiet except for the background "
    "noise of the machinery and whoever is still inside making sure "
    "the device works.",
    "Locate and disarm the device through the facility systems", "tech", 9,
    "The rig's environmental sensors are still running. A temperature "
    "anomaly in sub-level three leads you to the device — an "
    "improvised package wired into the main pressure line. Twelve "
    "minutes to disarm, six minutes to verify, and the rig is intact.",
    "The environmental sensor network has been deliberately corrupted "
    "as part of the sabotage. Every temperature reading is wrong. "
    "You find the device by smell with three minutes left on the "
    "timer, which is not enough time.",
    "Track down the saboteur before they activate it", "stealth", 8,
    "Someone is still in the facility. You track the sound of "
    "movement through the lower level corridors, moving faster "
    "than them and quieter. You intercept the saboteur at "
    "the device before the activation window opens.",
    "The facility's background noise masks the saboteur's "
    "movement completely. By the time you locate them they "
    "have already reached the device.",
    55, 4),

_mk("tm_w23", "Blinded", "wasteland", "wasteland_23_solar_mirror_desert",
    "Cross a decommissioned solar mirror field to reach a relay station on the far side.",
    "The mirror field was an energy project that outlived its "
    "operator by six years. The mirrors still track the sun. "
    "Anything crossing the field during daylight hours that "
    "breaks a sensor line triggers an automated focusing sequence. "
    "The relay station on the far side has intelligence you "
    "need and no other approach is viable today.",
    "Navigate the mirror field using sensor-gap analysis", "stealth", 9,
    "The mirror tracking system has a predictable blind spot — "
    "forty-seven seconds between repositioning cycles, twice per "
    "hour. You map the gaps and cross the field in three stages, "
    "lying flat in the sand during each reposition. An hour of "
    "patience and you emerge on the far side without triggering a single beam.",
    "The thermal updrafts in the field create movement artefacts "
    "that the sensors cannot reliably distinguish from a person. "
    "The system triggers on your second crossing stage and a "
    "focusing beam tracks your position for ninety seconds.",
    "Disable the tracking system from the perimeter control box", "tech", 8,
    "The control box is an antique and the override protocol "
    "is documented in a manual you found in a scrap archive. "
    "You shut down the tracking system from the perimeter "
    "in eleven minutes. The mirrors freeze. You cross "
    "in daylight without incident.",
    "The control box has been physically sealed with epoxy — "
    "someone else tried to access it before you. You can't "
    "reach the terminals without tools you don't have on site.",
    45, 3),

_mk("tm_w24", "Echo Town", "wasteland", "wasteland_24_badlands_ghost_town",
    "Clear a corporate observation post hidden inside an abandoned ghost town.",
    "Echo Town has been empty for twelve years, which is why "
    "Meridian-Sato chose it for a long-range observation post. "
    "Four operatives, a communication rig, and three months "
    "of surveillance data on your operations. The ghost town "
    "is quiet and the post is expecting a routine check-in "
    "in forty minutes.",
    "Move through the ghost town undetected and neutralise the post", "stealth", 8,
    "Empty buildings are better than crowds. You move through "
    "the service alleys and collapsed storefronts, using the "
    "ruins as cover. The observation post's outer watch is "
    "positioned for the main approaches, not the back lanes. "
    "You reach the communication rig first. The operatives "
    "surrender when the rig goes dark.",
    "One of the outer watchers is positioned in an unexpected "
    "location — on the roof of the building you've chosen "
    "as your approach route. You're compromised before you "
    "reach the town perimeter.",
    "Pose as the scheduled check-in team", "influence", 8,
    "You acquire the check-in authentication codes from an "
    "intercepted signal and present yourself at the post's "
    "front approach at the correct time. The observation team "
    "opens the door expecting colleagues and finds a situation "
    "they cannot recover from.",
    "The authentication codes include a verbal challenge "
    "component that wasn't in the intercepted signal. "
    "The observer on the door hears the wrong response "
    "and the post goes to alert.",
    40, 2),

_mk("tm_w25", "The Underground Route", "wasteland", "wasteland_25_smuggler_tunnel",
    "Guide a group of refugees through a dangerous smuggler tunnel network to safety.",
    "Forty-two people — families, an elderly medic, three children "
    "who haven't spoken since the crossing raid — are sheltering "
    "at the tunnel entrance. The tunnel network runs through "
    "active smuggler territory. The refugees cannot make it "
    "overland. The tunnel is the only route that doesn't cross "
    "a corporate checkpoint.",
    "Secure safe passage from the tunnel operators", "influence", 9,
    "The tunnel operators are businesspeople who value "
    "transaction more than ideology. You find the right "
    "framing — their long-term reputation, the intel "
    "value of goodwill, a specific future favour — "
    "and they clear a route through for the refugees. "
    "Four hours later, forty-two people are on the far side.",
    "The tunnel operators have a standing arrangement with "
    "the same faction that raided the refugees' settlement. "
    "The moment you identify who you're moving, the "
    "conversation ends and the entrance seals.",
    "Move the group through by memorising the patrol patterns", "stealth", 8,
    "You spend ninety minutes mapping the smuggler patrol "
    "routes through the first three sections. The patterns "
    "are consistent. You move the group in clusters of "
    "eight through the windows, communicating by hand "
    "signal. No contact. Everyone through.",
    "The patrol patterns change in the second section — "
    "a new smuggler faction has taken over that stretch "
    "and runs irregular rotations. Your timing model "
    "breaks and the group is stopped before the midpoint.",
    50, 3),

_mk("tm_w26", "Bone Ground", "wasteland", "wasteland_26_contaminated_battlefield",
    "Recover operational data from a contaminated battlefield before the site is sealed permanently.",
    "The battlefield has been radiologically contaminated "
    "for eleven years — a corporate tactical weapon that "
    "was never acknowledged. Somewhere in the debris field "
    "is a data recorder from an engagement your organisation "
    "needs to document. Meridian-Sato is sending a clean-up "
    "crew in seventy-two hours with orders to seal the site "
    "completely.",
    "Navigate the contamination safely with medical preparation", "medicine", 9,
    "Radiation distribution on a site this age is predictable "
    "if you understand how contamination migrates through "
    "soil and debris. You plan a route through the lower-dose "
    "corridors, dose-rate the approach on paper, and move "
    "through with appropriate protection. The recorder is "
    "under a collapsed vehicle. Total exposure: within safe limits.",
    "Your radiation assessment underestimates the hot spot "
    "concentration in the central debris field. The approach "
    "route you planned runs through levels that would "
    "produce a dangerous cumulative dose. You turn back.",
    "Access the data recorder through a remote signal interface", "tech", 8,
    "Military recorders broadcast a compressed status signal "
    "on a specific maintenance frequency for up to fifteen years. "
    "You locate the signal from the site perimeter, establish "
    "a handshake, and download the data partition remotely. "
    "No exposure required.",
    "The recorder's signal has been degraded by eleven years "
    "of radiation. The handshake protocol initiates but the "
    "data transfer fails before completion. You receive "
    "fragments — not enough.",
    60, 4),

_mk("tm_w27", "Supply Denial", "wasteland", "wasteland_27_logistics_depot",
    "Destroy a corporate logistics depot supplying a sustained offensive against civilian settlements.",
    "The depot at Grid Seven-Four runs fuel, ammunition, "
    "and rations to six forward positions. Without it, "
    "the offensive runs dry in four days. With it, "
    "three more settlements come under fire this week. "
    "The depot is guarded but not a hardened military "
    "installation — it was built for efficiency, not defence.",
    "Hit the depot fast before the guard cycle completes", "close_combat", 8,
    "The guard rotation has a four-minute window between "
    "the east and north positions. You go through the fence "
    "at the unobserved section, reach the primary fuel "
    "store, and set charges on the pressurised lines. "
    "The secondary explosions are visible from twelve kilometres.",
    "The guard rotation timing you were given is out of date. "
    "The window has been reduced to ninety seconds — not "
    "enough time to reach the fuel store and set charges.",
    "Sabotage the depot's supply tracking system", "tech", 8,
    "A depot this size coordinates resupply through "
    "a centralised logistics system. You access the "
    "inventory management node from a maintenance "
    "terminal and introduce systematic errors — wrong "
    "quantities, wrong destinations, false shortages. "
    "The depot continues to operate but begins "
    "delivering the wrong supplies to the wrong positions.",
    "The maintenance terminal is running an air-gapped "
    "system with no external connection. You would need "
    "physical access to every terminal in the depot "
    "to implement the changes, which takes longer "
    "than the mission window allows.",
    50, 3),

_mk("tm_w28", "Frequency", "wasteland", "wasteland_28_radio_shrine",
    "Protect the wasteland's independent radio shrine from corporate electronic warfare jamming.",
    "The radio shrine at Marker Nineteen has been broadcasting "
    "for nine years — weather reports, medical advisories, "
    "settlement news, missing persons. It is the only "
    "communications infrastructure that serves the independent "
    "settlements. Meridian-Sato has deployed a mobile jamming "
    "platform in the area. The shrine's operators have twelve "
    "hours before it becomes permanently inaudible.",
    "Locate and disable the jamming platform's transmitter", "tech", 8,
    "Jamming platforms leave their own signal signature — "
    "a suppression carrier that you can triangulate if "
    "you know what to listen for. You find the platform "
    "six kilometres north in a dry riverbed and disable "
    "its transmitter array in forty minutes. The shrine "
    "comes back online before sunset.",
    "The platform is military-spec and the transmitter "
    "is armoured against field disabling. You can get "
    "to it but you can't stop it with the equipment "
    "you have on site.",
    "Help the shrine operators build a frequency workaround", "tactics", 9,
    "The jamming platform covers a defined frequency range. "
    "With the right equipment and planning, the shrine can "
    "broadcast outside that range — the receivers would "
    "need to be retuned, but the signal would reach them. "
    "You spend six hours working with the shrine's engineers "
    "to implement the workaround across the settlement network.",
    "The jamming platform's frequency range is wider than "
    "the equipment at the shrine can accommodate. There is "
    "no frequency available outside its coverage that the "
    "settlements' receivers can pick up.",
    45, 3),

_mk("tm_w29", "Buried Intelligence", "wasteland", "wasteland_29_ewaste_landfill",
    "Recover a data archive from a corporate e-waste landfill before it is processed into scrap.",
    "The landfill at Site Eleven processes corporate e-waste "
    "legally. What it also processes — quietly, without "
    "documentation — is decommissioned hardware from operations "
    "the corporation would prefer not to have on record. "
    "An archive from an operation two years ago is somewhere "
    "in the current processing batch. Processing runs in "
    "eighteen hours.",
    "Identify the archive through medical-grade sensor analysis", "medicine", 7,
    "Medical-grade sensors can detect specific chemical compounds "
    "in organic and synthetic materials — including the "
    "preservative coating used on archival storage media. "
    "You scan the current batch systematically and the sensor "
    "pattern leads you to a sealed case in the third pile. "
    "The archive is intact.",
    "The archive's preservative coating has degraded — "
    "eleven months in an uncontrolled environment. "
    "The sensor signature is too faint to distinguish "
    "from background contamination in the landfill.",
    "Trace the archive through landfill intake records", "tech", 8,
    "The landfill runs an intake manifest for insurance "
    "liability purposes. The manifest is digital and "
    "poorly secured. You cross-reference intake dates "
    "with known operational timelines and find the "
    "shipment reference. The manifest includes a "
    "storage location code. The archive is exactly "
    "where the code says.",
    "The intake manifest uses an internal coding system "
    "that doesn't map to any physical location schema "
    "you can interpret. The codes are meaningless "
    "without the landfill's internal key, which "
    "is locked on a terminal you can't reach.",
    40, 2),

_mk("tm_w30", "Last Gate", "wasteland", "wasteland_30_storm_checkpoint",
    "Hold the last viable checkpoint during a sustained dust storm to prevent a hostile breakthrough.",
    "The storm rolled in at 0400 and it won't lift for "
    "eighteen hours. The checkpoint is the only crossing "
    "point for a hundred and sixty kilometres in either "
    "direction. Three hours ago a reconnaissance probe "
    "came through wearing civilian markings. In this "
    "visibility, a full hostile element could be at "
    "the gate in under thirty minutes and you wouldn't "
    "see them until they were close enough to matter.",
    "Fortify the checkpoint position using available materials", "tech", 8,
    "The checkpoint has a maintenance shed, a fuel cache, "
    "and three cargo containers that haven't moved in "
    "two years. You spend ninety minutes converting "
    "them into a defensible redoubt — elevated position, "
    "controlled approach lanes, an early warning system "
    "built from the shed's motion sensors. When the "
    "element arrives, they find a position they cannot "
    "take cheaply. They withdraw.",
    "The cargo containers are too heavy to reposition "
    "without equipment you don't have. The maintenance "
    "shed's motion sensors operate on a frequency "
    "that the storm disrupts completely. Your "
    "fortification plan collapses before it starts.",
    "Hold through the storm window using fire discipline", "composure", 9,
    "Eighteen hours is a long time to hold a checkpoint "
    "in zero visibility with insufficient personnel. "
    "You do it by making every decision deliberately — "
    "fields of fire, rotation schedules, ammunition "
    "allocation. When the element probes the perimeter "
    "at 1100, the response is immediate and controlled. "
    "They don't probe again.",
    "The storm's duration is longer than the forecast. "
    "At hour fourteen, fatigue and visibility conspire "
    "to create a gap in the perimeter. The probe at "
    "1600 finds it.",
    55, 4),

]  # end _WASTE


# ── Public API ─────────────────────────────────────────────────────────────────

_ALL_MISSIONS: list[TextMissionTemplate] = _CITY + _WASTE

_BY_ID: dict[str, TextMissionTemplate] = {m.id: m for m in _ALL_MISSIONS}


def all_text_missions() -> list[TextMissionTemplate]:
    return list(_ALL_MISSIONS)


def get_text_mission(mission_id: str) -> TextMissionTemplate | None:
    return _BY_ID.get(mission_id)


def text_missions_for_day(calendar_day: int, count: int = 6) -> list[TextMissionTemplate]:
    """Return a stable, day-keyed subset of missions for the world map board."""
    import hashlib
    seed = int(hashlib.md5(f"textmissions_{calendar_day}".encode()).hexdigest()[:8], 16)
    import random as _r
    rng = _r.Random(seed)
    pool = list(_ALL_MISSIONS)
    rng.shuffle(pool)
    return pool[:min(count, len(pool))]
