from tui_forms.form.form import Form
from tui_forms.form.question import BaseQuestion
from tui_forms.form.question import Question
from tui_forms.form.question import QuestionBoolean
from tui_forms.form.question import QuestionConstant
from tui_forms.parser import jsonschema_to_form
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def make_question():
    """Return a factory for minimal Question instances."""

    def factory(
        key: str = "x",
        *,
        q_type: str = "string",
        hidden: bool = False,
        condition: dict[str, Any] | None = None,
        subquestions: list[BaseQuestion] | None = None,
    ) -> Question:
        """Build a minimal Question with the given key and options."""
        return Question(
            key=key,
            type=q_type,
            title=key.upper(),
            description="",
            default="",
            hidden=hidden,
            condition=condition,
            subquestions=subquestions,
        )

    return factory


@pytest.fixture
def simple_form(make_question):
    """Return a Form with two visible string questions."""
    return Form(
        title="Test",
        description="",
        questions=[make_question("a"), make_question("b")],
    )


# ---------------------------------------------------------------------------
# is_active
# ---------------------------------------------------------------------------


def test_is_active_no_condition(simple_form, make_question):
    """A question with no condition is always active."""
    q = make_question("x")
    assert simple_form.is_active(q) is True


@pytest.mark.parametrize(
    "answers,expected",
    [
        ({"provider": "keycloak"}, True),
        ({"provider": "other"}, False),
        ({}, False),
    ],
)
def test_is_active_with_condition(make_question, answers, expected):
    """A question with a condition is active only when the condition is satisfied."""
    frm = Form(title="T", description="", questions=[])
    frm.answers.update(answers)
    q = make_question("x", condition=[{"key": "provider", "value": "keycloak"}])
    assert frm.is_active(q) is expected


@pytest.mark.parametrize(
    "answers,expected",
    [
        ({"a": "1", "b": "2"}, True),
        ({"a": "1", "b": "other"}, False),
        ({"a": "other", "b": "2"}, False),
        ({"a": "1"}, False),
        ({}, False),
    ],
)
def test_is_active_with_multiple_conditions(make_question, answers, expected):
    """All conditions must be satisfied (AND logic) for the question to be active."""
    frm = Form(title="T", description="", questions=[])
    frm.answers.update(answers)
    q = make_question(
        "x",
        condition=[{"key": "a", "value": "1"}, {"key": "b", "value": "2"}],
    )
    assert frm.is_active(q) is expected


# ---------------------------------------------------------------------------
# start / advance / record / question_index
# ---------------------------------------------------------------------------


def test_start_clears_answers(simple_form):
    """start() should clear any pre-existing answers."""
    simple_form.answers["a"] = "hello"
    simple_form.start()
    assert simple_form.answers == {}


def test_start_resets_index(simple_form):
    """start() should reset the question index to zero."""
    simple_form.advance()
    simple_form.start()
    assert simple_form.question_index == 0


def test_advance_increments_index(simple_form):
    """advance() should increment question_index by one each call."""
    assert simple_form.question_index == 0
    simple_form.advance()
    assert simple_form.question_index == 1
    simple_form.advance()
    assert simple_form.question_index == 2


def test_record_stores_answer(simple_form):
    """record() should store the value under the given key in answers."""
    simple_form.record("a", "hello")
    assert simple_form.answers["a"] == "hello"


def test_record_overwrites_existing_answer(simple_form):
    """record() should overwrite a previously recorded answer."""
    simple_form.record("a", "first")
    simple_form.record("a", "second")
    assert simple_form.answers["a"] == "second"


def test_record_user_provided_adds_to_user_answers(simple_form):
    """record() with user_provided=True should add the key to _user_answers."""
    simple_form.record("a", "hello", user_provided=True)
    assert "a" in simple_form._user_answers


def test_record_not_user_provided_does_not_add_to_user_answers(simple_form):
    """record() with user_provided=False (default) should not touch _user_answers."""
    simple_form.record("a", "hello")
    assert "a" not in simple_form._user_answers


def test_start_clears_user_answers(simple_form):
    """start() should clear _user_answers alongside answers."""
    simple_form.record("a", "hello", user_provided=True)
    simple_form.start()
    assert simple_form._user_answers == set()


