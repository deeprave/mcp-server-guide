# MCP Document Templates

> NOTE: These are templates, not "live" documents.
> They're representative of the prompts I use, but your preferences and development workflow may be significantly different from my own.

This directory contains a number of template prompts that you can copy to your server's document root, edit as you see fit according to your developement preferences, requirements,  expections and spoken language, link them into the MCP to serve as prompts.

Prompt documents in your docroot are shared across all projects in which you use this MCP. However the patterns defined per0project determine which of the prompt documents apply to your current project.

## Prompt Categories

When a new project is first initialised, the following prompt categories are pre-defined, the first three being layers:

- **guide** - These are general guidelines applicable to any project. Details the appoach, method and the development cycle you use.
- **lang** - Language specific guidelines. Common practices for your programming language(s), frameworks, best practices, pitfalls, style preferences and so on. These guidelines would apply to any project using the specific language or framework.
- **context** - This document describes the current project, usually consisting of unique information such as a project identifier to your bug tracker or issue management software, repository url, author information and so on.
- **prompt** -  Finally, this category defines documents that are automatically picked up and used during the various development phases:

  - _discussion_: `guide --discuss`
  - _planning_: `guide --plan`
  - _implementation_: `guide --implement`
  - _check_: `guide --check`
  - _status_: `guide --status` This is not not a development phase, but it is designed to determine and display the currently active phase

None of these automatically created categories are required, only recommended, and can be removed or renamed to suite.
The `prompt` category is the only one that the MCP will use on transitioning between phases, but if the category or prompt document does not exist, then pre-canned text is displayed instead.

## Prompt Collections

**Colllections** are category groups.

They are a convenient way to include and combine groups of prompt categories into a single document.

For example, you can create a category "default" with:
```
[@|/]guide --category --add --name "default"
```