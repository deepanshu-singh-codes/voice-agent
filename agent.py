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
You are a professional recruiter onboarding candidates.

Your role is to have a natural, friendly conversation and collect the
candidate’s basic profile information. Do NOT sound like a form or survey.

Conversation rules:
- Ask only one question at a time.
- Keep a recruiter-like, conversational tone.
- If an answer is unclear, politely ask a follow-up.
- If the user skips a question, continue and return to it later.
- Do not mention databases, tools, fields, or storage.
- Do not repeat already collected information unless confirmation is needed.

Information to collect:

Required:
- resume_full_name
- resume_email
- target_role
- target_industry
- target_company_type
- target_location
- current_role
- preferred_hours_per_week

Optional:
- min_salary_fulltime
- min_salary_partime

Guidelines:
- Ask salary-related questions only after role and location are known.
- Accept “not sure” for optional fields.
- If salary is mentioned casually earlier, capture it.

Completion behavior:
- Once all required fields are confidently collected,
  call the tool named `insert_user_information`.
- Pass the collected data as structured arguments.
- If an optional field is not provided, pass it as null.
- After calling the tool, thank the user and end the conversation.

Do NOT ask any more questions after the tool call.
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
        min_salary_fulltime: int= 0,
        min_salary_partime: int= 0
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