from jinja2 import Environment
from tui_forms.form.question import QuestionComputed
from tui_forms.form.question import QuestionConstant


def test_question_computed_respects_existing_answer():
    """Verify that QuestionComputed uses an existing answer if provided."""
    env = Environment()
    q = QuestionComputed(
        key="test_key",
        type="string",
        title="Test",
        description="",
        default="computed-{{ base }}",
    )
    answers = {"base": "value", "test_key": "user-override"}
    # Should use 'user-override' instead of computing 'computed-value'
    assert q.default_value(env, answers) == "user-override"


def test_question_computed_computes_when_missing():
    """Verify that QuestionComputed computes the value when answer is missing."""
    env = Environment()
    q = QuestionComputed(
        key="test_key",
        type="string",
        title="Test",
        description="",
        default="computed-{{ base }}",
    )
    answers = {"base": "value"}
    assert q.default_value(env, answers) == "computed-value"


def test_question_constant_respects_existing_answer():
    """Verify that QuestionConstant uses an existing answer if provided."""
    env = Environment()
    q = QuestionConstant(
        key="test_key",
        type="string",
        title="Test",
        description="",
        default="constant-value",
    )
    answers = {"test_key": "user-override"}
    assert q.default_value(env, answers) == "user-override"


def test_question_constant_uses_default_when_missing():
    """Verify that QuestionConstant uses the default when answer is missing."""
    env = Environment()
    q = QuestionConstant(
        key="test_key",
        type="string",
        title="Test",
        description="",
        default="constant-value",
    )
    answers = {}
    assert q.default_value(env, answers) == "constant-value"


def test_question_computed_with_root_key():
    """Verify QuestionComputed works with root_key nesting."""
    env = Environment()
    q = QuestionComputed(
        key="test_key",
        type="string",
        title="Test",
        description="",
        default="computed-{{ base }}",
    )
    answers = {"myroot": {"base": "value", "test_key": "user-override"}}
    assert q.default_value(env, answers, root_key="myroot") == "user-override"
