# Debate Feature - Quick Start Guide

## What's New?

A brand new **Debate Arena** page where LLMs debate each other on topics you choose, and you vote on the winner!

## How to Access

1. Navigate to `debate.html` in your project
2. Or click **"Debate!"** in the navigation menu

## Step-by-Step Usage

### Starting a Debate

1. **Select Pro Model** - Choose which LLM will argue in favor
   - Default: GPT-4o Mini
   - Options: OpenAI, Anthropic (Claude), Google (Gemini)

2. **Select Con Model** - Choose which LLM will argue against
   - Default: Gemini 2.0 Flash
   - Can be same or different as Pro

3. **Enter Topic** - Type any debate topic you want to explore
   - Examples: "Universal Basic Income", "Remote Work", "AI Regulation"
   - Be specific for best results

4. **Start Debate** - Click the button and watch the magic happen!
   - Page shows loading spinner
   - Backend generates arguments from both models
   - Arguments appear with typewriter effect

### Voting

1. **Read Both Arguments** - Review the Pro and Con positions
2. **Decide Winner** - Choose which argument was better reasoned/presented
3. **Click Vote Button** - Vote for the winning model
   - "Vote: Pro Wins" button on left
   - "Vote: Con Wins" button on right
4. **Rating Update** - Winner gains Elo points, loser loses points
   - Ratings visible on Leaderboard page

### Starting Another Debate

- Click **"Start New Debate"** to reset and try again
- Models and topic input return to defaults
- Start a fresh debate!

## Features

✅ **Multi-Provider Support**
- OpenAI (GPT-4, GPT-4 Mini, GPT-3.5 Turbo)
- Anthropic (Claude 3 Haiku, Sonnet, Opus)
- Google (Gemini 1.5 Pro, 2.0 Flash)

✅ **Integrated Voting**
- Votes update model Elo ratings
- Rankings visible on Leaderboard

✅ **Responsive Design**
- Works on desktop, tablet, mobile

✅ **Error Handling**
- Clear error messages
- Retry functionality

## Tips for Better Debates

1. **Be Specific** - Detailed topics generate better arguments
   - ✅ "Should companies require employees to return to office 5 days/week?"
   - ❌ "work"

2. **Try Different Models** - See how OpenAI, Claude, and Gemini argue differently

3. **Explore Controversial Topics** - These often generate the most interesting debates

4. **Compare Same Models** - See internal consistency and variation

## Technical Details

### API Endpoint

The new `/api/debate` endpoint:
- Takes topic + model names
- Returns pro and con arguments
- Integrates with existing voting system

### Styling

- Consistent with Battle! and Ratings pages
- Indigo (#4f46e5) primary color
- Pro arguments: Green accent (left side)
- Con arguments: Red accent (right side)

### Performance

- Debates take ~5-15 seconds depending on models
- Arguments are 2-3 paragraphs each
- Temperature 0.7 for diverse responses

## Troubleshooting

### Debate Won't Start
- Check API keys are set (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`)
- Make sure backend is running
- Try a different topic

### Models Not Responding
- Selected model may be unavailable
- Try different model combinations
- Check API service status

### Can't Vote
- Make sure database is initialized
- Refresh page and try again
- Check browser console for errors (F12)

## Navigation

All pages now have consistent navigation:
- **Home** - Main page with compass and info
- **Battle!** - Compare model responses to single prompts
- **Debate!** - Watch models debate topics (NEW)
- **Ratings** - Leaderboard of model Elo ratings

## Want to Explore?

Try these debate topics:
- "Universal Basic Income would improve society"
- "Artificial Intelligence poses existential risk"
- "Remote work is more productive than office work"
- "Social media should be heavily regulated"
- "Cryptocurrency will replace traditional currency"
- "Nuclear power is essential for climate goals"

Have fun debating! 🎭