# ---------------------------------------------------------------------------
# question_total / count_visible
# ---------------------------------------------------------------------------


def test_question_total_all_visible(simple_form):
    """question_total should count all non-hidden questions."""
    assert simple_form.question_total == 2


def test_question_total_skips_hidden(make_question):
    """question_total should not count hidden questions."""
    frm = Form(
        title="T",
        description="",
        questions=[
            make_question("a"),
            make_question("b", hidden=True),
        ],
    )
    assert frm.question_total == 1


def test_question_total_skips_inactive(make_question):
    """question_total should not count questions whose condition is not met."""
    frm = Form(
        title="T",
        description="",
        questions=[
            make_question("a"),
            make_question("b", condition=[{"key": "a", "value": "yes"}]),
        ],
    )
    # condition not satisfied → only 1 visible
    assert frm.question_total == 1
    frm.record("a", "yes")
    # condition now satisfied → 2 visible
    assert frm.question_total == 2


def test_question_total_recurses_into_object(make_question):
    """question_total should count subquestions of object-type questions."""
    obj = make_question(
        "parent",
        q_type="object",
        subquestions=[make_question("sub1"), make_question("sub2")],
    )
    frm = Form(title="T", description="", questions=[obj])
    assert frm.question_total == 2


def test_question_total_object_skips_hidden_subquestion(make_question):
    """question_total should skip hidden subquestions of object questions."""
    obj = make_question(
        "parent",
        q_type="object",
        subquestions=[
            make_question("sub1"),
            make_question("sub2", hidden=True),
        ],
    )
    frm = Form(title="T", description="", questions=[obj])
    assert frm.question_total == 1


# ---------------------------------------------------------------------------
# iter_all
# ---------------------------------------------------------------------------


def test_iter_all_yields_all_questions(simple_form, make_question):
    """iter_all should yield every top-level question."""
    keys = [q.key for q in simple_form.iter_all()]
    assert keys == ["a", "b"]


def test_iter_all_depth_first_with_subquestions(make_question):
    """iter_all should yield parent then its subquestions depth-first."""
    obj = make_question(
        "parent",
        q_type="object",
        subquestions=[make_question("sub1"), make_question("sub2")],
    )
    frm = Form(title="T", description="", questions=[obj, make_question("sibling")])
    keys = [q.key for q in frm.iter_all()]
    assert keys == ["parent", "sub1", "sub2", "sibling"]


def test_iter_all_includes_hidden_questions(make_question):
    """iter_all should yield hidden questions too (all questions, unconditionally)."""
    hidden_q = QuestionConstant(
        key="h", type="string", title="H", description="", default="v"
    )
    frm = Form(title="T", description="", questions=[make_question("a"), hidden_q])
    keys = [q.key for q in frm.iter_all()]
    assert "h" in keys


def test_iter_all_empty_form():
    """iter_all on a form with no questions should yield nothing."""
    frm = Form(title="T", description="", questions=[])
    assert list(frm.iter_all()) == []


# ---------------------------------------------------------------------------
# QuestionBoolean as a spot-check that is_active works with any question type
# ---------------------------------------------------------------------------


def test_is_active_boolean_question():
    """is_active should work for QuestionBoolean instances too."""
    q = QuestionBoolean(
        key="b",
        type="boolean",
        title="B",
        description="",
        default=False,
        condition=[{"key": "flag", "value": "on"}],
    )
    frm = Form(title="T", description="", questions=[q])
    assert frm.is_active(q) is False
    frm.record("flag", "on")
    assert frm.is_active(q) is True


# ---------------------------------------------------------------------------
# question_total with a real-world schema (cookieplone)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def cookieplone_schema(load_schema):
    """Load the cookieplone JSON schema fixture."""
    return load_schema("cookieplone.json")


@pytest.fixture(scope="module")
def cookieplone_form(cookieplone_schema):
    """Parse the cookieplone schema into a Form instance."""
    return jsonschema_to_form(cookieplone_schema)


def test_question_total_counts_all_visible_cookieplone(cookieplone_form):
    """question_total should count every visible leaf question in the cookieplone form.

    The cookieplone schema has 65 properties, but only 19 are visible by default
    due to conditions and hidden flags.
    """
    assert cookieplone_form.question_total == 19
