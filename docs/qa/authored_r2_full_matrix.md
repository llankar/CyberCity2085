# Completed R2 authored matrix

The previously running job finished: **1,098 cases, 958 victories, 118 defeats,
22 turn limits, no geometry errors**. Exact coverage is 122 maps times nine
objective kinds at seed zero, four level-4 rifle agents, six enemies/risk 5 and
the unchanged 60-turn cap. Every row's manual-survey hash was checked.

The code fingerprint matches the captured R2 pre-pilot snapshot:
`aa0a267bf0b173577db61feafdf4757e8a7492b754f04a42217b99937490ded7`.
The process had already loaded its code before pilot corrections; this is not
represented as a full current-pilot-source run. See
[per-objective totals and all limited cases](authored_r2_summary.json).

The post-clinic/pre-spacing baseline had 957 wins, 121 defeats and 20 limits.
The R2 containment subset changes from 20 wins/102 defeats to 21 wins/99 defeats/
two limits; other objective totals are unchanged. This comparison preserves the
same complete input set rather than adding historical partial replay totals.

Seven maps retain limited cases, including two collapsed-tunnel entries. The
power-substation and research-lab containment cases account for the two new
limits. These are unresolved pacing/route-design issues, not silently converted
to victories or hidden by a higher cap. Fixed-rifle results do not establish
balance, mixed-role success or human playability.

Raw data: `runtime/authored_r2_full_matrix.json`. The immutable R2 ZIP was built
before this long measurement completed, so its archive is not rewritten to
pretend this report was present at build time. The derived report is stored
beside this document. No desktop control was used.
