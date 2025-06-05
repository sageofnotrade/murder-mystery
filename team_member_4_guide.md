# Team Member 4 - Milestone 4 Task Guide

## Your Tasks Overview

| Task ID | Title | Estimate | Dependencies |
|---------|-------|----------|-------------|
| AI-010 | Advanced agent tuning & prompt engineering | 8h | AI-009 |
| DB-006 | Data migration & backup scripts | 4h | DB-004 |
| TEST-008 | End-to-end polish & deployment testing | 8h | AI-010, DB-006 |
| **Total** | | **20h** | |

## Task Details and Implementation Guide

### AI-010: Advanced agent tuning & prompt engineering

#### Description
Refine and optimize AI agent prompts and parameters for improved narrative quality, coherence, and player adaptation. Experiment with prompt engineering and model settings for best results.

#### Implementation Steps
1. **Review current agent prompts and outputs**
   - Identify areas for improvement in narrative, suspect, and clue generation.
2. **Research prompt engineering techniques**
   - Explore best practices for LLM prompt design and tuning.
3. **Experiment and iterate**
   - Test different prompt structures, temperature, and model settings.
   - Collect feedback from team and testers.
4. **Implement improvements**
   - Update agent code and prompt templates.
5. **Document changes**
   - Summarize improvements in PRs and docs.

#### Resources
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [PydanticAI Docs](https://github.com/pydantic/pydanticai)

---

### DB-006: Data migration & backup scripts

#### Description
Develop scripts for data migration and backup, ensuring safe upgrades and rollbacks for Supabase and Redis data. Automate regular backups and document the process.

#### Implementation Steps
1. **Review current data models and storage**
   - Identify tables/keys requiring migration or backup.
2. **Design migration/backup strategy**
   - Plan for safe, reversible migrations and regular backups.
3. **Implement scripts**
   - Write SQL and Python scripts for migration and backup.
   - Test on staging data.
4. **Automate backups**
   - Schedule regular backups using cron or CI workflows.
5. **Document process**
   - Update docs with migration/backup instructions and recovery steps.

#### Resources
- [Supabase Migration Docs](https://supabase.com/docs/guides/database/migrations)
- [PostgreSQL Backup Guide](https://www.postgresql.org/docs/current/backup-dump.html)
- [Redis Backup Docs](https://redis.io/docs/management/backup/)

---

### TEST-008: End-to-end polish & deployment testing

#### Description
Develop and run comprehensive E2E tests covering all major user flows, polish features, and deployment scenarios. Use Cypress and custom scripts for full coverage.

#### Implementation Steps
1. **Review all polish/deployment features**
   - Identify critical paths and edge cases.
2. **Write E2E test scripts**
   - Cover login, board, narrative, deployment, and error scenarios.
3. **Automate E2E tests in CI**
   - Ensure tests run on PRs and main branch merges.
4. **Review and fix issues**
   - Address any failures or polish gaps found during testing.
5. **Document test coverage**
   - Update docs with E2E scenarios and results.

#### Resources
- [Cypress Documentation](https://docs.cypress.io/)
- [Testing Vue Applications](https://vuejs.org/guide/scaling-up/testing.html)

---

## Testing Your Work
- Run the backend and frontend development servers.
- Test all agent, migration, and E2E features.
- Write and run unit/E2E tests for all new code.
- Verify migration safety and deployment reliability.

## Communication
If you encounter any blockers or have questions:
- Post in the #milestone-4 Slack channel
- Tag the project lead for urgent issues
- Document any design decisions or assumptions in your PR description

Good luck with your tasks! Remember to commit your work regularly and create pull requests for review.

---

*This guide will be updated as Milestone 4 progresses. Good luck!*