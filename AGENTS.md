# Issabel PBX Renovation - AI Agent Instructions

Welcome to the **ISABELL-RENOVAR** project workspace. This file (`AGENTS.md`) provides essential context, architectural guidelines, and rules for AI coding agents operating within this repository. 

## 1. Project Overview
This repository contains the source code for an **Issabel PBX** environment (or a fork/customization of it). Issabel is an open-source Unified Communications software based on Asterisk and a fork of Elastix. The goal of this project is to renovate, maintain, and expand its capabilities.

**Important Note on Call Center Module:**
This project utilizes the community-maintained Call Center module for Issabel 5. When interacting with or modifying call center functionalities (campaigns, agents, dialer, reports, etc.), agents must bear in mind the architecture and codebase guidelines of this specific module:
*   [ISSABELPBX/callcenter-issabel5 GitHub Repository](https://github.com/ISSABELPBX/callcenter-issabel5)

## 2. Technology Stack
Agents working on this codebase must be familiar with the following:
*   **Backend:** PHP (Legacy and modern, often 5.4 to 8.x depending on the OS base), Bash/Shell scripting.
*   **Frontend:** HTML, CSS, JavaScript (jQuery is prevalent), Smarty Templating Engine (`.tpl` files).
*   **Telephony Engine:** Asterisk (Dialplans, AGI scripts in PHP/Python, AMI/ARI).
*   **Database:** MariaDB / MySQL / SQLite (Internal configurations).
*   **OS Environment:** Linux (historically CentOS 7, migrating to Rocky Linux / AlmaLinux 8/9).

## 3. Directory Structure Guide
Understanding the layout is critical for implementing correct changes:
*   `modules/` - Contains the core functional modules of the Issabel GUI. Each module usually has an `index.php`, `themes/` (with `.tpl` files), and `libs/` (with `paloSanto*.class.php` models).
*   `themes/` - Global GUI themes and assets (CSS, JS, images, Smarty templates).
*   `libs/` - Global library files and core classes (e.g., database connection wrappers, authentication classes).
*   `admin/` - FreePBX legacy integration / administration panel.
*   `pbxapi/` & `rest.php` - API endpoints for external integrations.
*   `lang/` - Localization and internationalization files.
*   `configs/` - Configuration files.

## 4. Coding Conventions & Best Practices

### PHP & Legacy Code
*   **Framework Awareness:** Issabel uses a custom legacy modular framework (originally from Elastix). Do NOT assume modern MVC frameworks (like Laravel or Symfony) are available.
*   **Database Access:** Utilize the built-in database wrapper classes (e.g., `paloSantoDB`). Be incredibly careful to prevent SQL injection. Always sanitize inputs and use parameterized queries where the wrapper supports it, or `mysql_real_escape_string` / `PDO::quote` equivalents used in the project.
*   **Smarty Templates:** Separate UI logic from business logic. Pass variables to Smarty and handle HTML generation in `.tpl` files.

### Asterisk & Telephony
*   When editing Dialplans (`extensions_custom.conf`, etc.), ensure contexts do not overlap dangerously.
*   When creating AGI scripts, ensure proper permissions and execution environments (`#!/usr/bin/php -q` or `#!/usr/bin/env python`).

### Security (CRITICAL)
*   **Input Validation:** PBX systems are high-value targets for hackers. Validate and sanitize ALL user inputs (GET, POST, Cookies, API payloads).
*   **Command Injection:** Avoid using `exec()`, `shell_exec()`, or `system()` unless absolutely necessary. If required, use `escapeshellarg()` strictly.
*   **XSS Protection:** Escape outputs in Smarty templates and raw PHP outputs.

## 5. Agent Operational Rules
1.  **Read Before Write:** Always use `grep`, `glob`, and `read` to check how similar modules or features are implemented before writing new code. Conform to the existing style.
2.  **Preserve Compatibility:** This is a legacy-heavy system. Ensure changes do not break existing modules or FreePBX integrations.
3.  **No Hallucinated Libraries:** Do not include Composer packages or external libraries without verifying they exist or explicitly asking the user for permission to install them.
4.  **Logging & Debugging:** When modifying complex logic, integrate with Issabel's existing logging mechanisms or Asterisk's logger to facilitate debugging.

## 6. Common Agent Tasks
*   **Refactoring Modules:** Updating old PHP syntax to modern standards, removing deprecations.
*   **Theme Renovation:** Modifying CSS/JS within `themes/` to modernize the UI.
*   **API Extension:** Adding new RESTful routes in `pbxapi/`.
*   **Asterisk Integration:** Modifying PHP scripts that interact with the Asterisk Manager Interface (AMI).

---
*Note to Agents: When invoked in this workspace, implicitly load these rules into your context and apply them to all your actions.*