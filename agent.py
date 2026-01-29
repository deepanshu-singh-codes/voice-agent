from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io, function_tool
from livekit.plugins import (
    openai,
    noise_cancellation,
)
from database import supabase_client
# print(supabase_client.table("user").select("*").execute())
prompt = """
You are a professional recruiter onboarding candidates through a natural,
friendly conversation.

Your objective is to understand the candidate’s background, preferences,
and priorities without making the interaction feel like a form or interview.

GENERAL BEHAVIOR RULES
- Sound like an experienced human recruiter.
- Ask one question at a time.
- Keep responses short, warm, and conversational.
- Do not read field names or lists to the user.
- Do not mention databases, tools, schemas, or storage.
- If an answer is vague, politely ask a clarifying follow-up.
- If the user skips a question, move on and return to it later.
- Paraphrase occasionally to confirm understanding.
- Never rush the user.

--------------------------------------------------
INFORMATION TO COLLECT
--------------------------------------------------

BASIC PROFILE (Required)
- resume_full_name
- resume_email
- current_role
- target_role
- target_industry
- target_company_type
- target_location
- preferred_hours_per_week

AVAILABILITY & WORK AUTHORIZATION
- availability_to_start
- visa_sponsorship_required
- working_language_pref

COMPENSATION (Optional)
- min_salary_fulltime
- min_salary_partime

Ask compensation questions only after role, location, and availability
are already discussed. Accept “not sure” and store null if unknown.

CAREER PRIORITIES
Ask these conversationally, not as a checklist:
- work_life_balance_priority
- career_growth_priority
- tech_stack_priority
- diversity_inclusion_priority
- purpose_culture_priority
- location_flexibility_priority

Use values such as:
"Not important", "Slightly important", "Moderately important",
"Important", "Very important"

SOFT SKILLS (Infer or lightly probe)
- communication_style
- teamwork_leadership
- adaptability_creativity
- personality_type (optional, MBTI-style if natural)

RESUME DETAILS
Collect naturally if the user shares them:
- resume_education
- resume_work_experience
- resume_skills
- resume_certifications

Do not force resume details if the user prefers to skip them.

--------------------------------------------------
COMPLETION & TOOL CALL
--------------------------------------------------

Once all REQUIRED fields are confidently collected:

- Call the tool named `insert_user_information`
- Pass all collected values as structured arguments
- Any missing optional fields must be passed as null
- Call the tool only ONCE

After the tool call:
- Thank the user
- Confirm their profile has been saved
- End the conversation politely

Do not ask further questions after the tool call.
"""


load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=prompt)
        
    @function_tool()
    async def insert_user_information(
        self, 
        resume_full_name: str, 
        resume_email: str, 
        target_role: str,
        target_industry: str,
        target_company_type: str,
        target_location: str,
        current_role: str,
        preferred_hours_per_week: int,
        availability_to_start: str,
        visa_sponsorship_required: str,
        working_language_pref: str,
        work_life_balance_priority: str,
        career_growth_priority: str,
        tech_stack_priority: str,
        diversity_inclusion_priority: str,
        purpose_culture_priority: str,
        location_flexibility_priority: str,
        communication_style: str,
        teamwork_leadership: str,
        adaptability_creativity: str,
        personality_type: str,
        resume_education: dict,
        resume_work_experience: dict,
        resume_skills: list,
        resume_certifications: dict,
        min_salary_fulltime: int= 0,
        min_salary_partime: int= 0,
    ):
        """The function is to insert data in the table. All the fields in this are mandatory.
        Description for the following are below:
        resume_full_name: full name for the applicant.
        resume_email: email of the applicant
        target_role: The role user targetting.
        target_industry: The industry looked by the applicant.
        target_location: The location for which user is targetting for the user.
        target_company_type: The company types for which user is targetting for the user.
        current_role: The curreny designation or role of the user.
        min_salary_fulltime: The minimum salary for the full_time role which appkicant agrees too.
        min_salary_partime: The minimum salary for the full_time role which appkicant agrees too.
        preferred_hours_per_week: The preffered weekly hours what user wants to serve.
        availability_to_start: How soon the applicant can start (e.g., immediately, 2_weeks, 1_month).
        visa_sponsorship_required: Whether the applicant requires visa sponsorship ("yes" or "no").
        working_language_pref: Preferred working language of the applicant.
        work_life_balance_priority: Importance of work-life balance to the applicant.
        career_growth_priority: Importance of career growth and learning opportunities.
        tech_stack_priority: Importance of the technology stack in job selection.
        diversity_inclusion_priority: Importance of diversity and inclusion in the workplace.
        purpose_culture_priority: Importance of company mission, values, and culture.
        location_flexibility_priority: Importance of remote or hybrid work flexibility.
        communication_style: Description of the applicant’s communication style inferred from conversation.
        teamwork_leadership: Description of how the applicant collaborates or leads within a team.
        adaptability_creativity: Assessment of the applicant’s adaptability and creativity.
        personality_type: Optional personality classification (e.g., MBTI-style).
        resume_education: Structured education history of the applicant.
        resume_work_experience: Structured work experience history of the applicant.
        resume_skills: List of skills identified from the applicant’s resume or conversation.
        resume_certifications: Structured list of professional certifications held by the applicant.
        """
        response = (
    supabase_client.table("user")
    .insert({"resume_full_name": resume_full_name, "resume_email": resume_email, "target_role": target_role,
             "target_industry": target_industry, "target_company_type": target_company_type, "target_location": target_location,
             "current_role": current_role, "min_salary_fulltime": min_salary_fulltime, "min_salary_partime": min_salary_partime, 
             "preferred_hours_per_week": preferred_hours_per_week})
    .execute()
)

server = AgentServer()



@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral"
        )
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(
        instructions=prompt
        ,allow_interruptions=True
    )


if __name__ == "__main__":
    agents.cli.run_app(server)