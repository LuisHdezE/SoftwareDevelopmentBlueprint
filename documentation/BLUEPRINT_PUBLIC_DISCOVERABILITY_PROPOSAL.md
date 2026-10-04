# Blueprint Public Discoverability Proposal

## Status

Proposal-stage conditional capability.

This proposal does not alter stable Blueprint 0.5.4 and does not alter the frozen 0.5.5-dev release candidate.

## Purpose

Blueprint currently governs architecture, security, API quality, interface delivery and release evidence, but does not explicitly govern whether public product/marketing surfaces can be discovered through modern search.

Public Discoverability closes that gap for:

1. traditional search engines;
2. AI-powered search and answer engines;
3. ecommerce product discovery.

The capability is intentionally excluded from private/admin surfaces.

## Applicability semantics

Public Discoverability uses Blueprint's conditional applicability semantics:

```text
No PUBLIC_INDEXABLE surface
  -> Public Discoverability = NOT_APPLICABLE

One or more PUBLIC_INDEXABLE surfaces
  -> Public Discoverability = REQUIRED
  -> discoverability_ready must PASS before Release
```

Therefore `CONDITIONAL` does **not** mean optional when applicable.

A public marketing landing, storefront, public product/category page or equivalent surface intentionally classified as `PUBLIC_INDEXABLE` cannot be considered release-complete while its required discoverability evidence is missing.

### Growth is a separate adoption decision

This proposal intentionally does not make social or paid acquisition mandatory.

The following remain optional/opt-in capabilities unless separately adopted:

- Facebook or Instagram presence;
- organic social publishing;
- content calendars;
- paid acquisition;
- Meta Ads;
- Google Ads;
- campaign operations.

A consumer may complete and release its public product without adopting those Growth operations. That does not waive mandatory Discoverability for its `PUBLIC_INDEXABLE` surfaces.

## Capability name

`Public Discoverability`

Specialist:

`Search & AI Discoverability`

This specialist is conditional and is not part of the eleven-agent core.

## Surface classification

Every applicable route should be classified before discoverability work:

### PUBLIC_INDEXABLE

Public and intentionally discoverable.

Examples:

- home/landing;
- public service pages;
- category pages;
- product pages;
- public contact/store pages;
- useful public compatibility/help content.

### PUBLIC_NO_INDEX

Publicly reachable but intentionally not indexed.

Examples may include:

- cart;
- checkout;
- login;
- registration;
- internal site search;
- low-value filter/facet combinations.

### PRIVATE

Authenticated/authorized surfaces not intended for anonymous discovery.

Examples:

- admin;
- dashboard;
- account;
- order history;
- internal reports.

`robots.txt` and `noindex` are not security controls.

## Traditional search contract

For each PUBLIC_INDEXABLE surface, evaluate when applicable:

- crawler access;
- index policy;
- canonical URL;
- title;
- description;
- semantic headings;
- crawlable internal links;
- sitemap inclusion;
- structured data;
- product/variant semantics;
- image accessibility;
- performance;
- redirects and real 404 behavior;
- duplicate/faceted-navigation control.

## AI search contract

AI discoverability adds:

- explicit AI crawler policy;
- entity/business identity clarity;
- factual product/service clarity;
- answer-friendly public content;
- citation-friendly page structure;
- factual consistency between visible content and structured data;
- AI-referral measurement.

## OpenAI search discovery

Current OpenAI documentation distinguishes:

- OAI-SearchBot for ChatGPT search discovery;
- GPTBot for content that may be used to improve/train foundation models;
- ChatGPT-User for certain user-triggered fetches.

OAI-SearchBot and GPTBot policy are independent.

A consumer may deliberately allow search discovery while opting out of GPTBot.

Current reference:
- https://developers.openai.com/api/docs/bots
- https://help.openai.com/en/articles/12627856-publishers-and-developers-faq

The implementation must use current provider documentation rather than hardcoding crawler version strings.

## ChatGPT referral measurement

Current OpenAI publisher guidance states that ChatGPT search referrals include:

`utm_source=chatgpt.com`

This may be measured separately from traditional organic search.

The capability treats measurement as evidence, not as a ranking promise.

## Ecommerce

For ecommerce PUBLIC_INDEXABLE product pages, add explicit product semantics.

Typical public facts include:

- product name;
- description;
- brand;
- SKU/identifier;
- model compatibility;
- condition;
- price;
- currency;
- availability;
- images;
- shipping;
- returns;
- seller/store identity.

Google currently documents Product/Offer and merchant-listing structured data for purchasable products and recommends initial-HTML product markup for stronger shopping crawl reliability.

References:
- https://developers.google.com/search/docs/appearance/structured-data/merchant-listing
- https://developers.google.com/search/docs/appearance/structured-data/product-variants

## ChatGPT product discovery

OpenAI currently documents Agentic Commerce product feeds for catalog discovery in ChatGPT.

Product feeds can provide structured, refreshed catalog facts such as:

- identifiers;
- titles;
- descriptions;
- URLs;
- images;
- availability;
- price;
- brand;
- variants and additional fulfillment attributes.

This integration is optional and subject to current provider onboarding/eligibility.

References:
- https://developers.openai.com/commerce
- https://developers.openai.com/commerce/specs
- https://developers.openai.com/commerce/guides/get-started

A product feed does not replace crawlable, useful product pages.

## Discoverability gate proposal

Proposed conditional gate:

`discoverability_ready`

Scope:

`public_indexable_surface`

It is NOT a stable gate in this proposal.

Within this proposal lane, however, it is release-blocking whenever Public Discoverability is applicable. If there are no `PUBLIC_INDEXABLE` surfaces, the capability and gate are `NOT_APPLICABLE` rather than FAIL.

Suggested evidence:

### Search

- surface classification exists;
- crawl/index policy is correct;
- canonical is correct;
- sitemap behavior is correct;
- metadata is unique/appropriate;
- semantic content exists;
- internal links exist;
- structured data validates where applicable;
- important public facts are crawlable;
- no accidental duplicate/indexable noise is introduced.

### AI Search

- OAI-SearchBot policy is explicitly decided;
- GPTBot policy is independently decided;
- WAF/CDN does not accidentally contradict approved crawler policy;
- business/entity facts are explicit;
- important product/service facts are clear;
- factual content and machine-readable data agree;
- AI-search referrals can be measured when analytics exists.

### Ecommerce

- product facts map to authoritative state;
- price/currency/availability agree with the product domain;
- variants have stable identity;
- Product/Offer data is valid where applicable;
- AI product-feed applicability is explicitly decided.

## Framework neutrality

Public Discoverability does not require Next.js or any other specific framework.

The requirement is crawlable, semantically useful public content.

Suitable approaches may include:

- server-rendered templates;
- SSR;
- static generation;
- pre-rendering;
- other evidence-backed delivery models.

## What this proposal does not promise

Blueprint must never promise:

- Google ranking;
- ChatGPT citation;
- inclusion in a shopping result;
- rich-result display;
- AI-product-feed acceptance.

It governs eligibility, technical quality, clarity and evidence, not external ranking decisions.
