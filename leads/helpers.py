import datetime as dt
import os
from dataclasses import dataclass
from data.models import SearchTerm
from campaigns.models import Campaign

import xlsxwriter

from zACK import enums

RESULTS_DIR = "./tmp/"
RESULTS_FILE_NAME = "{}leadresults-{}.xlsx"


@dataclass
# TODO: Deprecate
class LeadSearchResult:
    campaign: Campaign
    search_term: SearchTerm
    location: enums.SearchLocation
    username: str
    profile_about: str
    profile_url: str
    comment: str
    prompt_template: str = ""
    prompt_request_text: str = ""
    prompt_response_text: str = ""
    evaluate_request_text: str = ""
    evaluate_response_text: str = ""
    score: int = -1


@dataclass
class CampaignLeadSearchResult:
    campaign: Campaign
    location: enums.SearchLocation
    username: str
    profile_about: str
    profile_url: str
    comment: str
    comment_url: str = ""
    prompt_template: str = ""
    prompt_request_text: str = ""
    prompt_response_text: str = ""
    post_evaluate_request_text: str = ""
    post_evaluate_response_text: str = ""
    evaluate_request_text: str = ""
    evaluate_response_text: str = ""
    post_score: int = 0
    score: int = 0


@dataclass
class SearchHits:
    location: enums.SearchLocation
    profile_about: str
    profile_url: str
    prompt_response_message: str
    score: int
    comment: str


def store_search_results(
    file_name_suffix: str, search_results: list[LeadSearchResult]
) -> None:
    assert search_results

    search_results.sort(
        key=lambda sr: -sr.score,
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)
    file_path = RESULTS_FILE_NAME.format(RESULTS_DIR, file_name_suffix)

    workbook = xlsxwriter.Workbook(file_path)
    sheet_name = "Results"
    worksheet = workbook.add_worksheet(sheet_name)

    header_cell_format = workbook.add_format(
        {"align": "center", "valign": "top", "text_wrap": True, "bold": True}
    )
    data_cell_format = workbook.add_format(
        {"align": "left", "valign": "top", "text_wrap": True}
    )
    centered_cell_format = workbook.add_format({"align": "center"})

    # Widen the first columns to make the text clearer.
    worksheet.set_column("A:A", 12)
    worksheet.set_column("B:B", 80)
    worksheet.set_column("C:C", 80)
    worksheet.set_column("D:D", 40)
    worksheet.set_column("E:E", 20)
    worksheet.set_column("F:F", 30)
    worksheet.set_column("G:G", 80)
    worksheet.set_column("H:H", 80)
    worksheet.set_column("I:I", 80)
    worksheet.set_column("J:J", 20)
    worksheet.set_column("K:K", 40)

    # Set headers in bold.
    worksheet.write("A1", "Score", header_cell_format)
    worksheet.write("B1", "Prompt response", header_cell_format)
    worksheet.write("C1", "Comment", header_cell_format)
    worksheet.write("D1", "Profile about", header_cell_format)
    worksheet.write("E1", "Username", header_cell_format)
    worksheet.write("F1", "Profile URL", header_cell_format)
    worksheet.write("G1", "Prompt request", header_cell_format)
    worksheet.write("H1", "Evaluate request", header_cell_format)
    worksheet.write("I1", "Evaluate response", header_cell_format)
    worksheet.write("J1", "Location", header_cell_format)
    worksheet.write("K1", "Prompt template", header_cell_format)

    row_index = 0
    for search_result in search_results:
        row_index += 1
        worksheet.write_row(
            row_index,
            0,
            [
                search_result.score,
                search_result.prompt_response_text,
                search_result.comment,
                search_result.profile_about,
                search_result.username,
                search_result.profile_url,
                search_result.prompt_request_text,
                search_result.evaluate_request_text,
                search_result.evaluate_response_text,
                enums.SearchLocation(search_result.location).label,
                search_result.prompt_template,
            ],
            data_cell_format,
        )

    # Update cell formats for some columns
    worksheet.set_column(0, 0, 12, header_cell_format)
    worksheet.set_column("F:F", 30, centered_cell_format)
    worksheet.set_column("J:J", 20, centered_cell_format)

    workbook.close()

    return file_path
