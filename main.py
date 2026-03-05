from candidate_pool_service import CandidatePoolService


def main():

    # ---------------- INITIALIZE SERVICE ---------------- #
    service = CandidatePoolService()

    print("\n🎯 Enter Candidate Search Details\n")

    # ---------------- USER INPUT ---------------- #
    title = input("Enter Job Title: ").strip()
    location = input("Enter Location: ").strip()

    skills_input = input("Enter Skills (comma separated): ").strip()
    skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]

    experience_range = input("Enter Experience Range (e.g., 3-5 years) [optional]: ").strip()
    experience_range = experience_range if experience_range else None

    print("\n🚀 Fetching Progressive Candidate Pool Sizes...\n")

    print(f"Location: {location}\n")

    # ---------------- PROGRESSIVE SKILL SEARCH ---------------- #
    try:
        for i in range(1, len(skills) + 1):

            current_skills = skills[:i]

            result = service.get_candidate_pool_size(
                title=title,
                location=location,
                skills=current_skills,
                experience_range=experience_range
            )

            skill_display = " + ".join(current_skills)
            pool_size = result["google_estimated_pool_size"]
            query_used = result["optimized_query_used"]

            print(f"{title} + ({skill_display}) = {pool_size:,}")
            print(f"Query Used: {query_used}")
            print("-" * 100)
            print()

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")


if __name__ == "__main__":
    main()