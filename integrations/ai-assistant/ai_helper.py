"""
AI Helper - Shared functionality for Gemini, ChatGPT, and Azure OpenAI integrations.
Similar to Home Assistant's AI helper pattern.
"""
import logging
from typing import Dict, Any, Optional
import json


class AIHelper:
    """Helper class providing shared AI functionality for multiple providers."""

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        chatgpt_api_key: Optional[str] = None,
        azure_openai_api_key: Optional[str] = None,
        azure_openai_endpoint: Optional[str] = None,
        azure_openai_deployment: Optional[str] = None,
        azure_openai_api_version: Optional[str] = None,
        default_provider: str = "gemini",
        gemini_model: str = "gemini-pro",
        chatgpt_model: str = "gpt-4",
        azure_openai_model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize AI Helper.

        Args:
            gemini_api_key: Google Gemini API key
            chatgpt_api_key: OpenAI API key
            azure_openai_api_key: Azure OpenAI API key
            azure_openai_endpoint: Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com)
            azure_openai_deployment: Azure OpenAI deployment name
            azure_openai_api_version: Azure OpenAI API version (default: "2024-02-15-preview")
            default_provider: Default provider ("gemini", "chatgpt", or "azure")
            gemini_model: Gemini model name
            chatgpt_model: ChatGPT model name
            azure_openai_model: Azure OpenAI model name (if different from deployment)
            max_tokens: Maximum tokens for responses
            temperature: Temperature for generation
            logger: Logger instance
        """
        self.gemini_api_key = gemini_api_key
        self.chatgpt_api_key = chatgpt_api_key
        self.azure_openai_api_key = azure_openai_api_key
        self.azure_openai_endpoint = azure_openai_endpoint
        self.azure_openai_deployment = azure_openai_deployment
        self.azure_openai_api_version = azure_openai_api_version or "2024-02-15-preview"
        self.default_provider = default_provider
        self.gemini_model = gemini_model
        self.chatgpt_model = chatgpt_model
        self.azure_openai_model = azure_openai_model or azure_openai_deployment
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.logger = logger or logging.getLogger(__name__)

        # Lazy import providers
        self._gemini_client = None
        self._chatgpt_client = None
        self._azure_openai_client = None

    async def query(
        self,
        prompt: str,
        provider: str = "auto",
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Query AI provider with a prompt.

        Args:
            prompt: The prompt/question
            provider: "gemini", "chatgpt", "azure", or "auto"
            system_prompt: Optional system prompt
            max_tokens: Optional max tokens override
            temperature: Optional temperature override

        Returns:
            Dictionary with response text and metadata
        """
        # Determine provider
        if provider == "auto":
            provider = self._select_best_provider()

        if provider == "gemini":
            return await self._query_gemini(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
        elif provider == "chatgpt":
            return await self._query_chatgpt(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
        elif provider == "azure" or provider == "azure_openai":
            return await self._query_azure_openai(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _select_best_provider(self) -> str:
        """Select the best available provider based on default_provider setting."""
        # First check if default provider is available
        if self.default_provider == "gemini" and self.gemini_api_key:
            return "gemini"
        elif self.default_provider == "chatgpt" and self.chatgpt_api_key:
            return "chatgpt"
        elif self.default_provider == "azure" and self.azure_openai_api_key:
            return "azure"

        # Fallback to first available provider
        if self.gemini_api_key:
            return "gemini"
        elif self.chatgpt_api_key:
            return "chatgpt"
        elif self.azure_openai_api_key:
            return "azure"
        else:
            raise ValueError("No AI provider API keys configured")

    async def _query_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Query Google Gemini API."""
        if not self.gemini_api_key:
            raise ValueError("Gemini API key not configured")

        try:
            import google.generativeai as genai

            # Initialize client if needed
            if self._gemini_client is None:
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_client = genai.GenerativeModel(self.gemini_model)

            # Build full prompt with system prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Generate content
            response = self._gemini_client.generate_content(
                full_prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": temperature
                }
            )

            return {
                "text": response.text,
                "provider": "gemini",
                "model": self.gemini_model,
                "tokens_used": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            }
        except ImportError:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        except Exception as e:
            self.logger.error(f"Gemini query failed: {e}")
            raise

    async def _query_chatgpt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Query OpenAI ChatGPT API."""
        if not self.chatgpt_api_key:
            raise ValueError("ChatGPT API key not configured")

        try:
            from openai import OpenAI

            # Initialize client if needed
            if self._chatgpt_client is None:
                self._chatgpt_client = OpenAI(api_key=self.chatgpt_api_key)

            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Generate response
            response = self._chatgpt_client.chat.completions.create(
                model=self.chatgpt_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            return {
                "text": response.choices[0].message.content,
                "provider": "chatgpt",
                "model": self.chatgpt_model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            self.logger.error(f"ChatGPT query failed: {e}")
            raise

    async def _query_azure_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Query Azure OpenAI Service (Microsoft Copilot)."""
        if not self.azure_openai_api_key:
            raise ValueError("Azure OpenAI API key not configured")
        if not self.azure_openai_endpoint:
            raise ValueError("Azure OpenAI endpoint not configured")
        if not self.azure_openai_deployment:
            raise ValueError("Azure OpenAI deployment name not configured")

        try:
            from openai import AzureOpenAI

            # Initialize client if needed
            if self._azure_openai_client is None:
                self._azure_openai_client = AzureOpenAI(
                    api_key=self.azure_openai_api_key,
                    api_version=self.azure_openai_api_version,
                    azure_endpoint=self.azure_openai_endpoint
                )

            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Generate response using deployment name
            response = self._azure_openai_client.chat.completions.create(
                model=self.azure_openai_deployment,  # Use deployment name as model
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            return {
                "text": response.choices[0].message.content,
                "provider": "azure",
                "model": self.azure_openai_model or self.azure_openai_deployment,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            self.logger.error(f"Azure OpenAI query failed: {e}")
            raise

    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available."""
        if provider == "gemini":
            return bool(self.gemini_api_key)
        elif provider == "chatgpt":
            return bool(self.chatgpt_api_key)
        elif provider == "azure" or provider == "azure_openai":
            return bool(self.azure_openai_api_key and self.azure_openai_endpoint and self.azure_openai_deployment)
        return False

    def get_available_providers(self) -> list:
        """Get list of available providers."""
        providers = []
        if self.gemini_api_key:
            providers.append("gemini")
        if self.chatgpt_api_key:
            providers.append("chatgpt")
        if self.azure_openai_api_key and self.azure_openai_endpoint and self.azure_openai_deployment:
            providers.append("azure")
        return providers
