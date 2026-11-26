from interior_batch import INTERIORS, fixtures


def test_interior_batch_limits_replacements_to_modelled_footprints():
    for name in INTERIORS:
        survey, selected = fixtures(name)
        assert "wall" in selected.values()
        assert set(selected) <= {row["id"] for row in survey["walls"] if "rect" in row or "points" in row}
        assert not any(identifier.startswith("outside_") for identifier in selected)

    _, clinic = fixtures("cybercity_inner_04_medical_clinic")
    _, lab = fixtures("cybercity_inner_06_blacksite_lab")
    _, warehouse = fixtures("cybercity_inner_13_warehouse_floor")
    assert clinic["east_bed1"] == "bed"
    assert lab["west_pods"] == "pod"
    assert warehouse["shelf_mid"] == "rack"
    assert lab["west_partition_n"] == "partition"
