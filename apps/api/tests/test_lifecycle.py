import pytest
from medipencil.lifecycle import cleanup_run,ensure_run,run_lock
from medipencil.common import Fault

def test_dry_run_explicit_confirmation_and_active_lock(app):
    root=app.state.settings.root;app.state.store.engine.dispose()
    result=cleanup_run(root)
    assert result['deleted_count']==0 and (root/'demo.sqlite').exists()
    with pytest.raises(Fault):cleanup_run(root,confirm='wrong',dry_run=False)
    with run_lock(root):
        with pytest.raises(Fault):cleanup_run(root)
    cleaned=cleanup_run(root,confirm=result['run_id'],dry_run=False)
    assert cleaned['deleted_count']>0 and not (root/'demo.sqlite').exists()

def test_cleanup_unknown_file_is_preserved(app):
    root=app.state.settings.root;(root/'unrelated.txt').write_text('keep')
    with pytest.raises(Fault):cleanup_run(root)
    assert (root/'unrelated.txt').read_text()=='keep'
