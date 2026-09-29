import json
import unittest
from uuid import UUID
from unittest.mock import patch

from jobpulse.ai.resume import ResumeProfile
from jobpulse.database import repository


class FakeCursor:
    def __init__(self, row=None):
        self.executed = []
        self.row = row

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self.row

    def close(self):
        pass


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_instance = cursor
        self.committed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def close(self):
        pass


class ResumeRepositoryTests(unittest.TestCase):
    def profile(self):
        return ResumeProfile(
            name="Alex Smith",
            summary="Backend engineer",
            skills=["Python"],
            technologies=["PostgreSQL"],
            experience=[{
                "company": "DataWorks",
                "role": "Engineer",
                "duration": "2022-2026",
                "description": "Built APIs",
            }],
            education=[{
                "institution": "University",
                "degree": "BSc",
                "field": "Computer Science",
                "year": "2020",
            }],
            projects=[{
                "name": "JobPulse",
                "description": "Resume intelligence platform",
                "technologies": ["Python"],
            }],
        )

    def test_successful_insert_returns_uuid_and_serializes_jsonb(self):
        cursor = FakeCursor()
        connection = FakeConnection(cursor)
        with patch.object(repository, "connect_db", return_value=connection):
            resume_id = repository.save_resume_profile(self.profile())

        query, params = cursor.executed[0]
        self.assertIsInstance(resume_id, UUID)
        self.assertIn("INSERT INTO resume_profiles", query)
        self.assertEqual(params[0], str(resume_id))
        self.assertEqual(params[1:3], ("Alex Smith", "Backend engineer"))
        self.assertEqual(params[3].adapted, ["Python"])
        self.assertEqual(params[4].adapted, ["PostgreSQL"])
        self.assertEqual(
            params[5].adapted,
            [{
                "company": "DataWorks",
                "role": "Engineer",
                "duration": "2022-2026",
                "description": "Built APIs",
            }],
        )
        self.assertEqual(
            params[6].adapted,
            [{
                "institution": "University",
                "degree": "BSc",
                "field": "Computer Science",
                "year": "2020",
            }],
        )
        self.assertEqual(
            params[7].adapted,
            [{
                "name": "JobPulse",
                "description": "Resume intelligence platform",
                "technologies": ["Python"],
            }],
        )
        self.assertTrue(connection.committed)

    def test_successful_retrieval_deserializes_jsonb(self):
        profile = self.profile()
        cursor = FakeCursor(
            (
                profile.name,
                profile.summary,
                json.dumps(profile.skills),
                json.dumps(profile.technologies),
                json.dumps([item.model_dump() for item in profile.experience]),
                json.dumps([item.model_dump() for item in profile.education]),
                json.dumps([item.model_dump() for item in profile.projects]),
            )
        )
        connection = FakeConnection(cursor)
        resume_id = UUID("11111111-1111-1111-1111-111111111111")
        with patch.object(repository, "connect_db", return_value=connection):
            result = repository.get_resume_profile(resume_id)

        self.assertEqual(result, profile)
        self.assertEqual(cursor.executed[0][1], (str(resume_id),))

    def test_missing_profile_returns_none(self):
        cursor = FakeCursor()
        connection = FakeConnection(cursor)
        with patch.object(repository, "connect_db", return_value=connection):
            result = repository.get_resume_profile(UUID(int=0))

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()