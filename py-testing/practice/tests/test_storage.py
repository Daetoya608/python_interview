import pytest

from study_app.storage import Notes

pytestmark = pytest.mark.integration


def test_add_and_read_note(notes):
    note_id = notes.add("Learn fixtures")
    assert notes.get(note_id) == "Learn fixtures"


def test_missing_note(notes):
    assert notes.get(999) is None


@pytest.mark.parametrize("title", ["", " ", "\t"])
def test_empty_title_is_rejected(notes, title):
    with pytest.raises(ValueError, match="title must not be empty"):
        notes.add(title)


def test_note_persists_after_reopening(tmp_path):
    path = tmp_path / "persistent.db"
    first = Notes(path)
    try:
        note_id = first.add("Persistent note")
    finally:
        first.close()
    second = Notes(path)
    try:
        assert second.get(note_id) == "Persistent note"
    finally:
        second.close()


def test_sql_like_title_is_stored_as_data(notes):
    title = "'); DROP TABLE notes; --"
    note_id = notes.add(title)
    assert notes.get(note_id) == title
    assert notes.get(notes.add("Still works")) == "Still works"
