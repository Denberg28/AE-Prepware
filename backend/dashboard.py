"""Faculty dashboard: run locally or behind an authenticated hosting gateway."""
import copy
import json
import os
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
import streamlit as st
from backend.bank import load_bank,validate_bank

st.set_page_config(page_title='AE Prepware · Faculty',page_icon='✈',layout='centered')
st.title('AE Prepware')
st.caption('Faculty hangar · Coursework, question review and cohort standings')
st.info('Run this dashboard privately. The student Android app works offline. AI drafts are unscored until an instructor checks and approves them.')
if 'bank' not in st.session_state:st.session_state.bank=load_bank()
bank=st.session_state.bank
study,review,cohort=st.tabs(['Coursework','Question review','Cohort'])
with study:
    selected=st.selectbox('Subject',bank['subjects'],format_func=lambda s:s['name'])
    topics=sorted({q['topic'] for q in bank['questions'] if q['subject']==selected['id']})
    topic=st.selectbox('Focus topic',topics)
    st.subheader('A focused 25-minute session')
    st.markdown(f'1. **Recall · 5 min:** write the central definitions and assumptions for {topic}.\n2. **Work · 10 min:** solve two examples with units and a reasonableness check.\n3. **Practice · 5 min:** answer a short AE Prepware session.\n4. **Reflect · 5 min:** explain each error and schedule another attempt.')
    st.caption('This default coursework is a local template, with no AI service or payment required.')
    with st.expander('Optional AI draft assistant'):
        st.write('Uses a server-side Gemini API key. Review the provider’s terms and cost limits before enabling. No student records are sent. Set both GEMINI_API_KEY and GEMINI_MODEL to an available model in your account.')
        if st.button('Draft a coursework plan with AI',disabled=not bool(os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_MODEL'))):
            try:
                prompt=f'Draft a 25-minute study plan for Philippine undergraduate aeronautical engineering students. Subject: {selected["name"]}. Topic: {topic}. Include objectives, prerequisite check, 2 original practice prompts, and a verification checklist. Do not claim PRC endorsement or guaranteed passing. Label all content DRAFT FOR INSTRUCTOR REVIEW. Do not use student personal data.'
                model=os.environ['GEMINI_MODEL']
                with httpx.Client(timeout=30,follow_redirects=False) as client:
                    response=client.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',headers={'x-goog-api-key':os.environ['GEMINI_API_KEY']},json={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'maxOutputTokens':1400,'temperature':0.4}})
                    response.raise_for_status()
                    text='\n'.join(p.get('text','') for p in response.json()['candidates'][0]['content']['parts'])
                st.session_state.ai_plan=text
            except (httpx.HTTPError,KeyError,IndexError,ValueError):st.error('The AI draft could not be generated. Check server configuration or use the local coursework plan. No draft was published.')
        if st.session_state.get('ai_plan'):
            st.warning('AI draft · instructor review required')
            st.markdown(st.session_state.ai_plan)
            st.download_button('Download draft plan',st.session_state.ai_plan,'AE-coursework-DRAFT.md')
with review:
    st.caption(f'{len(bank["questions"])} original foundation questions · {bank["version"]}')
    upload=st.file_uploader('Open a bank JSON for review',type='json')
    if upload and st.button('Load bank'):
        try:
            if upload.size>2_000_000:raise ValueError('File exceeds 2 MB')
            candidate=validate_bank(json.loads(upload.getvalue()))
            st.session_state.bank=candidate;st.session_state.approvals={};st.rerun()
        except (ValueError,KeyError,TypeError) as exc:st.error(str(exc))
    q=st.selectbox('Question',bank['questions'],format_func=lambda x:f'{x["id"]} · {x["topic"]}')
    st.write(q['prompt'])
    st.write('\n'.join(f'{"ABCD"[i]}. {c}' for i,c in enumerate(q['choices'])))
    st.success('Current key: '+q['choices'][q['answer']])
    st.write(q['explanation'])
    src=bank['sources'][q['source']]
    st.link_button(src['title'],src['url'])
    st.caption(src['locator'])
    st.caption('Use the repository generator or JSON editor to correct wording, choices and explanations before approving. Any edit requires a new bank version and re-review.')
    reviewer=st.text_input('Instructor reviewer name')
    checked=st.checkbox('I independently checked the wording, unique answer, calculation, units, explanation and cited source.',key='checked_'+q['id'])
    if st.button('Approve this question',disabled=not (reviewer.strip() and checked)):
        st.session_state.setdefault('approvals',{})[q['id']]={'review':'approved','reviewer':reviewer.strip(),'reviewedAt':date.today().isoformat()}
        st.success('Approval recorded in this dashboard session. Export to preserve it.')
    approvals=st.session_state.get('approvals',{})
    approved=sum(x['review']=='approved' or x['id'] in approvals for x in bank['questions'])
    st.write(f'{approved}/{len(bank["questions"])} instructor-approved')
    export=copy.deepcopy(bank)
    for item in export['questions']:item.update(approvals.get(item['id'],{}))
    st.download_button('Save review work in progress',json.dumps(export,ensure_ascii=False,indent=2),'AE-bank-review-work.json')
    version=st.text_input('New approved bank version',value=bank['version']+'-faculty1')
    if approved==len(bank['questions']) and version.strip()!=bank['version']:
        export['version']=version.strip();export['notice']='Original practice questions independently approved by the named instructors; not official PRC items or a pass guarantee.'
        validate_bank(export,imported=True)
        st.download_button('Export approved Android question bank',json.dumps(export,ensure_ascii=False,indent=2),'AE-approved-bank.json')
    else:st.caption('All questions need instructor approval and a new version before the Android import can accept the bank.')
with cohort:
    url=st.text_input('HTTPS cohort API root URL',value=os.getenv('AE_API_URL',''))
    if st.button('Load standings'):
        try:
            from urllib.parse import urlparse
            parsed=urlparse(url)
            if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:raise ValueError()
            data=httpx.get(url.rstrip('/')+'/leaderboard',timeout=10,follow_redirects=False);data.raise_for_status()
            st.dataframe(data.json()['entries'],hide_index=True,use_container_width=True)
        except (httpx.HTTPError,ValueError,KeyError):st.error('Could not load standings. Check the HTTPS API URL and service.')
    st.caption('Standings use first-correct daily question points. Participant names are self-chosen; these are practice results, not proctored examination rankings.')
