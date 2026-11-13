"""Faculty dashboard: run locally or behind an authenticated hosting gateway."""
import copy
import json
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
import streamlit as st
from backend.bank import load_bank,validate_bank
from backend.dashboard_config import setting

st.set_page_config(page_title='AE Prepware · Faculty',page_icon='✈',layout='centered')
st.title('AE Prepware')
st.caption('Faculty hangar · Coursework, question review and cohort standings')
st.info('Run this dashboard privately. The student Android app works offline. AI drafts are unscored until an instructor checks and approves them.')
if 'bank' not in st.session_state:st.session_state.bank=load_bank()
bank=st.session_state.bank
if 'bank_workspace_base' not in st.session_state: st.session_state.bank_workspace_base=copy.deepcopy(bank)
def store_update(updated):
    from backend.authoring import compatible_refresh
    base=st.session_state.bank_workspace_base
    updated['extends']=base['version']
    compatible_refresh(base,updated)
    st.session_state.bank=updated
    st.session_state.bank_refresh=updated
study,review,cohort=st.tabs(['Coursework','Question review','Cohort'])
with study:
    selected=st.selectbox('Subject',bank['subjects'],format_func=lambda s:s['name'])
    topics=sorted({q['topic'] for q in bank['questions'] if q['subject']==selected['id']})
    topic=st.selectbox('Focus topic',topics)
    st.subheader('A focused 25-minute session')
    st.markdown(f'1. **Recall · 5 min:** write the central definitions and assumptions for {topic}.\n2. **Work · 10 min:** solve two examples with units and a reasonableness check.\n3. **Practice · 5 min:** answer a short AE Prepware session.\n4. **Reflect · 5 min:** explain each error and schedule another attempt.')
    st.caption('This default coursework is a local template, with no AI service or payment required.')
    with st.expander('Optional AI draft assistant'):
        st.write('Uses a server-side Gemini API key. Review the provider’s terms and cost limits before enabling. No student records are sent. Add GEMINI_API_KEY to Streamlit App settings → Secrets. GEMINI_MODEL is optional; the default is gemini-3.5-flash-lite. Server environment variables also work.')
        api_key=setting('GEMINI_API_KEY')
        model=setting('GEMINI_MODEL','gemini-3.5-flash-lite')
        if not api_key:
            st.info('AI is not configured. Add GEMINI_API_KEY in Streamlit Secrets, then rerun the app. The local coursework plan remains available.')
        elif not model:
            st.info('GEMINI_MODEL is empty. Set an available Gemini model in Streamlit Secrets, or remove the entry to use the default.')
        else:
            st.caption('AI configuration loaded. Generate a draft to check provider access.')
        if st.button('Draft a coursework plan with AI',disabled=not bool(api_key and model)):
            try:
                prompt=f'Draft a 25-minute study plan for Philippine undergraduate aeronautical engineering students. Subject: {selected["name"]}. Topic: {topic}. Include objectives, prerequisite check, 2 original practice prompts, and a verification checklist. Do not claim PRC endorsement or guaranteed passing. Label all content DRAFT FOR INSTRUCTOR REVIEW. Do not use student personal data.'
                with httpx.Client(timeout=30,follow_redirects=False) as client:
                    response=client.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',headers={'x-goog-api-key':api_key},json={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'maxOutputTokens':1400}})
                    response.raise_for_status()
                    text='\n'.join(p.get('text','') for p in response.json()['candidates'][0]['content']['parts'])
                st.session_state.ai_plan=text
            except (httpx.HTTPError,KeyError,IndexError,ValueError,ImportError):st.error('The AI draft could not be generated. Check server configuration or use the local coursework plan. No draft was published.')
        if st.session_state.get('ai_plan'):
            st.warning('AI draft · instructor review required')
            st.markdown(st.session_state.ai_plan)
            st.download_button('Download draft plan',st.session_state.ai_plan,'AE-coursework-DRAFT.md')
