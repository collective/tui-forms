from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from tui_forms.form.question import BaseQuestion
from typing import Any


@dataclass
class Form:
    """Renderer-agnostic representation of a form.

    Tracks the current question index and collected answers so that
    renderers only need to handle I/O rather than state management.
    """

    title: str
    description: str
    questions: list[BaseQuestion]
    answers: dict[str, Any] = field(default_factory=dict)
    root_key: str = ""
    _question_index: int = field(default=0, init=False, repr=False)
    _user_answers: set[str] = field(default_factory=set, init=False, repr=False)

    @property
    def user_answers(self) -> dict[str, Any]:
        """Return question data answered by the user."""
        answers = self.answers
        if root_key := self.root_key:
            answers = answers[root_key]
        user_answers = {k: answers[k] for k in self._user_answers}
        return user_answers

    @property
    def question_index(self) -> int:
        """1-based index of the question currently being asked."""
        return self._question_index

    @property
    def question_total(self) -> int:
        """Total number of visible (non-hidden, active) leaf questions."""
        return self._count_visible(self.questions)

    def is_active(self, question: BaseQuestion) -> bool:
        """Return True if all of the question's conditions are satisfied.

        :param question: The question to check.
        :return: True when the question should be shown or computed.
        """
        if question.condition is None:
            return True
        return all(
            self.answers.get(cond["key"]) == cond["value"]
            for cond in question.condition
        )

    def start(self) -> None:
        """Reset the form to its initial state for a fresh rendering pass."""
        self.answers.clear()
        self._user_answers.clear()
        self._question_index = 0

    def advance(self) -> None:
        """Advance the question index by one."""
        self._question_index += 1

    def record(self, key: str, value: Any, user_provided: bool = False) -> None:
        """Record an answer for the given question key.

        :param key: The question key.
        :param value: The answer value.
        :param user_provided: When True, the answer came from a user interaction
            (either accepting the suggested default or entering a new value) and
            the key is added to ``_user_answers``.
        """
        answers = self.answers
        if self.root_key:
            if self.root_key not in answers:
                answers[self.root_key] = {}
            answers = answers[self.root_key]
        answers[key] = value
        if user_provided:
            self._user_answers.add(key)

    def set_question_index(self, n: int) -> None:
        """Set the question index directly.

        :param n: The new 1-based question index.
        """
        self._question_index = n

    def unrecord(self, key: str) -> None:
        """Remove an answer for the given question key.

        :param key: The question key to remove.
        """
        answers = self.answers
        if self.root_key:
            answers = answers.get(self.root_key, {})
        answers.pop(key, None)
        self._user_answers.discard(key)

    def iter_all(self) -> Iterator[BaseQuestion]:
        """Yield every question and its subquestions depth-first.

        :return: An iterator over all questions and subquestions.
        """
        return self._iter_all(self.questions)

    def _count_visible(self, questions: list[BaseQuestion]) -> int:
        """Recursively count non-hidden, active leaf questions.

        Object-type questions are not counted; their subquestions are
        traversed instead. Conditional questions that are not active given
        the current answers are excluded.

        :param questions: The questions to count.
        :return: Total number of user-facing leaf questions currently active.
        """
        count = 0
        for question in questions:
            if question.hidden:
                continue
            if not self.is_active(question):
                continue
            if question.type == "object" and question.subquestions:
                count += self._count_visible(question.subquestions)
            else:
                count += 1
        return count

    def _iter_all(self, questions: list[BaseQuestion]) -> Iterator[BaseQuestion]:
        """Recursively yield questions and their subquestions depth-first.

        :param questions: The questions to iterate.
        """
        for question in questions:
            yield question
            if question.subquestions:
                yield from self._iter_all(question.subquestions)
