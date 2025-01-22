import glob

from zACK import enums
from zACK.env import ENABLE_REAL_CELERY_IN_TESTING
from zACK.tasks import search_leads


# TODO: Fix test
def test_search_term_by_id_task(
    user,
    baker_make,
    enable_celery_tests,
    reach_out_template,
    city_check_evaluation_template,
):
    initial_count = len(glob.glob1(f"./tmp/{user.id}", "*.xlsx"))

    location = enums.SearchLocation.HACKER_NEWS
    search_term = baker_make(
        "data.SearchTerm",
        user=user,
        term="Python",
        location=location,
    )

    evaluation_template = baker_make(
        "data.EvaluationTemplate",
        template=city_check_evaluation_template,
    )

    prompt_template = baker_make(
        "data.PromptTemplate",
        min_profile_length=5,
        max_profile_length=1000,
        template=reach_out_template,
        search_terms=[search_term],
        evaluation_template=evaluation_template,
    )

    search_leads(search_term_id=search_term.id)

    assert initial_count + 1 == len(glob.glob1(f"./tmp/{user.id}", "*.xlsx"))
