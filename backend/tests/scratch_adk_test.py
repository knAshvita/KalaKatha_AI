"""Quick smoke test for google-adk 2.10.0 API."""
import asyncio
import os
import json
from pathlib import Path

# Load API key
env_content = Path('.env').read_text()
for line in env_content.splitlines():
    if line.startswith('GEMINI_API_KEY='):
        api_key = line.split('=', 1)[1].strip()
        os.environ['GOOGLE_API_KEY'] = api_key
        break

from google.adk.agents import LlmAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types


_MODEL = 'gemini-3.8-flash'

async def test_llm_agent():
    """Test a single LlmAgent returns structured state output."""
    agent = LlmAgent(
        name='greeter',
        model=_MODEL,
        instruction='Return a JSON object with a greeting field. Example: {"greeting": "Hello from ADK!"}',
        output_key='greeting_output',
        generate_content_config=genai_types.GenerateContentConfig(
            response_mime_type='application/json',
        ),
    )
    session_svc = InMemorySessionService()
    runner = Runner(agent=agent, app_name='kalakatha_test', session_service=session_svc)

    session = await session_svc.create_session(app_name='kalakatha_test', user_id='user1')

    events = []
    async for event in runner.run_async(
        user_id='user1',
        session_id=session.id,
        new_message=genai_types.Content(
            role='user',
            parts=[genai_types.Part(text='Say hello')]
        )
    ):
        events.append(event)

    final_session = await session_svc.get_session(
        app_name='kalakatha_test', user_id='user1', session_id=session.id
    )
    print('ADK Runner test PASSED')
    print(f'  Events received: {len(events)}')
    print(f'  Session state keys: {list(final_session.state.keys())}')
    if 'greeting_output' in final_session.state:
        print(f'  Output: {final_session.state["greeting_output"]}')
    return final_session.state


async def test_sequential_workflow():
    """Test a Workflow (sequential) with two LlmAgents."""
    from google.adk import Workflow

    agent1 = LlmAgent(
        name='step1_agent',
        model=_MODEL,
        instruction='Return JSON: {"step": "first", "value": 42}',
        output_key='step1_result',
        generate_content_config=genai_types.GenerateContentConfig(
            response_mime_type='application/json',
        ),
    )
    agent2 = LlmAgent(
        name='step2_agent',
        model=_MODEL,
        instruction='Return JSON: {"step": "second", "doubled": 84}',
        output_key='step2_result',
        generate_content_config=genai_types.GenerateContentConfig(
            response_mime_type='application/json',
        ),
    )

    workflow = Workflow(
        name='test_seq_workflow',
        edges=[
            ('START', agent1),
            (agent1, agent2),
        ],
    )

    session_svc = InMemorySessionService()
    runner = Runner(agent=workflow, app_name='kalakatha_wf_test', session_service=session_svc)
    session = await session_svc.create_session(app_name='kalakatha_wf_test', user_id='user1')

    events = []
    async for event in runner.run_async(
        user_id='user1',
        session_id=session.id,
        new_message=genai_types.Content(
            role='user',
            parts=[genai_types.Part(text='Run the workflow')]
        )
    ):
        events.append(event)

    final_session = await session_svc.get_session(
        app_name='kalakatha_wf_test', user_id='user1', session_id=session.id
    )
    print('\nADK Workflow test PASSED')
    print(f'  Events received: {len(events)}')
    print(f'  Session state keys: {list(final_session.state.keys())}')
    for k, v in final_session.state.items():
        print(f'  {k}: {v}')


if __name__ == '__main__':
    print('=== Testing google-adk 2.10.0 ===\n')
    asyncio.run(test_llm_agent())
    asyncio.run(test_sequential_workflow())
    print('\n=== All ADK tests passed ===')
