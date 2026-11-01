"""In-memory model of async jobs, idempotency and conditional GET. No network."""
from dataclasses import dataclass, field


@dataclass
class Response:
    status: int
    body: dict | None = None
    headers: dict[str, str] = field(default_factory=dict)


class ReportAPI:
    def __init__(self):
        self.keys: dict[str, tuple[str, int]] = {}
        self.jobs: dict[int, dict] = {}
        self.pending: list[int] = []

    def submit(self, key: str, payload: str) -> Response:
        if key in self.keys:
            original, job_id = self.keys[key]
            if original != payload:
                return Response(409, {"error": "key reused with another payload"})
        else:
            job_id = len(self.jobs) + 1
            self.keys[key] = (payload, job_id)
            self.jobs[job_id] = {"state": "queued", "version": 1}
            self.pending.append(job_id)
        return Response(202, {"job_id": job_id}, {"Location": f"/jobs/{job_id}"})

    def get(self, job_id: int, if_none_match: str | None = None) -> Response:
        job = self.jobs.get(job_id)
        if job is None:
            return Response(404)
        etag = f'"job-{job_id}-v{job["version"]}"'
        headers = {"ETag": etag, "Cache-Control": "private, no-cache"}
        if if_none_match == etag:
            return Response(304, headers=headers)
        return Response(200, dict(job), headers)

    def work(self) -> None:
        while self.pending:
            job_id = self.pending.pop(0)
            job = self.jobs[job_id]
            job.update(state="succeeded", result=f"report-{job_id}", version=job["version"] + 1)


def main():
    api = ReportAPI()
    accepted = api.submit("request-1", "month=2026-10")
    assert accepted.status == 202 and accepted.headers["Location"] == "/jobs/1"
    assert api.submit("request-1", "month=2026-10").body == accepted.body
    assert len(api.pending) == 1
    assert api.submit("request-1", "month=2026-11").status == 409
    queued = api.get(1)
    cached = api.get(1, queued.headers["ETag"])
    assert cached.status == 304 and cached.body is None
    api.work()
    completed = api.get(1, queued.headers["ETag"])
    assert completed.status == 200 and completed.body["state"] == "succeeded"
    assert api.get(999).status == 404
    assert api.get(1, completed.headers["ETag"]).status == 304
    print("202, stable job ID, deduplication, payload conflict, 200/304 and updated ETag verified.")


if __name__ == "__main__":
    main()
