# 🛒 faneX-ID Standard Integrations

[![Addon Validation](https://github.com/faneX-ID/integrations/actions/workflows/ci.yml/badge.svg)](https://github.com/faneX-ID/integrations/actions/workflows/ci.yml)

> **Official System Integrations** for [faneX-ID Core](https://github.com/faneX-ID/core). 🔐

This repository hosts the certified, battery-included integrations that ship (or are available) for faneX-ID.

---

## 📦 Available Integrations

**Total: 23 integrations**

| Name | Version | Description | Capabilities | Requirements |
|------|---------|-------------|--------------|--------------|
| [AI Assistant](ai-assistant/) | 1.0.0 | AI-powered assistant integration supporting Gemini, ChatGPT, and Azure OpenAI... | `ai`, `workflow`, `automation`, `query` | openai>=1.0.0, google-generativeai>=0.3.0, requests>=2.28.0 |
| [Bitwarden](bitwarden/) | 1.0.0 | Integration with Bitwarden password manager API for managing organizations, m... | `password_management`, `secrets_management` | requests>=2.28.0 |
| [Calendar Sync](calendar-sync/) | 1.0.0 | Sync employee events, onboarding dates, and important dates with Google Calen... | `automation`, `scheduler` | requests>=2.28.0 |
| [Cloudflare](cloudflare/) | 1.0.0 | Integration for Cloudflare API. Manage DNS records, zones, and Cloudflare ser... | `automation`, `dns_management`, `api_gateway` | cloudflare>=2.11.0 |
| [Discord Bot](discord_bot/) | 1.0.0 | Integration for Discord bots. Send messages and interact with Discord servers... | `automation`, `notification`, `bot` | discord.py>=2.3.0 |
| [Generic Webhook](webhook-generic/) | 1.0.0 | Send HTTP requests to any webhook endpoint for custom integrations and automa... | `webhook`, `automation` | - |
| [Home Assistant](homeassistant/) | 1.0.0 | Integration for controlling and monitoring Home Assistant devices and service... | `automation`, `monitoring`, `api_gateway` | requests>=2.28.0 |
| [Jira Integration](jira-integration/) | 1.0.0 | Create and manage Jira tickets for employee onboarding, IT requests, and work... | `automation`, `data_management` | requests>=2.28.0, jira>=3.5.0 |
| [Mattermost](mattermost/) | 1.0.0 | Integration with Mattermost team communication platform via REST API. | `communication`, `team_collaboration` | requests>=2.28.0 |
| [Microsoft Graph Exchange](microsoft-graph-exchange/) | 1.0.0 | Microsoft Graph integration for Exchange Online email and calendar management... | `email`, `calendar` | requests>=2.28.0 |
| [Microsoft Teams](microsoft-teams/) | 1.0.0 | Send notifications and alerts to Microsoft Teams channels via webhooks. | `notification`, `communication` | requests>=2.28.0 |
| [Microsoft Teams Bot](microsoft_teams_bot/) | 1.0.0 | Integration for Microsoft Teams bots. Send messages and interact with Teams c... | `automation`, `notification`, `bot` | botbuilder-core>=4.15.0 |
| [NetBox](netbox/) | 1.0.0 | Integration for managing NetBox IPAM and DCIM via REST API. | `automation`, `monitoring`, `api_gateway` | requests>=2.28.0 |
| [Nextcloud](nextcloud/) | 1.0.0 | Integration with Nextcloud file sharing and collaboration platform via WebDAV... | `file_sharing`, `collaboration` | requests>=2.28.0 |
| [Otobo](otobo/) | 1.0.0 | Integration with Otobo ticket system (Open Source). Create and manage tickets... | `ticketing`, `automation` | requests>=2.28.0 |
| [Slack Bot](slack_bot/) | 1.0.0 | Integration for Slack bots. Send messages and interact with Slack workspaces. | `automation`, `notification`, `bot` | slack-sdk>=3.20.0 |
| [Slack Notifications](slack-notifications/) | 1.0.0 | Send notifications and alerts to Slack channels via webhooks or API. | `notification`, `communication` | requests>=2.28.0 |
| [SMTP Email Service](smtp-standard/) | 1.0.0 | Standard SMTP Email integration for sending notifications. | `mail_provider` | aiosmtplib>=5.0.0 |
| [SoSafe](sosafe/) | 1.0.0 | Integration with SoSafe security awareness platform API. Note: Public API doc... | `security`, `awareness` | requests>=2.28.0 |
| [Telegram Bot](telegram/) | 1.0.0 | Integration for Telegram bots. Send and receive messages through Telegram. | `automation`, `notification`, `bot` | python-telegram-bot>=20.0 |
| [Vaultwarden](vaultwarden/) | 1.0.0 | Helper integration for Vaultwarden (self-hosted Bitwarden alternative). This ... | `password_management`, `secrets_management` | - |
| [VMware ESXi](esxi/) | 1.0.0 | Integration for managing VMware ESXi hosts and virtual machines via vSphere R... | `automation`, `monitoring`, `api_gateway` | requests>=2.28.0 |
| [Wiki.js](wiki-js/) | 1.0.0 | Integration with Wiki.js API for managing content, users, and pages. | `documentation`, `content_management` | requests>=2.28.0 |

## 📂 Repository Structure

*   `📜 addons.json` — The central index file read by faneX-ID Core.
*   Each integration directory contains:
    *   `manifest.json` — Integration metadata and configuration schema
    *   `integration.py` or `integration.ps1` — Implementation file
    *   `README.md` — Integration documentation

## 🚀 Getting Started

To utilize these integrations, ensure your faneX-ID instance is configured to use this repository (default setting).

## 🤝 Contributing

We welcome contributions! Please refer to the [🧩 Integration Development Guide](https://github.com/faneX-ID/core/blob/main/INTEGRATION_DEV_GUIDE.md) before submitting Pull Requests.

## 📝 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

---

*Last updated: 2025-12-14 07:20:11 UTC*