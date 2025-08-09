# Agentic Desktop: Redefining Support with Intelligent Assistance

**Design POV | Cash App Bitcoin Support**

We have been steadily moving the needle on automation across our customer support and advocate tooling efforts. On the customer side, we've improved routing accuracy, deployed LLM-powered chatbots, and elevated core UX around self-service and escalation paths. On the advocate side, we recently launched the Copilot fast lane escalation feature, a notable step toward simplifying complex cases and reducing handoffs.

These investments have led to improved CSAT, higher automation rates, and increased case resolution efficiency. But the next chapter requires a deeper shift—from AI-assisted tooling to fully **agentic workflows**, where agents operate alongside humans, not behind buttons.

---

## From Assisted to Agentic: A Shift in Workflow Philosophy

Much of what we've built so far falls under the umbrella of AI-assisted tooling. Copilot is a great example: it listens, offers escalation recommendations, and lets the advocate trigger the next action. But these tools still expect humans to drive the flow, make every decision, and initiate most actions.

**Agentic workflows** reframe this dynamic. In an agentic system, advocates are not micro-managing tools—they are supported by intelligent agents that take initiative, monitor context, and propose actions proactively. The AI is not a sidekick. It's a co-executor of the workflow.

This shift unlocks new goals:

* Reducing decision paralysis
* Automating routine actions
* Surfacing higher-quality signals faster
* Making support feel more fluid, adaptive, and human

The result? Advocates make better decisions, faster. And customers experience fewer hops, clearer answers, and a greater sense of trust.

---

## Designing for Advocate Goals

Designing agentic support begins with clarity around what advocates are trying to accomplish. From our work and observations, four goals stand out consistently:

1. **Clarity of Case** – Understand the context and what the customer needs within seconds of entering the case.
2. **Speed to Signal** – Prioritize the most relevant account details, transaction data, and recent interactions without digging across multiple tools.
3. **Confidence in Action** – Know what actions are available, safe, and likely to help, with low risk of error or duplication.
4. **Momentum Through Flow** – Keep moving forward in the case, even when things are ambiguous, complex, or require escalation.

Agentic design helps advocates meet these goals not by giving them more tools, but by reducing their need to orchestrate everything themselves.

---

## Agent Presence in the Workflow

Where should agents live in the advocate experience? We see two layers of agentic presence emerging:

### 1. **Foundation Layer** – Autonomous Micro-Actions

This layer handles the repetitive, high-frequency tasks advocates should never have to do manually. These include things like:

* Pulling the last five transactions for a Bitcoin customer
* Fetching Know Your Customer (KYC) status and history
* Searching for prior escalations or sentiment patterns

These actions can be triggered ambiently based on case type or agent prompt classification, without requiring advocate input.

### 2. **Acceleration Layer** – Suggestive Flow Guidance

Here, agents act more like flow advisors. They monitor real-time progress and intervene with nudges, summaries, and options. For example:

* "It looks like this customer has had three failed transfers in the past week. Would you like me to draft a proactive refund message?"
* "You're viewing a case flagged as high-risk. I've pulled recent BTC transaction hashes—would you like me to analyze the blockchain entries?"

These interventions appear **inline** in the advocate's workflow, not buried in sidebars or passive tooltips. They operate ambiently—reading context, surfacing next best actions, and asking for approval where needed.

---

## Interface Strategy: Rethinking the Panel Paradigm

Historically, our support tooling has leaned on a three-panel layout: one for the case, one for the customer, and one for AI. This design often reinforces a fragmented experience—forcing advocates to shift focus across verticals to complete even the simplest task.

We've experimented with a two-panel layout in G2 and Grid to tighten focus. But even here, the experience is still **prompt-led**, not **agent-led**. It relies on the user to initiate every interaction.

We propose a **single-panel contextual interface** as the future of agentic support. In this model:

* The advocate sees the case, customer, and AI-generated insight in one unified space.
* A chat input at the bottom lets them message either the customer or the AI, using natural language or commands.
* The agent operates **ambiently**, injecting insights and suggested actions directly into the case flow.

**Example Components to Explore:**

* Ambient Suggestion Cards: e.g., "Possible fraud risk detected, want to review blockchain match?"
* Inline Resolution Preview: shows what the agent would do if approved (e.g., auto-refund, message template, escalation)
* Case Timeline Module: logs agent-initiated actions alongside advocate steps to ensure clarity and trust

This is not just a layout change. It's a shift in who carries the workflow.

---

## Building with Minimum Viable Agents (MVAs)

To bridge the gap between vision and implementation, we introduce the idea of **Minimum Viable Agents**—small, purposeful agents designed to execute scoped tasks that have high utility, clear guardrails, and measurable ROI.

**Examples in Progress:**

* **Recent Transactions Agent**
  When triggered on entry, this agent fetches the last 5 transactions for the customer and classifies them by status. This reduces advocate lookup time by ~30 seconds per case.

* **Blockchain Decoder Agent**
  Given a BTC transaction hash, this agent analyzes the associated ledger activity, flags anomalies, and proposes a fraud escalation path.

* **Customer Risk Summary Agent**
  Summarizes account age, prior blocks, sentiment history, and open tickets into a two-sentence report shown at case start.

Each MVA is evaluated on its ability to reduce case handling time, improve advocate confidence, and align with CSAT improvements.

---

## Design Strategy: Toward an Agentic System

Designing agentic tooling requires more than replacing buttons with bots. It demands new thinking in how information is structured, how decisions are supported, and how agency is shared between human and machine.

Our approach includes:

* **Context-Aware Entry** – Agents should trigger based on metadata like case reason, customer tier, or risk flags.
* **Feedback-Informed Evolution** – Every agent action is logged, scored, and refined using advocate and performance feedback loops.
* **Transparent Execution** – Agents declare what they plan to do, show a preview, and only act when approved (until proven trustworthy).
* **Composable UI** – Agent interventions appear as modules that can be accepted, edited, or dismissed inline—no modal hell, no mystery automation.

We'll begin with a suite of scoped MVAs, measure their impact, and expand as confidence and velocity increase.

---

## Closing Thought

We are not just redesigning support tooling. We are rethinking the relationship between advocates, customers, and automation. Agentic design is not a feature layer. It's a philosophy of **collaborative execution**, where humans don't just command the machine—they **work with it**. 