"""
Robust LLM Client with Retry Logic and Fallbacks

Handles API rate limits, overloads, and provides backup options.
"""
import time
import json
from typing import Dict, Optional, List
import anthropic
import openai
import google.generativeai as genai
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model_used: str
    success: bool
    error: Optional[str] = None


class RobustLLMClient:
    """LLM client with retry logic and multiple provider support"""
    
    def __init__(self, anthropic_key: str = None, openai_key: str = None, gemini_key: str = None):
        self.anthropic_client = None
        self.openai_client = None
        self.gemini_configured = False
        
        if anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        
        if openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)
            
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.gemini_configured = True
    
    def query_with_retry(self, prompt: str, max_tokens: int = 2000, max_retries: int = 3) -> LLMResponse:
        """Query LLM with retry logic and fallback providers"""
        
        # Try Anthropic Claude first
        if self.anthropic_client:
            for attempt in range(max_retries):
                try:
                    print(f"🤖 Trying Claude (attempt {attempt + 1}/{max_retries})...")
                    
                    response = self.anthropic_client.messages.create(
                        model="claude-sonnet-4-20250514",  # Claude Sonnet 4
                        max_tokens=max_tokens,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    return LLMResponse(
                        content=response.content[0].text,
                        model_used="Claude Sonnet 4",
                        success=True
                    )
                    
                except anthropic.APIError as e:
                    error_msg = str(e)
                    print(f"❌ Claude error: {error_msg}")
                    
                    if "overloaded" in error_msg.lower():
                        wait_time = (attempt + 1) * 10  # Exponential backoff
                        print(f"⏳ Claude overloaded. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    elif "rate_limit" in error_msg.lower():
                        wait_time = (attempt + 1) * 15
                        print(f"⏳ Rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        break  # Don't retry for other errors
                
                except Exception as e:
                    print(f"❌ Claude unexpected error: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    break
        
        # Secondary fallback to Google Gemini 2.5 Pro
        if self.gemini_configured:
            for attempt in range(max_retries):
                try:
                    print(f"🤖 Trying Gemini 2.5 Pro (attempt {attempt + 1}/{max_retries})...")
                    
                    model = genai.GenerativeModel('gemini-2.5-pro')
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=max_tokens,
                            temperature=0.1
                        )
                    )
                    
                    if response.text:
                        return LLMResponse(
                            content=response.text,
                            model_used="Gemini 2.5 Pro",
                            success=True
                        )
                    else:
                        print("❌ Gemini returned empty response")
                        continue
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ Gemini error: {error_msg}")
                    
                    if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                        wait_time = (attempt + 1) * 25
                        print(f"⏳ Gemini rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    elif "overloaded" in error_msg.lower() or "unavailable" in error_msg.lower():
                        wait_time = (attempt + 1) * 15
                        print(f"⏳ Gemini unavailable. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(8)
                            continue
                        break
        
        # Final fallback to OpenAI GPT-4
        if self.openai_client:
            for attempt in range(max_retries):
                try:
                    print(f"🤖 Trying GPT-4 (final attempt {attempt + 1}/{max_retries})...")
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4.1-2025-04-14",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens
                    )
                    
                    return LLMResponse(
                        content=response.choices[0].message.content,
                        model_used="GPT-4.1",
                        success=True
                    )
                    
                except openai.APIError as e:
                    error_msg = str(e)
                    print(f"❌ GPT-4 error: {error_msg}")
                    
                    if "rate_limit" in error_msg.lower():
                        wait_time = (attempt + 1) * 20
                        print(f"⏳ GPT-4 rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        break
                
                except Exception as e:
                    print(f"❌ GPT-4 unexpected error: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    break
        
        # If all providers failed
        return LLMResponse(
            content="",
            model_used="None",
            success=False,
            error="All LLM providers failed or unavailable"
        )
    
    def query_code_analysis(self, prompt: str, max_tokens: int = 2000) -> LLMResponse:
        """Use Claude Sonnet 4 specifically for code analysis tasks"""
        if not self.anthropic_client:
            return LLMResponse(
                content="", model_used="None", success=False,
                error="Claude API key required for code analysis"
            )
        
        # Force Claude-only for code analysis
        for attempt in range(3):
            try:
                print(f"🧠 Claude Sonnet 4 code analysis (attempt {attempt + 1}/3)...")
                
                response = self.anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                return LLMResponse(
                    content=response.content[0].text,
                    model_used="Claude Sonnet 4 (Code Analysis)",
                    success=True
                )
                
            except anthropic.APIError as e:
                error_msg = str(e)
                print(f"❌ Claude error: {error_msg}")
                
                if "overloaded" in error_msg.lower():
                    wait_time = (attempt + 1) * 15
                    print(f"⏳ Claude overloaded. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    break
            except Exception as e:
                print(f"❌ Claude unexpected error: {e}")
                if attempt < 2:
                    time.sleep(10)
                    continue
                break
        
        return LLMResponse(
            content="", model_used="Claude Sonnet 4", success=False,
            error="Claude code analysis failed after retries"
        )
    
    def query_creative_generation(self, prompt: str, max_tokens: int = 2000) -> LLMResponse:
        """Use Gemini 2.5 Pro specifically for creative generation tasks"""
        if not self.gemini_configured:
            return LLMResponse(
                content="", model_used="None", success=False,
                error="Gemini API key required for creative generation"
            )
        
        # Force Gemini-only for creative generation
        for attempt in range(3):
            try:
                print(f"🎨 Gemini 2.5 Pro creative generation (attempt {attempt + 1}/3)...")
                
                model = genai.GenerativeModel('gemini-2.5-pro')
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.8  # Higher creativity for generation
                    )
                )
                
                if response.text:
                    return LLMResponse(
                        content=response.text,
                        model_used="Gemini 2.5 Pro (Creative Generation)",
                        success=True
                    )
                else:
                    print("❌ Gemini returned empty response")
                    continue
                    
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Gemini error: {error_msg}")
                
                if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    wait_time = (attempt + 1) * 20
                    print(f"⏳ Gemini rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    if attempt < 2:
                        time.sleep(8)
                        continue
                    break
        
        return LLMResponse(
            content="", model_used="Gemini 2.5 Pro", success=False,
            error="Gemini creative generation failed after retries"
        )

    def query_simple(self, prompt: str, context: str = "game analysis") -> Dict:
        """Simplified query for basic analysis with better error handling"""
        
        # Shorter, more focused prompt to avoid token limits
        focused_prompt = f"""
        {context.title()} Task:
        {prompt}
        
        Provide response in valid JSON format only, no extra text.
        """
        
        response = self.query_with_retry(focused_prompt, max_tokens=1500)
        
        if not response.success:
            return {"error": response.error, "model": response.model_used}
        
        try:
            # Parse JSON response
            if '```json' in response.content:
                start = response.content.find('```json') + 7
                end = response.content.find('```', start)
                json_text = response.content[start:end].strip()
            elif '{' in response.content:
                start = response.content.find('{')
                end = response.content.rfind('}') + 1
                json_text = response.content[start:end]
            else:
                json_text = response.content
            
            result = json.loads(json_text)
            result["_model_used"] = response.model_used
            return result
            
        except json.JSONDecodeError:
            # Return structured response even if JSON parsing fails
            return {
                "summary": response.content[:200] + "..." if len(response.content) > 200 else response.content,
                "analysis": "Raw LLM response (JSON parsing failed)",
                "model_used": response.model_used,
                "_raw_response": response.content
            }