oai_reword_role_instructions = """
You're a helpful assistance designed to reword generic
messages with the recipient's user context.
"""

oai_evaluation_role_instructions = """
You're a helpful assistance designed to evaluate how accurately
a given text adheres to some criteria.
Please respond ONLY with an integer from 1 to 100.
"""

oai_instruction_1 = """
The next paragraph is a generic sales email that a salesperson sends to leads sourced
from Hacker News:

"""

oai_instruction_2 = """

The comment the recipient posted contained this, in the following paragraph:

"""

oai_instruction_3 = """

The recipient's username is
"""

oai_instruction_4 = """

And the recipient's profile about page contained the following paragraph:

"""

oai_instruction_5 = """

Now, with the above information, please reword the given pitch prompt template to include some of the 
recipient user's personal information and be relevant to the comment they posted. Do not change the 
salesperson's name or signature, if it exists. If there's no salesperson
name attached, please use some generic greeting rather than mentioning sales directly.

If you can't find the recipient's name, please keep the introduction generic, 
a "Hi there!" or "Hey", would suffice. Don't include a subject like in an email, assume you are
responding to a forum post. Please add proper paragraphs for readability. Try not to be too formal or too casual,
Again, ideally, use the recipient's name or username if you can find it.

Please try to keep the response within 300 characters, try not to add too much flair, keep it simple and concise,
and look to address the user's pain points with regards to what we are offering.

"""


post_evaluation_1 = """
The following paragraph is the initial post by the user on the Hacker News platform:

"""

post_evaluation_2 = """

And the next paragraph below is the criteria that you are to evaluate the above generated text:

"""

post_evaluation_3 = """

Now, please respond with an integer from 1 to 100 as to how well the initial post 
meets the criteria of the post evaluation template so that it can be scored.

Example scoring:
50 and below. Post is not relevant, and does not contain criteria
60. Post is potentially relevant
70. Post is relevant
80. Post is very relevance
90. Post is extremely relevant, and contains most if not all mentioned criteria

Answer in the following format, with the explanation within 250 characters: <score integer>. Explanation
"""

aoi_evaluation_1 = """
The following paragraph contains generated text used by a salesperson
to respond to a user on Hacker News looking for help:

"""

aoi_evaluation_2 = """

And the below paragraph is the criteria that you are to evaluate the above generated text.

"""

aoi_evaluation_3 = """

Please respond with an integer from 1 to 100 as to how well the generated
response meets the criteria of the evaluation template so that it can scored.

Example scoring:
50 and below. Response is not relevant, and does not contain criteria
60. Response is potentially relevant
70. Response is relevant
80. Response is very relevant
90. Response is extremely relevant, and contains most if not all mentioned criteria

Answer in the following format, with the explanation within 250 characters: <score integer>. Explanation
"""
