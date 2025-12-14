# AI Assistant Integration

AI-powered assistant integration for faneX-ID supporting Google Gemini, OpenAI ChatGPT, and Azure OpenAI (Microsoft Copilot) for intelligent workflows and admin queries.

## Overview

The AI Assistant integration enables faneX-ID to leverage artificial intelligence for:
- **Intelligent Workflows**: Make workflows dynamic and intelligent with AI decision-making
- **Log Analysis**: Analyze logs and provide insights with one click
- **Admin Queries**: Ask questions about system state, logs, and data
- **Workflow Enhancement**: Automatically optimize and enhance workflows
- **Workflow Generation**: Generate workflows from natural language descriptions

## Features

- **Multi-Provider Support**: Works with Google Gemini, OpenAI ChatGPT, and Azure OpenAI (Microsoft Copilot)
- **Intelligent Workflows**: Use AI to make dynamic decisions in workflows
- **Log Analysis**: One-click AI analysis of log entries
- **Admin Queries**: Query system state and get AI-powered answers
- **Workflow Enhancement**: Automatically improve workflow performance and error handling
- **Workflow Generation**: Create workflows from natural language
- **Enterprise-Ready**: Azure OpenAI support for organizations using Microsoft Azure

## Setup

### Prerequisites

- At least one of the following:
  - Google Gemini API key (for Gemini)
  - OpenAI API key (for ChatGPT)
  - Azure OpenAI credentials (for Microsoft Copilot/Azure OpenAI)
- Network connectivity to AI provider APIs
- Python packages: `openai>=1.0.0`, `google-generativeai>=0.3.0`

### Configuration

Configure via Admin Panel under **Settings > Integrations > AI Assistant**.

#### Required Settings

At least one API key is required:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `gemini_api_key` | string | ✅* | Google Gemini API key |
| `chatgpt_api_key` | string | ✅* | OpenAI API key |
| `azure_openai_api_key` | string | ✅* | Azure OpenAI API key |
| `azure_openai_endpoint` | string | ✅* | Azure OpenAI endpoint URL |
| `azure_openai_deployment` | string | ✅* | Azure OpenAI deployment name |

*At least one provider's credentials are required

#### Optional Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `default_provider` | string | ❌ | Default provider: "gemini", "chatgpt", or "azure" (default: "gemini") |
| `gemini_model` | string | ❌ | Gemini model (default: "gemini-pro") |
| `chatgpt_model` | string | ❌ | ChatGPT model (default: "gpt-4") |
| `azure_openai_model` | string | ❌ | Azure OpenAI model name (optional, defaults to deployment name) |
| `azure_openai_api_version` | string | ❌ | Azure OpenAI API version (default: "2024-02-15-preview") |
| `max_tokens` | integer | ❌ | Max tokens for responses (default: 2000) |
| `temperature` | number | ❌ | Temperature 0.0-2.0 (default: 0.7) |
| `enable_workflow_enhancement` | boolean | ❌ | Enable workflow enhancement (default: true) |
| `enable_log_analysis` | boolean | ❌ | Enable log analysis (default: true) |

### Getting API Keys

#### Google Gemini

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Paste into `gemini_api_key` configuration

#### OpenAI ChatGPT

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the API key
5. Paste into `chatgpt_api_key` configuration

#### Azure OpenAI (Microsoft Copilot)

Azure OpenAI Service is Microsoft's enterprise-grade AI service that provides access to OpenAI models (like GPT-4) through Azure. This is ideal for organizations that:
- Need enterprise security and compliance
- Want to use Microsoft Azure infrastructure
- Require data residency and privacy controls
- Need integration with other Azure services

**What is Azure OpenAI vs. Microsoft Copilot?**

- **Azure OpenAI Service**: The underlying API service that provides access to OpenAI models through Azure
- **Microsoft Copilot**: A branded name for Microsoft's AI assistant products that may use Azure OpenAI under the hood
- For this integration, we use **Azure OpenAI Service** directly, which gives you full control and the same capabilities as OpenAI's API, but hosted on Azure

**Setting up Azure OpenAI:**

1. **Create Azure OpenAI Resource:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Click "Create a resource"
   - Search for "Azure OpenAI"
   - Click "Create" and fill in:
     - **Subscription**: Your Azure subscription
     - **Resource Group**: Create new or use existing
     - **Region**: Choose a region (e.g., East US, West Europe)
     - **Name**: Choose a unique name (e.g., `my-ai-resource`)
     - **Pricing Tier**: Choose based on your needs

2. **Get API Key and Endpoint:**
   - After creation, go to your Azure OpenAI resource
   - Navigate to **"Keys and Endpoint"** in the left menu
   - Copy:
     - **KEY 1** or **KEY 2** → Paste into `azure_openai_api_key`
     - **Endpoint** → Paste into `azure_openai_endpoint` (e.g., `https://my-ai-resource.openai.azure.com`)

3. **Create a Deployment:**
   - In your Azure OpenAI resource, go to **"Model deployments"** or **"Deployments"**
   - Click **"Create"** or **"Manage deployments"**
   - Click **"Create new deployment"**
   - Choose a model (e.g., `gpt-4`, `gpt-35-turbo`)
   - Enter a **Deployment name** (e.g., `gpt-4`, `gpt-35-turbo`)
   - Click **"Create"**
   - Copy the deployment name → Paste into `azure_openai_deployment`

4. **Configure in faneX-ID:**
   - `azure_openai_api_key`: The API key from step 2
   - `azure_openai_endpoint`: The endpoint URL from step 2
   - `azure_openai_deployment`: The deployment name from step 3
   - `azure_openai_api_version`: Usually `2024-02-15-preview` (default)
   - `azure_openai_model`: Optional, defaults to deployment name

