# CyberCity 2085 authoring assets

Large animation source sheets live in the private sibling repository
`llankar/CyberCity2085-SourceAssets`. They are production evidence and inputs,
not runtime game files.

Clone both repositories as siblings:

```text
Cybercity-2085/
  CyberCity2085/
  CyberCity2085-SourceAssets/
```

Tools discover that sibling automatically. Set `CYBERCITY_SOURCE_ASSETS` to
the source repository root when using another layout. Runtime packaging and
the Godot client consume only `assets/combat_visual/animations`.
