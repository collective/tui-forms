from tui_forms.form.form import Form
from tui_forms.form.question import Question


def test_is_active_with_root_key():
    """Verify that is_active correctly finds answers when a root_key is used."""
    q_cond = Question(
        key="thumbor",
        type="boolean",
        title="Thumbor",
        description="",
        default=False,
        condition=[{"key": "postgres", "value": True}],
    )

    # Without root_key
    frm1 = Form(title="T", description="", questions=[q_cond])
    frm1.record("postgres", True)
    assert frm1.is_active(q_cond) is True

    # With root_key (e.g. cookiecutter)
    frm2 = Form(title="T", description="", questions=[q_cond], root_key="cookiecutter")
    frm2.record("postgres", True)
    # This is expected to FAIL before the fix
    assert frm2.is_active(q_cond) is True


def test_user_answers_with_root_key():
    """Verify that user_answers correctly retrieves answers when a root_key is used."""
    q = Question(key="a", type="string", title="A", description="", default="")
    frm = Form(title="T", description="", questions=[q], root_key="cookiecutter")

    frm.record("a", "val", user_provided=True)

    # This should return {'a': 'val'}
    # Before fix it might raise KeyError or return wrong data depending on implementation
    assert frm.user_answers == {"a": "val"}


def test_user_answers_empty_with_root_key():
    """Verify that user_answers doesn't crash when no answers recorded yet with root_key."""
    frm = Form(title="T", description="", questions=[], root_key="cookiecutter")
    assert frm.user_answers == {}
