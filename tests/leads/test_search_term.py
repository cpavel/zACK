from ack.helpers import (
    build_hacker_news_oai_instruction,
    get_openai_models,
    hacker_news_client,
    run_reword,
)


def re_runnable_test(baker_make, reach_out_template):
    min_profile_length = 5
    prompt_template = baker_make(
        "data.PromptTemplate",
        template=reach_out_template,
        min_profile_length=min_profile_length,
    )
    response = hacker_news_client.search_hacker_news("django")
    response.json()["hits"][0]["comment_text"]
    hits = response.json()["hits"]
    assert hits

    found_viable_results = False

    for rec in hits:
        comment = rec["comment_text"]
        hn_username = rec["author"]
        profile_about, __ = hacker_news_client.get_hacker_news_profile(
            hn_username
        )
        if len(profile_about) < min_profile_length:
            continue

        pitch = build_hacker_news_oai_instruction(
            prompt_template=prompt_template,
            comment=comment,
            profile_about=profile_about,
        )
        reworded_pitch = run_reword(pitch)
        found_viable_results = True
        # Exit early, since it's a test.
        break

    # TODO: Iterate through fallback words for full test.
    if not found_viable_results:
        # Skip the test for now.
        return

    # TODO: Think about how to test that the reworded pitch is
    #       meaningfully written. Difficult at this point.
    assert reworded_pitch is not None


def test_hacker_news_lead_gen(
    enable_api_tests,
    reach_out_template,
    baker_make,
):
    if not enable_api_tests:
        # TODO: Use mocks or fakes here.
        assert True
        return

    re_runnable_test(baker_make, reach_out_template)
