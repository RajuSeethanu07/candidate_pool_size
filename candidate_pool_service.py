import os
import json
from datetime import datetime
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()


class CandidatePoolService:

    # ================= INIT ================= #

    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")

        if not self.api_key:
            raise ValueError("SERPAPI_KEY not found in .env file")

        self.cache_file = "cache.json"
        self._initialize_cache()

    def _initialize_cache(self):
        if not os.path.exists(self.cache_file):
            with open(self.cache_file, "w") as f:
                json.dump({}, f)

    # ================= CACHE ================= #

    def _load_cache(self):
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_cache(self, cache_data):
        with open(self.cache_file, "w") as f:
            json.dump(cache_data, f, indent=4)

    # ================= EXPERIENCE ================= #

    def _expand_experience(self, experience):

        if not experience:
            return ""

        experience = experience.lower().replace("years", "").strip()

        if "-" in experience:
            try:
                start, end = map(int, experience.split("-"))
                exp_terms = [f'"{year} years"' for year in range(start, end + 1)]
                return "(" + " OR ".join(exp_terms) + ")"
            except ValueError:
                return ""

        if experience.isdigit():
            return f'"{experience} years"'

        return f'"{experience}"'

    # ================= QUERY BUILDER ================= #

    def _build_query(self, title, location, skills, experience_range):

        # Clean and quote skills (STRICT AND matching)
        skills = [s.strip() for s in skills if s.strip()]
        skills_query = " ".join([f'"{skill}"' for skill in skills]) if skills else ""

        experience_query = self._expand_experience(experience_range)

        query = (
            f'site:linkedin.com/in/ '
            f'"{title}" '
            f'"{location}" '
            f'{skills_query} '
            f'{experience_query} '
            f'-intitle:jobs -inurl:jobs'
        )

        return " ".join(query.split())

    # ================= SERPAPI CALL ================= #

    def _call_serpapi(self, query):

        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key,
                "gl": "in",
                "hl": "en"
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            return results.get("search_information", {}).get("total_results", 0)

        except Exception as e:
            print(f"\n❌ SerpAPI call failed: {e}")
            return 0

    # ================= RESULT FORMATTER ================= #

    def _format_result(self, title, location, skills, experience_range, query, total_results):

        return {
            "title": title,
            "location": location,
            "skills": skills,
            "experience_range": experience_range,
            "optimized_query_used": query,
            "google_estimated_pool_size": total_results,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # ================= MAIN FUNCTION ================= #

    def get_candidate_pool_size(
        self,
        title,
        location,
        skills,
        experience_range=None
    ):

        query = self._build_query(title, location, skills, experience_range)

        cache = self._load_cache()

        if query in cache:
            return cache[query]

        total_results = self._call_serpapi(query)

        result_data = self._format_result(
            title,
            location,
            skills,
            experience_range,
            query,
            total_results
        )

        cache[query] = result_data
        self._save_cache(cache)

        return result_data