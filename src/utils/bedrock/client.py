"""Amazon Bedrock client utilities"""
import json
import os
import boto3
from typing import Dict, Any, Optional

class BedrockClient:
    """Client for Amazon Bedrock API"""
    
    def __init__(self):
        self.region = os.getenv('BEDROCK_REGION', 'us-east-1')
        # Try Meta Llama 3 8B first (should have fewer restrictions)
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'meta.llama3-8b-instruct-v1:0')
        self.client = boto3.client('bedrock-runtime', region_name=self.region)
        
        # Determine model type for different API formats
        if 'anthropic' in self.model_id:
            self.model_type = 'anthropic'
        elif 'amazon.nova' in self.model_id:
            self.model_type = 'nova'
        elif 'meta.llama' in self.model_id:
            self.model_type = 'llama'
        elif 'mistral' in self.model_id:
            self.model_type = 'mistral'
        else:
            self.model_type = 'unknown'
    
    def invoke_model(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Invoke any supported model via Bedrock
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        try:
            if self.model_type == 'anthropic':
                return self._invoke_anthropic(prompt, system_prompt, max_tokens, temperature)
            elif self.model_type == 'nova':
                return self._invoke_nova(prompt, system_prompt, max_tokens, temperature)
            elif self.model_type == 'llama':
                return self._invoke_llama(prompt, system_prompt, max_tokens, temperature)
            elif self.model_type == 'mistral':
                return self._invoke_mistral(prompt, system_prompt, max_tokens, temperature)
            else:
                # Fallback to generic approach
                return self._invoke_generic(prompt, system_prompt, max_tokens, temperature)
                
        except Exception as e:
            print(f"Error invoking Bedrock model {self.model_id}: {e}")
            raise
    
    def _invoke_anthropic(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Invoke Anthropic Claude models"""
        messages = [{"role": "user", "content": prompt}]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system_prompt:
            body["system"] = system_prompt
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _invoke_nova(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Invoke Amazon Nova models"""
        messages = [{"role": "user", "content": prompt}]
        
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        body = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['output']['message']['content'][0]['text']
    
    def _invoke_llama(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Invoke Meta Llama models"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        
        body = {
            "prompt": full_prompt,
            "max_gen_len": max_tokens,
            "temperature": temperature,
            "top_p": 0.9
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['generation']
    
    def _invoke_mistral(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Invoke Mistral models"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        
        body = {
            "prompt": full_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['outputs'][0]['text']
    
    def _invoke_generic(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Generic fallback for unknown models"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        
        body = {
            "prompt": full_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        # Try common response formats
        if 'text' in response_body:
            return response_body['text']
        elif 'generation' in response_body:
            return response_body['generation']
        elif 'output' in response_body:
            return str(response_body['output'])
        else:
            return str(response_body)
    
    def extract_ingredients(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract and identify ingredients from OCR text
        
        Args:
            ocr_text: Raw text from Textract
            
        Returns:
            Dictionary with identified ingredients
        """
        system_prompt = """You are an expert at analyzing food labels and extracting ingredient information.
Your task is to identify all ingredients from the provided text, which comes from OCR of a food label.

Return a JSON object with:
- ingredients: list of ingredient names (normalized)
- confidence: your confidence level (high/medium/low)
- notes: any observations about the label quality

Be thorough but only include actual ingredients, not nutritional information or other label text."""

        prompt = f"""Extract all ingredients from this food label text:

{ocr_text}

Return only valid JSON."""

        try:
            response = self.invoke_model(prompt, system_prompt, max_tokens=1000, temperature=0.3)
            # Parse JSON from response
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if response isn't valid JSON
            return {
                "ingredients": [],
                "confidence": "low",
                "notes": "Failed to parse ingredients"
            }
    
    def normalize_ingredient(self, ingredient: str) -> Dict[str, Any]:
        """
        Normalize ingredient name to standard regulatory terminology
        
        Args:
            ingredient: Raw ingredient name
            
        Returns:
            Normalized ingredient information
        """
        system_prompt = """You are an expert in food ingredient nomenclature and regulatory terminology.
Your task is to normalize ingredient names to their standard regulatory identifiers.

Consider:
- E-numbers (e.g., E102, E110)
- Chemical names (e.g., Tartrazine, Sunset Yellow FCF)
- Common names
- Regional variations
- Hindi/English variations

Return JSON with:
- standard_name: The official regulatory name
- e_number: E-number if applicable
- chemical_name: Chemical/scientific name
- common_names: List of common alternative names
- category: Ingredient category (color, preservative, etc.)"""

        prompt = f"""Normalize this ingredient name: "{ingredient}"

Return only valid JSON."""

        try:
            response = self.invoke_model(prompt, system_prompt, max_tokens=500, temperature=0.2)
            return json.loads(response)
        except:
            return {
                "standard_name": ingredient,
                "e_number": None,
                "chemical_name": ingredient,
                "common_names": [ingredient],
                "category": "unknown"
            }
    
    def generate_regulatory_explanation(
        self,
        ingredient: str,
        comparison: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for regulatory differences
        
        Args:
            ingredient: Ingredient name
            comparison: Regulatory comparison data from RegulatoryAnalyzer
            
        Returns:
            Human-readable explanation
        """
        system_prompt = """You are an expert in food regulations across India (FSSAI), EU, and US (FDA).
Your task is to explain regulatory differences in a clear, factual manner.

IMPORTANT GUIDELINES:
- Provide ONLY factual regulatory information
- DO NOT give medical advice or health recommendations
- DO NOT make safety claims
- Always include disclaimer that this is informational only
- Cite regulatory sources when possible
- Explain WHY regulations differ when known
- Be concise but informative
- Use simple language suitable for WhatsApp messaging
- Include a short "regulatory health-impact context" sentence explaining what
  bans/warnings/restrictions imply for consumers (without diagnosis/treatment advice)"""

        if not comparison or not comparison.get('jurisdictions'):
            return f"No specific regulatory data found for {ingredient}. This may be a basic ingredient or not commonly regulated as a food additive."

        # Build the prompt with comparison data
        jurisdictions_info = ""
        for jurisdiction, data in comparison['jurisdictions'].items():
            status = data.get('status', 'unknown')
            authority = data.get('authority', '')
            limits = data.get('limits', '')
            restrictions = data.get('restrictions', '')
            
            jurisdictions_info += f"\n{jurisdiction.upper()} ({authority}): {status}"
            if limits:
                jurisdictions_info += f" - Limits: {limits}"
            if restrictions:
                jurisdictions_info += f" - Restrictions: {restrictions}"

        differences = comparison.get('differences', [])
        warnings = comparison.get('warnings', [])
        summary = comparison.get('summary', '')
        health_context = comparison.get('health_context', '')

        prompt = f"""Explain the regulatory status of {ingredient}:

REGULATORY STATUS:{jurisdictions_info}

SUMMARY: {summary}

DIFFERENCES: {', '.join(differences) if differences else 'No major differences'}

WARNINGS: {', '.join(warnings) if warnings else 'No specific warnings'}

REGULATORY HEALTH-IMPACT CONTEXT: {health_context if health_context else 'No additional context provided.'}

Provide a clear, concise explanation suitable for a WhatsApp message (max 200 words).
Include appropriate disclaimers."""

        return self.invoke_model(prompt, system_prompt, max_tokens=800, temperature=0.3)
