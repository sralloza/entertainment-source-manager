import pytest
from pydantic import ValidationError

from app.models.inputs import SpyXFamilyInputs


class TestSpyXFamilyInputs:
    def test_source_name_overriten(self):
        with pytest.raises(ValidationError, match=self.get_msg("source_name")):
            self.build_inputs(source_name="test")

    def test_source_encoded_name_overriten(self):
        with pytest.raises(ValidationError, match=self.get_msg("source_encoded_name")):
            self.build_inputs(source_encoded_name="test")

    def get_msg(self, field):
        return f"{field} cannot be overwritten in SpyXFamilyInputs"

    def build_inputs(self, **kwargs):
        return SpyXFamilyInputs(todoist_project_id="test", todoist_section_id="test", **kwargs)
