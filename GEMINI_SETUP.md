# Google Gemini 2.5 Pro Setup Guide

## 🚀 Get Your Gemini API Key

### Step 1: Google AI Studio
1. Go to https://aistudio.google.com/
2. Sign in with your Google account
3. Click "Get API key" in the left sidebar
4. Create new API key (will start with `AIza...`)
5. Copy the key securely

### Step 2: Test Gemini Access
```bash
# Test if Gemini key works
source venv/bin/activate
python scripts/robust_llm_test.py --gemini-key AIzaSyYourKeyHere
```

## 🔄 Triple Fallback System Now Available

### Priority Order:
1. **🥇 Anthropic Claude 3.5 Sonnet** (primary - best at code analysis)
2. **🥈 Google Gemini 2.5 Pro** (secondary - fast & intelligent)  
3. **🥉 OpenAI GPT-4 Turbo** (final backup - most reliable)

### Full Command Options:
```bash
# Use all three providers as fallbacks
python scripts/robust_llm_test.py \
  --anthropic-key sk-ant-your-key \
  --openai-key sk-your-openai-key \
  --gemini-key AIzaSyYour-gemini-key

# Or use environment variables (more secure)
export ANTHROPIC_API_KEY="sk-ant-your-key"
export OPENAI_API_KEY="sk-your-openai-key"
export GEMINI_API_KEY="AIzaSyYour-gemini-key"
python scripts/robust_llm_test.py
```

## 💰 Cost Comparison (Per Analysis)

| Provider | Cost | Best For |
|----------|------|----------|
| **Claude** | $0.50-2.00 | Code understanding, game analysis |
| **GPT-4** | $1.00-3.00 | Creative concepts, general reasoning |
| **Gemini** | $0.25-1.50 | Cost-effective backup, fast responses |

## 🎯 What This Gives You

### Maximum Reliability
- If Claude is overloaded → tries GPT-4
- If GPT-4 is rate limited → tries Gemini
- If all fail → clear error messages

### Different Strengths
- **Claude**: Best semantic code analysis
- **GPT-4**: Most creative mini-game concepts
- **Gemini**: Fast, cost-effective insights

### Smart Retry Logic
- Exponential backoff for overloaded servers
- Different wait times for different error types
- Up to 3 attempts per provider = 9 total attempts

## 🧪 Test the Complete System

```bash
# This will now try all three SOTA LLMs!
source venv/bin/activate
python scripts/robust_llm_test.py --anthropic-key sk-ant-your-key
```

Expected output:
```
🤖 Trying Claude (attempt 1/3)...
⏳ Claude overloaded. Waiting 10s before retry...
🤖 Trying Claude (attempt 2/3)...
❌ Claude error: Overloaded
🤖 Trying Gemini 2.5 Pro (attempt 1/3)...
✅ LLM Analysis Complete!
📡 Model used: Gemini 2.5 Pro
```

Now you have the most robust SOTA LLM system possible with triple fallback protection! 🤖