with review:
    from backend.dashboard_auth import admin_gate
    from backend.authoring import revise_question, merge_instructor_upload
    st.caption(f'{len(bank["questions"])} question records · {bank["version"]}')
    authorized = admin_gate()
    if authorized:
        upload = st.file_uploader('Open a saved bank workspace', type='json')
        if upload and st.button('Load bank'):
            try:
                if upload.size > 8_000_000:
                    raise ValueError('File exceeds 8 MB')
                candidate = validate_bank(json.loads(upload.getvalue()), imported=True, trusted=load_bank())
                st.session_state.bank = candidate
                st.session_state.bank_workspace_base = copy.deepcopy(candidate)
                st.session_state.pop('bank_refresh', None)
                st.rerun()
            except (ValueError, KeyError, TypeError) as exc:
                st.error(str(exc))
        active = [q for q in bank['questions'] if q.get('active', True)]
        q = st.selectbox('Question', active, format_func=lambda x: f'{x.get("origin", "AI")} · {x["id"]} · {x["topic"]}')
        st.caption('Source: ' + q.get('origin', 'AI') + ' · ' + q['review'])
        st.write(q['prompt'])
        st.write('\n'.join(f'{"ABCD"[i]}. {c}' for i, c in enumerate(q['choices'])))
        st.success('Current key: ' + q['choices'][q['answer']])
        st.write(q['explanation'])
        src = bank['sources'][q['source']]
        st.link_button(src['title'], src['url'])
        st.caption(src['locator'])
        if q.get('upload'):
            st.caption('Upload: ' + q['upload']['file'] + ' · ' + q['upload']['locator'])
        with st.form('edit_' + q['id']):
            st.subheader('Correct this question')
            prompt = st.text_area('Question text', q['prompt'])
            choices = [st.text_input('Choice ' + letter, q['choices'][i]) for i, letter in enumerate('ABCD'[:len(q['choices'])])]
            answer = st.selectbox('Correct answer', list(range(len(q['choices']))), index=q['answer'], format_func=lambda i: 'ABCD'[i])
            explanation = st.text_area('Explanation', q['explanation'])
            reviewer = st.text_input('Instructor reviewer name')
            version = st.text_input('New bank version', bank['version'] + '-revision1')
            checked = st.checkbox('I independently checked this question, answer, explanation and source.')
            commit_edit = st.form_submit_button('Save reviewed revision')
        if commit_edit:
            try:
                if not checked:
                    raise ValueError('Independent instructor review is required')
                updated = revise_question(bank, q['id'], prompt=prompt, choices=choices,
                    answer=answer, explanation=explanation, reviewer=reviewer, version=version)
                store_update(updated)
                st.rerun()
            except (ValueError, KeyError, TypeError) as exc:
                st.error(str(exc))
        st.caption('A correction retires the old ID and creates a reviewed revision. Old scores keep the old key. Export after every edit; dashboard memory may reset on reboot.')
        with st.expander('Add instructor questions · IN'):
            incoming = st.file_uploader('Reviewed instructor JSON', type='json', key='in_upload')
            incoming_version = st.text_input('Merged bank version', bank['version'] + '-IN1')
            st.caption('Use the instructor_uploads folder schema. Each question needs source/page, upload filename, redistribution rights, reviewer and approval. PDF extraction never implies approval.')
            if st.button('Add reviewed IN questions', disabled=incoming is None):
                try:
                    if incoming.size > 8_000_000:
                        raise ValueError('File exceeds 8 MB')
                    updated = merge_instructor_upload(bank, json.loads(incoming.getvalue()), incoming_version)
                    store_update(updated)
                    st.rerun()
                except (ValueError, KeyError, TypeError) as exc:
                    st.error(str(exc))
        st.download_button('Save bank workspace / Android refresh', json.dumps(bank, ensure_ascii=False, indent=2), 'AE-bank-refresh.json')
        st.caption('Import each exported refresh on the matching current bank in Android Settings. Progress, active sessions and queued results are retained for append-only updates. Restart the API with the same export after backing up its database.')
with cohort:
    url=st.text_input('HTTPS cohort API root URL',value=setting('AE_API_URL'))
    if st.button('Load standings'):
        try:
            from urllib.parse import urlparse
            parsed=urlparse(url)
            if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:raise ValueError()
            data=httpx.get(url.rstrip('/')+'/accounts/leaderboard',timeout=10,follow_redirects=False);data.raise_for_status()
            st.dataframe(data.json()['entries'],hide_index=True,use_container_width=True)
        except (httpx.HTTPError,ValueError,KeyError):st.error('Could not load standings. Check the HTTPS API URL and service.')
    st.caption('Account standings use first-correct daily question points and masked account suffixes. Names are self-chosen; these are practice results, not proctored examination rankings.')
