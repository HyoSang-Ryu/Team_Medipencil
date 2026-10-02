from medipencil.aggregation import intervals

def test_overnight_duplicates_missing_coverage():
    events=[{'kind':'enter','at':'2026-01-01T23:00:00+02:00'},{'kind':'enter','at':'2026-01-01T23:00:00+02:00'},{'kind':'leave','at':'2026-01-02T01:00:00+02:00'}]
    r=intervals(events,'2026-01-01T20:00:00Z','2026-01-02T02:00:00Z')
    assert r['seconds']==7200 and len(r['intervals'])==1
    assert intervals(events[:1],'2026-01-01T20:00:00Z','2026-01-02T02:00:00Z')['coverage_state']=='incomplete'
