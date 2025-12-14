from services.integration_base import Integration
from services.service_registry import service_registry
import logging
import json
from typing import Dict, Any, Optional, List
import os

# Import AI helper
try:
    from .ai_helper import AIHelper
except ImportError:
    # Fallback for when running as standalone
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from ai_helper import AIHelper


class AIAssistantIntegration(Integration):
    """
    AI Assistant Integration supporting Gemini, ChatGPT, and Azure OpenAI.

    This integration is fully dynamic and works with:
    - System integrations (from backend/app/system_integrations)
    - Standard integrations (from integrations store)
    - Custom integrations (from data/integrations/custom)
    - Local integrations (from data/integrations/local)

    All services are registered dynamically and can be discovered at runtime.
    """

    async def async_setup(self):
        self.logger.info("Setting up AI Assistant Integration")

        # Initialize AI helper
        self.ai_helper = AIHelper(
            gemini_api_key=self.config.get("gemini_api_key"),
            chatgpt_api_key=self.config.get("chatgpt_api_key"),
            azure_openai_api_key=self.config.get("azure_openai_api_key"),
            azure_openai_endpoint=self.config.get("azure_openai_endpoint"),
            azure_openai_deployment=self.config.get("azure_openai_deployment"),
            azure_openai_api_version=self.config.get("azure_openai_api_version"),
            default_provider=self.config.get("default_provider", "gemini"),
            gemini_model=self.config.get("gemini_model", "gemini-pro"),
            chatgpt_model=self.config.get("chatgpt_model", "gpt-4"),
            azure_openai_model=self.config.get("azure_openai_model"),
            max_tokens=self.config.get("max_tokens", 2000),
            temperature=self.config.get("temperature", 0.7),
            logger=self.logger
        )

        # Register services
        service_registry.register(
            domain=self.domain,
            service="query",
            service_func=self.query,
            schema={
                "question": str,
                "provider": str,
                "context": dict,
                "system_prompt": str,
                "max_tokens": int,
                "temperature": float
            },
            description="Query the AI assistant"
        )

        service_registry.register(
            domain=self.domain,
            service="analyze_logs",
            service_func=self.analyze_logs,
            schema={
                "log_data": list,
                "question": str,
                "provider": str
            },
            description="Analyze log entries with AI"
        )

        service_registry.register(
            domain=self.domain,
            service="enhance_workflow",
            service_func=self.enhance_workflow,
            schema={
                "workflow": dict,
                "goal": str,
                "provider": str
            },
            description="Enhance a workflow using AI"
        )

        service_registry.register(
            domain=self.domain,
            service="generate_workflow",
            service_func=self.generate_workflow,
            schema={
                "description": str,
                "context": dict,
                "provider": str
            },
            description="Generate a workflow from description"
        )

        return True

    async def query(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the AI assistant with a question.

        Args:
            data: Dictionary containing:
                - question: The question to ask
                - provider: "gemini", "chatgpt", or "auto"
                - context: Optional context data
                - system_prompt: Optional custom system prompt
                - max_tokens: Optional max tokens override
                - temperature: Optional temperature override

        Returns:
            Dictionary with response and metadata
        """
        question = data.get("question", "")
        if not question:
            raise ValueError("question is required")

        provider = data.get("provider", "auto")
        context = data.get("context")
        system_prompt = data.get("system_prompt")
        max_tokens = data.get("max_tokens")
        temperature = data.get("temperature")

        try:
            # Build prompt with context if provided
            prompt = question
            if context:
                context_str = json.dumps(context, indent=2)
                prompt = f"{prompt}\n\nContext:\n{context_str}"

            # Query AI
            response = await self.ai_helper.query(
                prompt=prompt,
                provider=provider,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )

            return {
                "response": response.get("text", ""),
                "provider": response.get("provider"),
                "model": response.get("model"),
                "tokens_used": response.get("tokens_used", 0),
                "success": True
            }
        except Exception as e:
            self.logger.error(f"AI query failed: {e}")
            raise

    async def analyze_logs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze log entries and provide insights.

        Args:
            data: Dictionary containing:
                - log_data: Array of log entries
                - question: Optional specific question
                - provider: AI provider to use

        Returns:
            Dictionary with analysis and insights
        """
        log_data = data.get("log_data", [])
        if not log_data:
            raise ValueError("log_data is required")

        question = data.get("question", "Analyze these logs and provide insights, errors, and recommendations.")
        provider = data.get("provider", "auto")

        try:
            # Format logs for AI consumption
            logs_summary = self._format_logs_for_ai(log_data)

            # Build prompt
            prompt = f"""{question}

Log Data:
{logs_summary}

Please provide:
1. Summary of key events
2. Any errors or warnings
3. Patterns or anomalies
4. Recommendations"""

            response = await self.ai_helper.query(
                prompt=prompt,
                provider=provider,
                system_prompt="You are a log analysis expert. Analyze logs efficiently and provide actionable insights."
            )

            return {
                "analysis": response.get("text", ""),
                "provider": response.get("provider"),
                "model": response.get("model"),
                "logs_analyzed": len(log_data),
                "success": True
            }
        except Exception as e:
            self.logger.error(f"Log analysis failed: {e}")
            raise

    async def enhance_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance or optimize a workflow using AI.

        Args:
            data: Dictionary containing:
                - workflow: Workflow definition
                - goal: Optional goal for enhancement
                - provider: AI provider to use

        Returns:
            Dictionary with enhanced workflow
        """
        workflow = data.get("workflow")
        if not workflow:
            raise ValueError("workflow is required")

        goal = data.get("goal", "Optimize this workflow for better performance and error handling.")
        provider = data.get("provider", "auto")

        try:
            workflow_str = json.dumps(workflow, indent=2)

            prompt = f"""{goal}

Current Workflow:
{workflow_str}

Please provide an enhanced version of this workflow with:
1. Better error handling
2. Optimized performance
3. Clear documentation
4. Best practices

Return the enhanced workflow as valid JSON."""

            response = await self.ai_helper.query(
                prompt=prompt,
                provider=provider,
                system_prompt="You are a workflow optimization expert. Enhance workflows while maintaining functionality."
            )

            # Try to extract JSON from response
            response_text = response.get("text", "")
            enhanced_workflow = self._extract_json_from_response(response_text)

            return {
                "enhanced_workflow": enhanced_workflow or workflow,
                "suggestions": response_text,
                "provider": response.get("provider"),
                "model": response.get("model"),
                "success": True
            }
        except Exception as e:
            self.logger.error(f"Workflow enhancement failed: {e}")
            raise

    async def generate_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a new workflow based on a description.

        Args:
            data: Dictionary containing:
                - description: Description of desired workflow
                - context: Optional context about available integrations
                - provider: AI provider to use

        Returns:
            Dictionary with generated workflow
        """
        description = data.get("description", "")
        if not description:
            raise ValueError("description is required")

        context = data.get("context", {})
        provider = data.get("provider", "auto")

        try:
            context_str = ""
            if context:
                context_str = f"\n\nAvailable Integrations:\n{json.dumps(context, indent=2)}"

            prompt = f"""Generate a faneX-ID workflow based on this description:

{description}
{context_str}

Please create a complete workflow JSON with:
1. Name and description
2. Triggers
3. Steps with proper service calls
4. Error handling
5. Documentation

Return the workflow as valid JSON following faneX-ID workflow schema."""

            response = await self.ai_helper.query(
                prompt=prompt,
                provider=provider,
                system_prompt="You are a workflow generation expert. Create functional faneX-ID workflows."
            )

            # Extract JSON from response
            response_text = response.get("text", "")
            workflow = self._extract_json_from_response(response_text)

            return {
                "workflow": workflow,
                "explanation": response_text,
                "provider": response.get("provider"),
                "model": response.get("model"),
                "success": True
            }
        except Exception as e:
            self.logger.error(f"Workflow generation failed: {e}")
            raise

    def _format_logs_for_ai(self, log_data: List[Dict]) -> str:
        """Format log entries for efficient AI consumption."""
        if not log_data:
            return "No logs provided."

        # Limit to most recent/relevant entries
        max_logs = 100
        logs_to_analyze = log_data[-max_logs:] if len(log_data) > max_logs else log_data

        formatted = []
        for entry in logs_to_analyze:
            timestamp = entry.get("timestamp", entry.get("time", ""))
            level = entry.get("level", entry.get("severity", "INFO"))
            message = entry.get("message", entry.get("msg", ""))
            source = entry.get("source", entry.get("logger", ""))

            formatted.append(f"[{timestamp}] {level} {source}: {message}")

        return "\n".join(formatted)

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """Extract JSON from AI response text."""
        import re

        # Try to find JSON block
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Try code block
        code_match = re.search(r'```(?:json)?\s*(\{[\s\S]*\})\s*```', response_text)
        if code_match:
            try:
                return json.loads(code_match.group(1))
            except json.JSONDecodeError:
                pass

        return None
