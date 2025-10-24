Comprehensive Onboarding Guide: Integrating the Serena Coding Agent

Welcome to Serena, a transformative coding agent toolkit designed to turn your Large Language Model (LLM) into a fully-featured development partner that works directly on your codebase. At its core, Serena equips LLMs with an IDE-like semantic understanding of your projects, moving beyond simple text analysis to grasp code at a symbolic level. For developers, this translates to significantly enhanced agent performance, greater token efficiency, and the ability to perform precise, complex code manipulations with confidence. Developers consistently report that integrating Serena is a game-changer, providing an enormous productivity boost, especially when navigating and manipulating complex projects.

This guide provides a clear, step-by-step path for installing, configuring, and integrating the Serena toolkit into your development environment. Our objective is to ensure you have a smooth and successful onboarding experience, empowering you to leverage Serena's full potential from day one.


--------------------------------------------------------------------------------


1.0 Foundational Concepts: Understanding the Serena Ecosystem

To effectively configure, use, and troubleshoot Serena, it is crucial to first understand its core architectural components. Grasping these foundational concepts will provide you with the strategic insight needed to tailor the toolkit to your specific workflows and development environments.

* Model Context Protocol (MCP) Server: The MCP Server is the central integration bridge of the Serena ecosystem. It connects Serena's powerful semantic tools to a wide variety of clients, including IDEs (like VSCode or Cursor), terminal-based assistants (like Claude Code), and local GUIs (like OpenWebUI).
* Language Server Protocol (LSP): Serena leverages the widely adopted Language Server Protocol (LSP) to achieve a deep, symbolic understanding of your codebase. This is the same technology that powers modern IDEs, allowing Serena to move beyond simplistic text searches and perform operations based on the actual structure and relationships within your code. This symbolic approach is what elevates Serena beyond simple text-based search (like grep) or find-and-replace, enabling true agentic refactoring and comprehension.
* Contexts: A "context" (e.g., ide-assistant, desktop-app) is a pre-defined configuration that tailors Serena's tools and system prompts for a specific client or environment. For instance, the ide-assistant context is optimized for integration with IDEs, while the desktop-app context is designed for standalone applications like Claude Desktop. The desktop-app context is the default if no other is specified. You will select the appropriate context (e.g., --context ide-assistant) during the client integration step to ensure Serena is perfectly configured for your chosen tool.
* Modes: A "mode" (e.g., planning, editing) dynamically refines Serena's behavior for a specific task. Modes can adjust the available tools and system prompts to focus the agent on a particular objective, such as planning a complex change versus directly implementing code edits. Multiple modes can be active simultaneously and can be switched dynamically during a session.

With these core concepts in mind, you are ready to prepare your local environment for installation.


--------------------------------------------------------------------------------


2.0 Prerequisites: Preparing Your Environment

A correct initial setup is the foundation for a successful and seamless integration. This section provides a quick but critical checklist to ensure your system is ready before you proceed with the installation.

2.1 Install uv

Serena is managed by uv, a fast Python package installer and resolver. You must have uv installed on your system before proceeding with the next steps.

2.2 Version Control Best Practices

To allow Serena to effectively track its changes and for you to easily review its work, it is highly recommended to start any code generation task from a clean git state.

For Windows users, to ensure Serena's git diff analysis is always accurate, we strongly recommend setting a global Git configuration to handle line endings automatically. This prevents false-positive changes from cluttering the agent's view of its work. Run the following command in your terminal to set this configuration globally:

git config --global core.autocrlf true


Once your environment is properly prepared, you can proceed with the core installation and server setup.


--------------------------------------------------------------------------------


3.0 Core Setup: Running the Serena MCP Server

This section provides the central guide to getting the Serena MCP server—the engine that powers the toolkit—up and running. There are several flexible methods to launch the server, allowing you to choose the one that best fits your preference and development environment.

3.1 Recommended Method: Using uvx

The simplest method for running the latest version of Serena directly from its repository without a local clone is to use uvx. This command ensures you are always using the most up-to-date version with minimal setup.

uvx --from git+https://github.com/oraios/serena serena start-mcp-server


