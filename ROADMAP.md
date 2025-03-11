Overview
This project aims to build a Django-based, multi-user system that manages Clients and Projects, parses network device files, organizes structured inventory data, and generates AI-assisted reports. The solution leverages CrewAI—an AI-empowered workflow comprising multiple specialized agents—to parse device configurations, generate reports based on project intent, and streamline collaboration. By following a modular, well-documented, and scalable design, the application can easily adapt to additional device types, new parsing rules, and future enhancements.

1. Initial Project Setup and Structure
Django Initialization

Initialize a Django project using best practices for multi-user (e.g., separate well-defined permission model).
Create separate apps for each functional domain:
clients (Client management)
projects (Project management per client)
parsers (Device file uploads and parsing logic)
inventory (Stores all parsed configurations)
reports (AI-driven report generation using CrewAI and exports)
Setup PostgreSQL Database

Poetry for package management

Provision PostgreSQL and configure Django settings for secure connections.
Establish a schema that can handle:
Client/Project data
Inventory tables (interfaces, ACLs, VRFs, etc.)
Parsed device data storage
Prompt Suggestions for CursorAI

Project Initialization Prompt
“Create a new Django project named VarAI with multiple apps (clients, projects, parsers, inventory, reports). Use a PostgreSQL backend. Provide boilerplate settings for multi-user support and demonstrate how to configure environment variables for DB connections.”

Database Setup Prompt
“Generate Django model boilerplate for the following concepts: Client, Project, Device, and InventoryItem. Ensure that each model has necessary foreign keys, standard fields (timestamps, created_by), and meta classes for clean admin representation.”

2. Data Models and Schema Design
Client Models

Fields: Name, Industry, Primary Contacts, Secondary Contacts, Web Pages, Notes
Project Models

Fields: Name, Intent, Created Date, Status (e.g., Active, Complete)
Linked to a Client via ForeignKey
Distinguish between general and split-off projects
Device Models

Fields: Device Name, Model, Device Type, Firmware, Interface Count, Route Count, ACL Count, SFP Count, IPSEC details, Routing Protocols
Inventory Models

Tables: Interfaces (L2/L3 attributes), ACL/Firewall rules, VRFs, IPSEC tunnels, Routing tables
FileUpload Models

Fields: Uploaded file, detected device type, device name, user overrides, upload timestamps
Prompt Suggestions for CursorAI

Model Design Prompt
“Create Django models for Client, Project, Device, Inventory entities, and FileUpload. For each, define appropriate fields, foreign key links, and any custom save() methods for additional validation. Include indexing for commonly queried fields such as device_name and project references.”

Schema Relationship Prompt
“Generate a diagram or textual representation (using a Python-based library, such as django-extensions graph_models) to visualize the relationships between Client, Project, Device, Inventory, and FileUpload models.”

3. User Interface Development (Frontend)
Client Management UI

CRUD views to manage client data and easily navigate to associated projects.
Project Management UI

Create and manage projects within clients.
Sections for project “Intent” (feeds into AI report generation).
File Upload and Parser UI

Drag-and-drop or file selector interface.
Automatic device identification with a manual override.
Feedback on parsing progress and errors.
Data Visualization and Reporting UI

Structured views for inventory data (interfaces, ACLs, routes, etc.).
Export options for individual tables or a full set of project data.
Prompt Suggestions for CursorAI

Form and View Prompt
“Generate Django CRUD views using class-based views or DRF viewsets for managing Clients, Projects, and FileUploads. Include logic to upload and parse device configuration files.”

Frontend Template Prompt
“Provide example Django template snippets that display a table of Projects for a selected Client, including an ‘Upload Configuration’ button that triggers file parsing.”

4. Device File Parsing and Analysis
Modular Parser Framework

Separate parser classes for: Cisco IOS, Cisco ASA, Cisco Nexus, FortiGate, FortiSwitch, JunOS.
Common interface for extensibility.
Parsing Logic

Automatically detect device type (file contents, filename, or hints).
Extract relevant configuration data (hostnames, firmware, interface details, ACLs, VRFs, etc.).
Parsing Validation

Run validation checks post-parse (e.g., verifying field formats, optional overrides).
Allow manual edits if automated parsing is incomplete.
Prompt Suggestions for CursorAI

