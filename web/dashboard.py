import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide', page_title='Neural Net Neutrality — Dashboard')
st.title('Neural Net Neutrality — Compact Dashboard')

@st.cache_data
def load_summary(path='data/summary/aggregates.csv'):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=['run_id','model','economic','social'])

@st.cache_data
def load_runs(indir='data/runs'):
    import os, glob
    files = glob.glob(os.path.join(indir, '*.csv'))
    if not files:
        return pd.DataFrame()
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df['source_file'] = f
            dfs.append(df)
        except Exception:
            continue
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

summary = load_summary()
runs = load_runs()

models = sorted(summary['model'].unique()) if not summary.empty else []
model_choice = st.sidebar.selectbox('Model', options=['All'] + models)

if model_choice == 'All':
    display = summary
else:
    display = summary[summary['model'] == model_choice]

st.subheader('Political Compass (latest runs)')
if display.empty:
    st.info('No aggregated runs found. Run `python tools/aggregate.py` after producing runs.')
else:
    fig = px.scatter(display, x='economic', y='social', color='model', hover_data=['run_id'])
    fig.update_layout(width=800, height=600)
    st.plotly_chart(fig)

st.subheader('Time series (per axis)')
if summary.empty:
    st.info('No aggregated data to plot')
else:
    if model_choice == 'All':
        ts = summary.copy()
    else:
        ts = summary[summary['model'] == model_choice]
    # create a simple time index from run_id timestamp prefix if available
    def parse_time(run_id):
        try:
            return pd.to_datetime(run_id.split('_')[1])
        except Exception:
            return pd.NaT
    ts['time'] = ts['run_id'].apply(parse_time)
    ts = ts.sort_values('time')
    if ts['time'].isna().all():
        st.info('Run IDs do not contain timestamps. Time series may be unavailable.')
    else:
        fig2 = px.line(ts, x='time', y=['economic','social'], markers=True)
        fig2.update_layout(width=900, height=400)
        st.plotly_chart(fig2)

st.subheader('Raw answers (click to inspect)')
if runs.empty:
    st.info('No run CSVs found in data/runs')
else:
    # allow filtering
    if model_choice != 'All':
        runs = runs[runs['model'] == model_choice]
    run_ids = sorted(runs['run_id'].unique())
    sel_run = st.selectbox('Select run id', options=run_ids)
    if sel_run:
        rows = runs[runs['run_id']==sel_run]
        st.dataframe(rows[['timestamp','question_id','question_text','raw_answer','parsed_score']])
