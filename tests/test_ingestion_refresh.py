import unittest

from jobpulse.ingestion.parser import extract_jobs, parse_html


class IngestionRefreshTests(unittest.TestCase):
    def test_missing_listing_description_is_filled_from_detail_page(self):
        listing_html = """
        <ol class="list-recent-jobs">
          <li>
            <span class="listing-company-name">
              <a href="/jobs/123/backend/">Backend Engineer</a><br/>JobPulse
            </span>
            <span class="listing-location">Remote</span>
            <span class="listing-posted">Posted: 28 September 2026</span>
          </li>
        </ol>
        """
        detail_html = """
        <div class="job-description">
          <p>Build and maintain APIs.</p>
          <p>Collaborate with the platform team.</p>
        </div>
        """

        jobs = extract_jobs(
            parse_html(listing_html),
            detail_fetcher=lambda url: detail_html,
        )

        self.assertEqual(jobs[0].source_job_id, "123")
        self.assertEqual(
            jobs[0].description,
            "Build and maintain APIs. Collaborate with the platform team.",
        )


if __name__ == "__main__":
    unittest.main()