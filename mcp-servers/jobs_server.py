from typing import Any, Dict, List
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("jobs")
REMOTIVE_API = "https://remotive.com/api/remote-jobs"

@mcp.tool()
def search_jobs(q: str, location: str = "", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search live jobs (Remotive public API). Returns dicts with:
    title, company, url, location, tags[], published_at, job_type, salary, description
    """
    params = {"search": q}
    results: List[Dict[str, Any]] = []
    with httpx.Client(timeout=20) as client:
        r = client.get(REMOTIVE_API, params=params)
        r.raise_for_status()
        data = r.json()
        for job in data.get("jobs", [])[:limit]:
            loc = job.get("candidate_required_location") or ""
            if location and location.lower() not in loc.lower():
                continue
            results.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "url": job.get("url"),
                "location": loc,
                "tags": job.get("tags", []),
                "job_type": job.get("job_type"),
                "published_at": job.get("publication_date"),
                "salary": job.get("salary", ""),
                "description": (job.get("description", "") or "")[:600]
            })
    return results

if __name__ == "__main__":
    mcp.run(transport="stdio")
