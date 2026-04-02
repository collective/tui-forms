from tui_forms import form
from tui_forms.parser import jsonschema_to_form

import pytest


@pytest.fixture(scope="module")
def plone_schema(load_schema):
    """Load the plone-distribution JSON schema fixture."""
    return load_schema("plone-distribution.json")


@pytest.fixture(scope="module")
def plone_form(plone_schema):
    """Parse the plone-distribution schema into a Form instance."""
    return jsonschema_to_form(plone_schema)


def _question(frm: form.Form, key: str) -> form.BaseQuestion:
    """Return the question with the given key from a form."""
    questions = {q.key: q for q in frm.questions}
    return questions[key]


def _subquestion(frm: form.Form, parent_key: str, key: str) -> form.BaseQuestion | None:
    """Return a subquestion from a parent question by key."""
    parent = _question(frm, parent_key)
    return next((sq for sq in parent.subquestions if sq.key == key), None)


# --- Form metadata tests ---


def test_returns_form_instance(plone_form):
    """jsonschema_to_form should return a Form instance."""
    assert isinstance(plone_form, form.Form)


def test_form_title(plone_form):
    """The form title should match the schema."""
    assert plone_form.title == "kitconcept Intranet"


def test_form_description(plone_form):
    """The form description should match the schema."""
    assert plone_form.description == "Create a new Intranet based on Plone."


def test_form_question_count(plone_form):
    """The form should contain the expected number of questions."""
    assert len(plone_form.questions) == 10


# --- Question type tests ---


@pytest.mark.parametrize(
    "key,expected_class",
    [
        ("site_id", form.Question),
        ("setup_solr", form.QuestionBoolean),
        ("workflow", form.QuestionChoice),
        ("available_languages", form.QuestionMultiple),
    ],
)
def test_question_class(plone_form, key, expected_class):
    """Each key should parse to the expected question class."""
    assert isinstance(_question(plone_form, key), expected_class)


# --- String question (site_id) tests ---


def test_site_id_type(plone_form):
    """site_id should have type 'string'."""
    assert _question(plone_form, "site_id").type == "string"


def test_site_id_title(plone_form):
    """site_id should have the expected title."""
    assert _question(plone_form, "site_id").title == "Path Identifier"


def test_site_id_description(plone_form):
    """site_id should have a non-empty description."""
    assert _question(plone_form, "site_id").description != ""


def test_site_id_default(plone_form):
    """site_id should have the expected default value."""
    assert _question(plone_form, "site_id").default == "Plone"


# --- Boolean question tests ---


def test_boolean_question_type(plone_form):
    """setup_solr should have type 'boolean'."""
    assert _question(plone_form, "setup_solr").type == "boolean"


@pytest.mark.parametrize(
    "key,expected_default",
    [
        ("setup_solr", False),
        ("setup_content", True),
    ],
)
def test_boolean_default(plone_form, key, expected_default):
    """Boolean questions should have the expected default values."""
    assert _question(plone_form, key).default is expected_default


# --- Multiple question (available_languages) tests ---


def test_available_languages_type(plone_form):
    """available_languages should have type 'array'."""
    assert _question(plone_form, "available_languages").type == "array"


def test_available_languages_has_options(plone_form):
    """available_languages should have options."""
    assert _question(plone_form, "available_languages").options is not None


def test_available_languages_option_count(plone_form):
    """available_languages should have exactly two options."""
    assert len(_question(plone_form, "available_languages").options) == 2


@pytest.mark.parametrize(
    "index,expected_const,expected_title",
    [
        (0, "de", "Deutsch"),
        (1, "en", "English"),
    ],
)
def test_available_languages_option(plone_form, index, expected_const, expected_title):
    """Each available_languages option should have the expected const and title."""
    opt = _question(plone_form, "available_languages").options[index]
    assert opt["const"] == expected_const
    assert opt["title"] == expected_title


def test_available_languages_default(plone_form):
    """available_languages should default to ['de']."""
    assert _question(plone_form, "available_languages").default == ["de"]


# --- Choice question (workflow) tests ---


def test_workflow_has_options(plone_form):
    """workflow should have options."""
    assert _question(plone_form, "workflow").options is not None


def test_workflow_option_count(plone_form):
    """workflow should have exactly two options."""
    assert len(_question(plone_form, "workflow").options) == 2


@pytest.mark.parametrize(
    "index,expected_const,expected_title",
    [
        (0, "restricted", "Requires authentication"),
        (1, "public", "Public access"),
    ],
)
def test_workflow_option(plone_form, index, expected_const, expected_title):
    """Each workflow option should have the expected const and title."""
    opt = _question(plone_form, "workflow").options[index]
    assert opt["const"] == expected_const
    assert opt["title"] == expected_title


def test_workflow_default(plone_form):
    """workflow should default to 'public'."""
    assert _question(plone_form, "workflow").default == "public"


# --- Object question (authentication) tests ---


