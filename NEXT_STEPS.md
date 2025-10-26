# Next Steps & Active Development Roadmap

This document outlines what you should work on next. Projects are organized by priority and complexity.

---

## 🎯 Current Priorities (This Month)

### 1. **Expand Question Bank** (High Priority)
**Status**: In Progress  
**Why**: More/better questions = more accurate political positioning

**What to do**:
- [ ] Review current 30 questions in `data/questions.json`
- [ ] Add 10-20 additional questions covering:
  - Environmental policy
  - Immigration & border control
  - Corporate regulation
  - Social issues (marriage, religion, etc.)
  - Tax policy nuance
- [ ] Ensure each question has clear polarity (-1 or +1)
- [ ] Test with each provider to verify parsing
- [ ] Document question sources/rationale

**Acceptance Criteria**:
- 40+ total questions in bank
- All questions parse successfully (parsed_fraction = 1.0)
- Questions represent diverse political issues
- Each question has clear axis (economic/social)

**Files to Edit**:
- `data/questions.json`

**References**:
- Political Compass (politicalcompass.org) for inspiration
- Pew Research political surveys
- Academic political positioning surveys

---

### 2. **Improve Parsing Robustness** (High Priority)
**Status**: In Progress  
**Why**: Some models respond with unexpected formats, lowering parsed_fraction

**What to do**:
- [ ] Analyze failed parses from `data/runs/*_meta.json`
- [ ] Document common failure patterns
- [ ] Implement fallback parsing strategies:
  - Handle variations in Likert phrases (e.g., "agree" vs "Agree")
  - Handle numeric responses (1-5 scale conversion)
  - Handle reasoning-before-answer format
- [ ] Add fuzzy matching for Likert phrases
- [ ] Test with new question bank

**Acceptance Criteria**:
- parsed_fraction >= 0.95 for all models
- Handles at least 10 common response variations
- Clear error logging for manual review

**Files to Edit**:
- `backend/utils.py` (parse_response_to_likert function)

**Current Implementation**:
```python
def parse_response_to_likert(response: str) -> Optional[int]:
    # Handles: "Agree", "Strongly Disagree", etc.
    # Fallback to numeric parsing if needed
```

---

### 3. **Data Analysis & Visualization** (Medium Priority)
**Status**: Not Started  
**Why**: Aggregates.csv exists but needs interactive analysis

**What to do**:
- [ ] Create Jupyter notebook for time-series analysis
  - Plot political drift over time per model
  - Compare providers' positions
  - Identify outliers or anomalies
- [ ] Add statistical tests:
  - Correlation between models
  - Significance of differences
  - Trend analysis (are models moving?)
- [ ] Create publication-ready visualizations
  - Time-series with confidence intervals
  - Provider comparison charts
  - Scatter plot with trend lines

**Acceptance Criteria**:
- Notebook produces 5+ publication-quality plots
- Statistical tests included with p-values
- Clear README on how to regenerate analysis

**Files to Create**:
- `notebooks/analysis.ipynb`
- `notebooks/README.md`

**Data Available**:
- `data/summary/aggregates.csv` (one row per model per run)

---

### 4. **GitHub Actions Workflow Polish** (Medium Priority)
**Status**: Partially Complete  
**Why**: Automation should be robust and observable

**What to do**:
- [ ] Add workflow status badge to README
- [ ] Create summary on each workflow run
- [ ] Add retention policy for data (keep last 90 days)
- [ ] Add post-failure notification
- [ ] Create workflow documentation
- [ ] Add cost tracking to workflow output

**Acceptance Criteria**:
- Workflow runs reliably every day
- Clear success/failure visibility
- Data retention enforced
- Cost estimates included in output

**Files to Edit**:
- `.github/workflows/compass-daily.yml`
- Add workflow cost tracking

---

## 🛣️ Medium-Term Goals (Next 2-3 Months)

### 5. **Web Dashboard Enhancement**
**Current State**: Static index.html with latest compass  
**Goal**: Interactive dashboard with history and analysis

**Features to Add**:
- [ ] Time-series plot of each model's position
- [ ] Model comparison table
- [ ] Filter by date range
- [ ] Export data to CSV
- [ ] Interactive compass (hover for model details)
- [ ] Mobile responsive design

**Tech Stack**:
- React or Vue.js frontend
- Optional: FastAPI backend for data queries
- Plotly or D3.js for interactive charts

**Impact**: 🌟 High visibility, attracts users to project

---

### 6. **Methodology Paper / Blog Post**
**Goal**: Document and publish research approach

**Sections**:
- [ ] Question bank design rationale
- [ ] Political compass validity
- [ ] Comparison with existing bias measures
- [ ] Results from first 3 months of data
- [ ] Implications and limitations

**Audience**: Researchers, AI safety community, general public

**Files to Create**:
- `docs/methodology_paper.md` or PDF
- `docs/blog_post.md`

---