3.2 Local Installation

For users who prefer to have a local copy of the repository, follow these steps:

1. Clone the repository:
2. Navigate into the directory:
3. Run the server:
  * Note: If running this command from outside the serena directory, you must specify the path using the --directory flag: uv run --directory /abs/path/to/serena serena start-mcp-server

3.3 Alternative Methods: Docker and Nix

For users who prefer containerized or reproducible environments, Serena supports both Docker and Nix.

Method	Command and Key Considerations
Docker	docker run --rm -i --network host -v /path/to/your/projects:/workspaces/projects ghcr.io/oraios/serena:latest serena start-mcp-server --transport stdio<br><br>The -v flag mounts your local projects directory into the container, allowing Serena to access your codebase.<br><br>Warning: Docker support is currently experimental and has several known limitations.
Nix	nix run github:oraios/serena -- start-mcp-server --transport stdio<br><br>Note: This requires the nix-command and flakes features to be enabled in your Nix configuration.

3.4 Understanding Server Transport Modes

By default, Serena uses stdio (standard input/output) for communication. In this mode, the client application (like Claude Code) uses the command you provide in its configuration to start and manage the Serena server process for each session.

Alternatively, you can run the server in Streamable HTTP mode. In this configuration, you start the server manually, and the client connects to it via a URL. This gives you direct control over the server's lifecycle.

To start the server in this mode, use the --transport streamable-http flag:

uv run serena start-mcp-server --transport streamable-http --port 9121


You would then configure your client to connect to the provided URL, such as http://localhost:9121/mcp.

With the server running, the next step is to integrate it with your preferred developer client.


--------------------------------------------------------------------------------


4.0 Client Integration Guides

Once the Serena MCP server is running, you must connect it to a client application. This section provides specific, step-by-step instructions for integrating Serena with popular development tools and environments.

4.1 Claude Code Integration (Recommended)

Using Serena with Claude Code is a powerful combination that significantly enhances Claude's native capabilities, making it both more effective and more cost-efficient.

1. Navigate to your project's root directory in your terminal.
2. Use the claude mcp add command with the following structure:
3. For the recommended uvx method, the complete command is:
4. Important Note: Claude Code versions v1.0.52 and later automatically read Serena's initial instructions to understand how to use its tools. If you are using an older version, you may need to explicitly ask Claude to "read Serena's initial instructions" at the beginning of a new session to ensure proper tool usage.

4.2 Claude Desktop Integration

To set up Serena with the Claude Desktop application on Windows and macOS, follow these steps:

1. In the Claude Desktop application, navigate to File > Settings > Developer > MCP Servers > Edit Config.
2. This action will open the claude_desktop_config.json configuration file in your default text editor.
3. Add the following serena object inside the mcpServers block. Choose the appropriate command and args based on your chosen installation method (e.g., uvx or local).
  * Note: The command should be the absolute path to your uv or uvx executable. If uv is in your system's PATH, you may be able to use uv and uvx directly, but providing the full path is the most reliable method.
  * When specifying paths on Windows, remember to either use forward slashes (/) or escape backslashes (\\).
4. Critical Warning: To apply the changes, you must fully quit the Claude Desktop application. Simply closing the window may minimize it to the system tray; ensure the process is completely terminated before relaunching.

4.3 Other Integrations

Serena's use of the MCP standard allows it to integrate with a wide range of other tools.

* Terminal Clients (Codex, Gemini-CLI, etc.): Serena works well with terminal-based clients. These integrations may require a specific context, such as --context codex, to ensure compatibility. For example, to configure Codex, add the following to your ~/.codex/config.toml file:
* IDE-Based Clients (Cursor, Cline, etc.): Serena can be integrated into any MCP-compatible client, including IDE extensions and standalone IDEs. For these integrations, it is highly recommended to use the --context ide-assistant to boost their performance with Serena's symbolic operations.
* Local GUIs (Jan, OpenWebUI, etc.): Open-source graphical interfaces like Jan and OpenWebUI support MCP servers, enabling you to connect Serena to almost any LLM, including locally hosted models.

