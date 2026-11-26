# BF-OT-013 - ChatGPT adapter proposal

## Target surface

This order prepares a manual ChatGPT Projects kit. Projects support project-specific instructions and reference files. They fit Luis's current personal Plus account better than a new custom GPT: current OpenAI Help Center guidance says new GPT creation is unavailable on personal accounts, including Plus.

The generator creates a review-only kit with:
- CHATGPT_PROJECT_INSTRUCTIONS.md for copy/paste into Project settings.
- Three knowledge files containing the exact 12 canonical role contracts, 16 materialized skills, and text resources referenced by those skills.
- README-SETUP.md and blueprint-adapter-manifest.json with the exact source commit, resource mapping, and SHA-256 hashes.

Three knowledge files stay below the current Plus Project file limit of 25. The limit and availability may change; check the destination UI at adoption time.

## Platform boundary

Project instructions and attached files inform responses; they do not enforce hard approvals, execute packaged scripts, authenticate agent identity, or provide independent multi-agent execution. A role-specific response in one conversation is not independent QA, Security, or Auditor review. Keep independent evidence requirements explicit.

The adapter does not create or edit a ChatGPT Project, GPT, API skill, connector, credential, or account setting. It does not automatically sync when canonical files change. A fresh kit must be generated and reviewed for each source revision.

No code is installed into consumers. No external change, merge, deployment, or release is part of this proposal.

## Run the structural regression

    python scripts/test-chatgpt-project-adapter.py

The test validates canonical preservation, project-kit boundaries, determinism, hashes, unsafe paths, and overwrite rejection. It does not prove ChatGPT runtime behavior; only a manually configured project can be evaluated in the product.