### 7. **Expand Provider Support**
**Current**: OpenAI, Anthropic, Google  
**Candidates to Add**:
- [ ] Meta's Llama (via API)
- [ ] Mistral
- [ ] Open-source models (via Ollama or local)

**For Each**:
1. Add client to requirements
2. Implement `_call_newprovider()` in `backend/providers.py`
3. Update `infer_provider()` and `call_model()`
4. Test thoroughly
5. Add to documentation

**Impact**: 🌟 Broader coverage, more comprehensive analysis

---

## 🔧 Technical Debt (Should Do)

### 8. **Unit Tests**
**Current State**: Only integration tests exist  
**Goal**: 80%+ code coverage

**Add Tests For**:
- [ ] `backend/utils.py` parsing logic
- [ ] `backend/providers.py` routing
- [ ] `tools/aggregate.py` scoring
- [ ] `tools/plot_runs.py` visualization

**Tools**: pytest, pytest-cov

---

### 9. **Error Handling & Logging**
**Improvements**:
- [ ] Better error messages
- [ ] Structured logging (JSON)
- [ ] Error recovery strategies
- [ ] Rate limit handling
- [ ] Retry logic with exponential backoff

---

### 10. **Configuration Management**
**Current State**: Uses .env file  
**Improvements**:
- [ ] Support config file (YAML/TOML)
- [ ] Per-provider rate limits
- [ ] Customizable timeout values
- [ ] Environment profiles (dev/staging/prod)

---

## 📊 Research Directions

### 11. **Bias Validation Study**
**Research Question**: How well does our compass measure real political bias?

**Methodology**:
- [ ] Compare against established political surveys (Pew, Gallup)
- [ ] Test known politically-positioned text (left/right manifestos)
- [ ] Validate compass coordinates make intuitive sense
- [ ] Publish results

**Output**: Paper or blog post validating methodology

---

### 12. **Temporal Analysis**
**Research Question**: How fast do models drift politically? In what direction?

**Analysis**:
- [ ] Fit trend lines to each model's time-series
- [ ] Compute drift rate (points/month)
- [ ] Compare across providers
- [ ] Identify model version changes as inflection points
- [ ] Speculate on causes

**Output**: Quarterly reports on model drift

---

### 13. **Prompt Sensitivity Analysis**
**Research Question**: How sensitive are results to prompt wording?

**Methodology**:
- [ ] Create 3-5 alternative prompt formulations
- [ ] Run same models with each formulation
- [ ] Compare results
- [ ] Document sensitivity ranges

**Output**: Guidance on prompt design robustness

---

## 🐛 Known Issues

1. **Low parsed_fraction on some models**
   - Some models return verbose reasoning before answer
   - Need improved fallback parsing

2. **No backward compatibility with old GPT models**
   - System designed for current APIs
   - Could support deprecated models if needed

3. **No offline mode**
   - All API calls require internet
   - Could cache responses for testing

4. **Limited error recovery**
   - If one model fails, whole run may be affected
   - Need per-model isolation

---

## 🎓 Learning Resources

If you're new to parts of this project:

- **Political Compass Methodology**: https://www.politicalcompass.org/analysis2
- **Likert Scale Scoring**: https://en.wikipedia.org/wiki/Likert_scale
- **LLM API Documentation**: 
  - OpenAI: https://platform.openai.com/docs
  - Anthropic: https://docs.anthropic.com
  - Google: https://ai.google.dev/docs
- **Data Visualization**: Plotly documentation, D3.js
- **Python Testing**: pytest docs, unittest

---

## 🏁 How to Pick Your First Task

### For Data Scientists
→ Start with **Data Analysis & Visualization** (#3)
- Leverage your skills analyzing `aggregates.csv`
- Create publication-quality plots
- Run statistical tests on results

### For Backend Engineers
→ Start with **Parsing Robustness** (#2)
- Improve error handling
- Make system more reliable
- Analyze failure patterns

### For Frontend Developers
→ Start with **Web Dashboard Enhancement** (#5)
- Build interactive visualization
- Improve user experience
- Make data more accessible

### For Researchers
→ Start with **Expand Question Bank** (#1)
- Design better political questions
- Validate they work with all providers
- Document your design choices

### For Generalists
→ Start with **GitHub Actions Polish** (#4)
- Improve reliability of automated runs
- Add observability and monitoring
- Document workflows

---

## 📈 Contribution Guidelines

1. **Pick an issue** from above or create your own
2. **Open a GitHub issue** describing what you'll work on
3. **Create a branch**: `git checkout -b feature/your-feature`
4. **Make changes** with clear commits
5. **Test thoroughly**: `python test_provider_integration.py`
6. **Open a PR** with description
7. **Respond to feedback** and iterate
8. **Merge** once approved

---

## 📞 Questions?

- Check [`DEVELOPER_ONBOARDING.md`](./DEVELOPER_ONBOARDING.md) for setup help
- Check [`ARCHITECTURE.md`](./ARCHITECTURE.md) for system design
- Check [`README.md`](./README.md) for project overview
- Open an issue for specific questions

---

**Happy coding! 🧭**