Parser Setup Prompt
“Implement an abstract base parser class. Inherit specialized classes (e.g., CiscoIOSParser, FortiGateParser) that handle device-specific parsing. Provide error-handling and logging for invalid lines or unsupported config sections.”

Parsing Validation Prompt
“Generate Python tests using Django’s TestCase or PyTest to verify that each parser correctly extracts and validates device data from sample configuration files. Include coverage for normal, edge, and malformed inputs.”

5. CrewAI Integration (AI-Assisted Workflow)
Crews and Responsibilities

Solutions Architect (Lead Agent): Reviews final outputs before approval.
Parse Engineer: Confirms device matches, deduplicates files, runs parsers, validates output.
Analyst: Creates report outlines from parsed data.
Content Creator: Produces narratives from Analyst outlines.
Editor: Ensures coherence, accuracy, and alignment with the project intent.
CrewAI Workflow

Define each crew agent with distinct tasks and prompts.
Use Langtrace for crew tracking, logs, debugging.
Integrate multiple AI endpoints for redundancy/efficiency.
Prompt Suggestions for CursorAI

Crew Agent Setup Prompt
“Generate a Python class that uses OpenAI or similar API endpoints to simulate each Crew member. Define methods like generate_outline(), create_narrative(), edit_content(), and tie them to respective tasks.”

Workflow Integration Prompt
“Write Django signals or Celery tasks that trigger each Crew member’s AI function in sequence (Parse Engineer → Analyst → Content Creator → Editor → Solutions Architect). Log the process using langtrace for transparency.”

6. AI-Enhanced Reporting Capability
Intent-Based Reporting

Utilize the project’s ‘Intent’ field to shape the AI’s tone and content depth.
Report Generation Workflow

Parse and store structured data.
Analyst generates outlines.
Content Creator and Editor refine the report.
Flexible Export Functionality

Support granular exports (single tables) and comprehensive exports (all project data).
Excel as the primary format; optionally provide PDF/CSV.
Prompt Suggestions for CursorAI

Report Outline Prompt
“Based on the Project model’s ‘Intent’ field and associated Inventory data, generate a structured outline for the final report. Include recommended sections such as Executive Summary, Detailed Findings, and Recommendations.”

Narrative Generation Prompt
“Transform the outline into a detailed narrative. Make sure the language style reflects the project’s ‘Intent’ and remains consistent with standard technical documentation norms.”

7. Operational & Administrative Features
Authentication & Permissions

Django authentication system with permissions or a role-based approach.
Ensure data isolation by tenant (Client-based scoping).
Administrative Dashboards

Django admin pages for viewing & managing data.
Real-time analytics on usage, device parsing counts, project status.
Prompt Suggestions for CursorAI

Permissions Setup Prompt
“Implement role-based access control. Each user role (admin, viewer, editor) has specific permissions on the Clients and Projects. Update the Django admin to limit object visibility by role.”

Analytics Dashboard Prompt
“Generate a Django admin dashboard panel displaying key metrics (e.g., total device parsings, active vs. completed projects, AI report generation tasks). Provide recommended charting code (Matplotlib or Chart.js).”

8. Deployment & Maintenance Strategy
Containerization (Docker & Docker Compose)

Containerize Django, PostgreSQL, and CrewAI services for consistent environments.
Continuous Integration/Deployment (CI/CD)

Automate testing, linting, and deployment through GitHub Actions or equivalent.
Monitoring & Logging

Track AI API usage, parsing accuracy, and system resources.
Log CrewAI workflows for auditing and debugging.
Documentation & Testing

Comprehensive documentation covering setup, AI crew logic, parser modules.
Automated tests (PyTest or Django Test Framework) for critical paths.
Modular Design Principles

Reusable & Maintainable: Parsers, crew definitions, and reporting modules are loosely coupled.
Scalability: Database schema and AI workflow can grow with higher data volumes or expanded tasks.
Prompt Suggestions for CursorAI

Dockerfile and Docker Compose Prompt
“Create Dockerfiles for Django and PostgreSQL. Write a Docker Compose file that orchestrates both services (and any additional AI microservices). Provide health checks for each container.”

CI/CD Pipeline Prompt
“Generate a GitHub Actions YAML config that runs tests, lints the code, and upon success, builds Docker images and deploys to a staging environment. Include rollback steps if deployment fails.”