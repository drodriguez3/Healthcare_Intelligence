import streamlit as st
import pandas as pd
from pathlib import Path
import json
st.set_page_config(page_title='Healthcare Enterprise Intelligence | IronGate',page_icon='◆',layout='wide')
root=Path(__file__).parent
claims=pd.read_csv(root/'data/denials.csv')
policies=json.loads((root/'data/policies.json').read_text())
ops=pd.read_csv(root/'data/operations.csv')
cost=pd.read_csv(root/'data/costs.csv')
def money(x): return f'${x:,.0f}'
st.markdown('''<style>.block-container{max-width:1150px;padding-top:2rem} div[data-testid="stMetric"]{border:1px solid #dce3eb;padding:14px;border-radius:12px}</style>''',unsafe_allow_html=True)
st.title('Healthcare Enterprise Intelligence')
st.subheader('AI-powered financial and operational decision support')
st.markdown('**Prepared for Prisma Health | Presented by IronGate Data Solutions LLC**')
st.info('Independent concept demonstration. All records, facilities and policies are fictional. AI responses use local rule-based analytics and lexical retrieval, not live Snowflake Cortex services. No Prisma affiliation or endorsement.')
modules=['Recover revenue','Improve operations','Reduce costs','Estimate value','Technology & pilot']
mode=st.radio('Where would you like to create value?',modules,horizontal=True)
from engine import analyze, search
if mode in modules[:3]:
    st.header({'Recover revenue':'Revenue Recovery Intelligence','Improve operations':'Hospital Operations Intelligence','Reduce costs':'Healthcare Cost Intelligence'}[mode])
    interaction=st.radio('Choose an investigation', ['Investigate & Recommend','Explore Your Data','Explore Your Knowledge'],horizontal=True,key=mode)
    examples={'Recover revenue':['Where should we prioritize denied revenue recovery?','Which aging denials over 30 days need review?','What authorization denial guidance applies?'],'Improve operations':['Where is capacity pressure greatest?','Which facilities have staffing gaps?','What discharge coordination guidance applies?'],'Reduce costs':['What is driving cost increases?','Which services have the greatest unit cost increase?','What utilization review guidance applies?']}[mode]
    example=st.selectbox('Suggested question',examples,key=mode+interaction)
    q=st.text_input('Or enter your own question',placeholder=example,key=mode+interaction+'q') or example
    if st.button('Run investigation',type='primary'):
        try:
            context=q
            if interaction!='Explore Your Knowledge':
                table,summary,context=analyze(mode,q)
                st.subheader('Executive findings');st.write(summary)
                with st.expander('Supporting structured data'): st.dataframe(table,hide_index=True)
            if interaction!='Explore Your Data':
                docs=search(mode,q+' '+context)
                st.subheader('Relevant fictional guidance')
                if not docs: st.warning('No matching guidance found. Try more specific terms.')
                for d in docs: st.write(f"**[{d['id']}] {d['title']}** — {d['text']}")
                if interaction=='Investigate & Recommend':
                    st.subheader('Recommended next steps')
                    st.write('Validate the analytical finding with the responsible business owner before acting.')
                    for d in docs: st.write(f"- {d['text']} [{d['id']}]")
                    st.write('Measure review time and verified outcomes against an agreed baseline.')
            st.caption('Local simulation: rule-based analytics, TF-IDF document retrieval and template synthesis. Not an LLM or live Cortex agent.')
        except ValueError as e: st.warning(str(e))
elif mode==modules[3]:
    st.header('Estimate potential annual value');st.caption('Adjust illustrative assumptions. These are not Prisma figures or forecasts.')
    denied=st.number_input('Annual denied revenue ($)',min_value=0,value=50000000,step=1000000);rate=st.slider('Incremental recovery (% of denied revenue)',0.0,10.0,2.0,0.1);staff=st.number_input('Analysts',min_value=0,value=20);hours=st.number_input('Hours saved per analyst per week',min_value=0.0,max_value=40.0,value=5.0);wage=st.number_input('Loaded hourly labor cost ($)',min_value=0,value=50);pilot=st.number_input('Estimated annual solution cost ($)',min_value=0,value=100000)
    recovery=denied*rate/100;capacity=staff*hours*52*wage
    a,b,c=st.columns(3);a.metric('Potential incremental recovery',money(recovery));b.metric('Labor capacity value',money(capacity));c.metric('Gross economic value',money(recovery+capacity));st.write(f'Illustrative net economic value after solution cost: **{money(recovery+capacity-pilot)}**.');st.caption('Labor capacity is not necessarily cash savings. Validate recoverability, attribution, ongoing costs and overlap before calculating realized ROI.')
else:
    st.header('Designed for Snowflake Cortex AI');st.write('Proposed production architecture, not implemented in this demo.')
    st.code('Approved enterprise data → Governed semantic views → Cortex Analyst\nApproved policies → Cortex Search\nAnalyst + Search → Cortex Agents → Human-reviewed briefing',language=None)
    st.write('Pilot: select one workflow, confirm Snowflake access and security, establish baseline, implement live Cortex integration, evaluate grounded accuracy and business outcomes. No automated clinical or billing decisions.')
st.divider();st.markdown('### Explore a focused AI pilot');st.write('Validate one high-value workflow using approved data and measurable outcomes.');st.markdown('[Contact IronGate](mailto:info@irongatedatasolutions.com) · [Company website](https://irongatedatasolutions.com)')