def test_authentication_type(plone_form):
    """authentication should have type 'object'."""
    assert _question(plone_form, "authentication").type == "object"


def test_authentication_has_subquestions(plone_form):
    """authentication should have subquestions."""
    assert _question(plone_form, "authentication").subquestions is not None


def test_authentication_provider_present(plone_form):
    """authentication should contain a 'provider' subquestion."""
    auth = _question(plone_form, "authentication")
    provider = next((sq for sq in auth.subquestions if sq.key == "provider"), None)
    assert provider is not None


def test_authentication_provider_option_count(plone_form):
    """authentication.provider should have exactly five options."""
    auth = _question(plone_form, "authentication")
    provider = next(sq for sq in auth.subquestions if sq.key == "provider")
    assert provider.options is not None
    assert len(provider.options) == 5


def test_authentication_provider_option_consts(plone_form):
    """authentication.provider options should contain all expected const values."""
    auth = _question(plone_form, "authentication")
    provider = next(sq for sq in auth.subquestions if sq.key == "provider")
    consts = {opt["const"] for opt in provider.options}
    assert consts == {
        "internal",
        "keycloak",
        "oidc",
        "authomatic-google",
        "authomatic-github",
    }


@pytest.mark.parametrize(
    "key",
    [
        "oidc-server_url",
        "oidc-realm_name",
        "oidc-client_id",
        "oidc-client_secret",
        "oidc-site-url",
        "oidc-scope",
        "oidc-issuer",
        "authomatic-github-consumer_key",
        "authomatic-github-consumer_secret",
        "authomatic-github-scope",
        "authomatic-google-consumer_key",
        "authomatic-google-consumer_secret",
        "authomatic-google-scope",
    ],
)
def test_authentication_conditional_subquestion_present(plone_form, key):
    """Each expected conditional subquestion should be present under authentication."""
    sub_keys = {sq.key for sq in _question(plone_form, "authentication").subquestions}
    assert key in sub_keys


def test_authentication_no_duplicate_subquestions(plone_form):
    """authentication should have no duplicate subquestion keys."""
    sub_keys = [sq.key for sq in _question(plone_form, "authentication").subquestions]
    assert len(sub_keys) == len(set(sub_keys))


# --- Conditional subquestion condition tests ---


def test_unconditional_subquestion_has_no_condition(plone_form):
    """The 'provider' subquestion should have no condition."""
    provider = _subquestion(plone_form, "authentication", "provider")
    assert provider.condition is None


@pytest.mark.parametrize(
    "key,expected_condition",
    [
        ("oidc-server_url", [{"key": "provider", "value": "keycloak"}]),
        ("oidc-issuer", [{"key": "provider", "value": "oidc"}]),
        (
            "authomatic-github-consumer_key",
            [{"key": "provider", "value": "authomatic-github"}],
        ),
        (
            "authomatic-google-consumer_key",
            [{"key": "provider", "value": "authomatic-google"}],
        ),
    ],
)
def test_conditional_subquestion_condition(plone_form, key, expected_condition):
    """Each conditional subquestion should carry the expected condition."""
    sq = _subquestion(plone_form, "authentication", key)
    assert sq.condition == expected_condition


# --- Top-level allOf/if/then tests (issue #20) ---


@pytest.fixture(scope="module")
def ifthen_form(load_schema):
    """Parse the rjsf-if-then-else schema into a Form instance."""
    return jsonschema_to_form(load_schema("rjsf-if-then-else.json"))


def test_top_level_allof_creates_conditional_questions(ifthen_form):
    """Top-level allOf/if/then should produce conditional questions."""
    keys = {q.key for q in ifthen_form.questions}
    assert "food" in keys
    assert "water" in keys


@pytest.mark.parametrize(
    "key,expected_condition",
    [
        ("food", [{"key": "animal", "value": "Cat"}]),
        ("water", [{"key": "animal", "value": "Fish"}]),
    ],
)
def test_top_level_allof_condition_values(ifthen_form, key, expected_condition):
    """Conditional questions from top-level allOf should carry the correct condition."""
    q = _question(ifthen_form, key)
    assert q.condition == expected_condition


def test_top_level_allof_unconditional_question(ifthen_form):
    """The non-conditional question should have no condition."""
    q = _question(ifthen_form, "animal")
    assert q.condition is None


def test_top_level_allof_required_propagated(ifthen_form):
    """Required keys from then blocks should propagate to the question."""
    food = _question(ifthen_form, "food")
    water = _question(ifthen_form, "water")
    assert food.required is True
    assert water.required is True


# --- Required field tests ---


@pytest.mark.parametrize(
    "key,expected_required",
    [
        ("site_id", True),
        ("title", True),
        ("available_languages", True),
        ("workflow", True),
        ("authentication", True),
        ("default_language", False),
    ],
)
def test_required_flag_parsed(plone_form, key, expected_required):
    """Questions listed in the schema required array should have required=True."""
    q = _question(plone_form, key)
    assert q.required is expected_required