After successfully integrating Serena with your client, the next step is to activate and prepare a specific project for agentic work.


--------------------------------------------------------------------------------


5.0 Project Workflow: Activation and Optimization

Properly activating and indexing a project is a crucial step in the Serena workflow. This process effectively "teaches" Serena about the specific codebase it will be working on, which is essential for achieving optimal performance, speed, and accuracy.

5.1 Activating a Project

There are two primary methods for activating a project within Serena.

* At Startup: For projects you work on frequently, you can configure Serena to activate them automatically at launch. Add the --project <path_or_name> flag to the start-mcp-server command in your client's configuration.
* Dynamically: The recommended and most flexible method is to ask the LLM to activate a project using a natural language command during a session. Provide either the absolute path or the project's known name (which defaults to its directory name).

5.2 Indexing for Performance

To unlock maximum performance in large or complex codebases, indexing is a critical optimization step. This process pre-analyzes the project's symbols and structure, which significantly accelerates Serena's tools and prevents slowness or delays on the first tool use in a session.

To index your project, run the following command from the project's root directory:

uvx --from git+https://github.com/oraios/serena serena project index


With your project activated and optimized, you can now apply advanced strategies to get the most out of the toolkit.


--------------------------------------------------------------------------------


6.0 Best Practices for Effective Use

Following these expert recommendations will help you elevate your usage of Serena from basic operations to proficient, agentic-style development. These practices are designed to maximize Serena's effectiveness and ensure reliable, high-quality results.

6.1 Leveraging Onboarding and Memories

When Serena works on a project for the first time, it performs an initial onboarding process to familiarize itself with the project's structure and key components. During this process, it creates "Memories"—files stored in the .serena/memories/ directory of your project. The agent can read these memories in future sessions to rapidly regain context.

Users can and should review, edit, or even manually add new memories to this directory. Curating these memory files is a powerful way to guide Serena's understanding and improve its long-term performance on a project.

6.2 Preparing Your Codebase

Serena's performance is directly influenced by the quality and structure of the code it works with.

* Well-Structured Code: Serena performs best on well-structured, modular codebases. For dynamically typed languages, adding type annotations is highly beneficial and improves the accuracy of its semantic analysis.
* Automated Testing & Linting: Serena relies on the output from test suites, logs, and linters to assess the correctness of its actions and to self-correct when issues arise. A project with good test coverage and clear linting rules is much easier for Serena to work with.
* Clean Git State: Always start a task from a clean git state. This not only makes it easier for you to review the changes but also allows the agent to use git diff to track its own progress and make more informed decisions.

6.3 Prompting and Context Management

For non-trivial tasks, a structured approach to prompting yields the best results.

* Plan, Then Implement: We recommend a two-step process for complex tasks. First, dedicate a session to planning and code exploration, allowing Serena to read relevant code and build context. Once a clear plan is established, begin the implementation in a new, fresh session.
* Manage Long-Running Tasks: On long tasks that may approach the LLM's context limit, use Serena's dedicated tool to create a summary memory of the current progress. You can then start a new conversation and simply instruct Serena to read that memory to pick up exactly where it left off, with a full and fresh context window.

Finally, effective monitoring is key to understanding and troubleshooting Serena's operations.


--------------------------------------------------------------------------------


7.0 Monitoring and Support

Effective monitoring provides crucial insight into Serena's operations, helping you understand its tool usage and troubleshoot any issues that may arise. Serena offers two primary methods for accessing session logs.

* Web-Based Dashboard: Enabled by default, the dashboard is accessible on your local machine (e.g., http://localhost:24282/dashboard/index.html). It provides a real-time view of logs and tool usage statistics. Crucially, it also includes a button to reliably shut down the Serena agent.
* GUI Tool: This is an alternative logging tool that is disabled by default. It is primarily supported on Windows and may not be available on other operating systems.

A common pitfall with client-managed servers is the creation of "zombie processes" when a client fails to properly terminate the server. To avoid this, we've built a reliable shutdown method directly into the web dashboard, giving you a consistent way to view active sessions and prevent this issue.