**Important Notes:**
- Azure OpenAI requires an Azure subscription (may have costs)
- Some regions may have waitlists for Azure OpenAI access
- The endpoint URL format is: `https://YOUR-RESOURCE-NAME.openai.azure.com`
- The deployment name is what you created, not the model name (though they can be the same)
- API version may need to be updated as Azure releases new versions

## Exposed Services

### `ai_assistant.query`

Query the AI assistant with a question and optional context.

**Parameters:**
- `question` (string, required): The question or prompt
- `provider` (string, optional): "gemini", "chatgpt", "azure", or "auto" (default: "auto")
- `context` (object, optional): Additional context data
- `system_prompt` (string, optional): Custom system prompt
- `max_tokens` (integer, optional): Max tokens override
- `temperature` (number, optional): Temperature override

**Example Workflow Action:**
```yaml
actions:
  - service: ai_assistant.query
    data:
      question: "What are the most common errors in the last 24 hours?"
      context:
        time_range: "24h"
        log_level: "error"
      provider: "azure"  # Use Azure OpenAI
```

### `ai_assistant.analyze_logs`

Analyze log entries and provide insights.

**Parameters:**
- `log_data` (array, required): Array of log entries
- `question` (string, optional): Specific question about the logs
- `provider` (string, optional): AI provider to use

**Example:**
```yaml
actions:
  - service: ai_assistant.analyze_logs
    data:
      log_data: "{{ recent_logs }}"
      question: "What patterns do you see in these errors?"
```

### `ai_assistant.enhance_workflow`

Enhance or optimize a workflow using AI.

**Parameters:**
- `workflow` (object, required): Workflow definition
- `goal` (string, optional): Goal for enhancement
- `provider` (string, optional): AI provider to use

**Example:**
```yaml
actions:
  - service: ai_assistant.enhance_workflow
    data:
      workflow: "{{ current_workflow }}"
      goal: "Add better error handling and retry logic"
```

### `ai_assistant.generate_workflow`

Generate a new workflow from a description.

**Parameters:**
- `description` (string, required): Description of desired workflow
- `context` (object, optional): Available integrations and services
- `provider` (string, optional): AI provider to use

**Example:**
```yaml
actions:
  - service: ai_assistant.generate_workflow
    data:
      description: "Create a workflow that syncs new employees to Active Directory and sends a welcome email"
      context:
        available_integrations: ["active_directory", "mail"]
```

## Use Cases

### Intelligent Workflow Decision Making

```yaml
trigger:
  type: event
  event: employee.created
actions:
  - service: ai_assistant.query
    data:
      question: "Based on this employee's department ({{ employee.department }}), what groups should they be added to?"
      context:
        employee: "{{ employee }}"
        available_groups: "{{ ad_groups }}"
      provider: "azure"  # Use Azure OpenAI for enterprise compliance
  - service: active_directory.add_to_groups
    data:
      groups: "{{ ai_response.suggested_groups }}"
```

### Log Analysis in Admin Panel

The integration automatically provides a "Ask AI" button in the log viewer that:
1. Collects recent log entries
2. Formats them efficiently for AI
3. Sends to AI with context
4. Displays insights and recommendations

### Workflow Optimization

```yaml
actions:
  - service: ai_assistant.enhance_workflow
    data:
      workflow: "{{ current_workflow }}"
      goal: "Optimize for performance and add comprehensive error handling"
```

## Admin Integration

The AI Assistant is automatically integrated into:

- **Log Viewer**: "Ask AI" button provides one-click log analysis
- **Admin Dashboard**: AI query interface for system questions
- **Workflow Editor**: AI suggestions for workflow improvement
- **System Status**: AI-powered insights about system health

## Security Notes

- **API Keys are Secret**: Store API keys securely
- **Rate Limiting**: Be aware of API rate limits
- **Data Privacy**:
  - **OpenAI/ChatGPT**: Data may be processed by OpenAI
  - **Azure OpenAI**: Data stays within your Azure subscription and region (better for compliance)
  - **Gemini**: Data processed by Google
- **Cost Management**: Monitor API usage to control costs
- **Token Limits**: Respect max_tokens to avoid excessive costs
- **Azure OpenAI Benefits**:
  - Enterprise-grade security and compliance
  - Data residency controls
  - Integration with Azure security features
  - Better for organizations with compliance requirements

## Troubleshooting

### API Key Errors

- Verify API keys are correct and active
- Check API key permissions
- Ensure network connectivity to provider APIs

### Import Errors

- Install required packages: `pip install openai google-generativeai`
- Check Python version compatibility

### Rate Limiting

- Implement delays between requests
- Use appropriate max_tokens values
- Consider caching responses

### Provider Selection

- Ensure at least one provider is configured
- Check `default_provider` setting
- Use "auto" to let the system choose
- Azure OpenAI requires all three: API key, endpoint, and deployment name

### Azure OpenAI Specific Issues

- **"Endpoint not configured"**: Ensure `azure_openai_endpoint` is set correctly (full URL)
- **"Deployment not found"**: Verify deployment name matches what you created in Azure Portal
- **"Authentication failed"**: Check API key is correct and not expired
- **"Model not available"**: Ensure the model is deployed in your Azure OpenAI resource
- **API version errors**: Update `azure_openai_api_version` to a supported version

## Changelog

### 1.0.0 (2025-12-13)
- Initial release
- Gemini and ChatGPT support
- Azure OpenAI (Microsoft Copilot) support
- Workflow enhancement and generation
- Log analysis
- Admin panel integration
- Multi-provider support with auto-selection
