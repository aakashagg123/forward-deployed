# 9. Examples of effective vs. ineffective prompts

Let's look at some side-by-side examples to drive home the lessons. For each scenario relevant to a product manager, we'll compare an ineffective prompt (one that has issues like vagueness or lack of context) with an effective prompt that addresses those issues. We'll also briefly explain why the effective one works better. Think of this as a "before and after" gallery for prompts.

**Example 1: Brainstorming features**

- Ineffective prompt: "Give me some product ideas."
- Effective prompt: "You are a product manager for a fitness app. Generate 5 new feature ideas to increase user engagement, especially focusing on social or competitive elements (e.g., challenges, community). Provide each idea with a one-sentence description."

*Why the effective prompt works:* The ineffective prompt is extremely broad – product ideas for what? By specifying the domain (fitness app), the goal (increase engagement), and even a hint at the kind of features (social/competitive), the effective prompt guides the AI to relevant, creative suggestions. It also limits to 5 and asks for a one-liner description, ensuring concise, useful output. The result will be far more actionable than a generic list of product ideas which might not even apply to your app.

**Example 2: Writing release notes**

- Ineffective prompt: "Write release notes for our latest update."
- Effective prompt: "Act as a technical writer. Draft the release notes for version 2.3 of our task management app. Include: (1) a brief intro sentence, (2) bullet points of new features (like subtask support, Google Calendar integration), (3) one bullet for 'bug fixes and performance improvements'. Use a professional and upbeat tone, as these notes will be read by end-users."

*Why the effective prompt works:* The ineffective prompt gives no detail about what's in the update, so the AI might make stuff up or be extremely vague ("New features and improvements"). The effective prompt, however, provides specific content to include (so you need to tell the AI what the new features are; it won't know unless you say "like subtask support" etc.), and it defines structure (intro sentence + bullet list) and tone (professional, upbeat). This way, the AI will produce a clean, well-structured draft of release notes that actually reflects the update's content and feels on-brand. Essentially, we avoided the mistake of not providing context, and also avoided asking the AI to know our update magically.

**Example 3: Analyzing survey results**

- Ineffective prompt: "What are people saying about our product in the survey?"
- Effective prompt: "You are a data analyst. Summarize the key themes from our recent user survey about our product. Out of 100 responses, main feedback topics include ease of use, pricing, and support. For each of these three topics, provide a short summary of what users said (e.g., 'many found it easy to use because…, some found it hard because…' etc.). Then list one suggested improvement for each topic."

*Why the effective prompt works:* The ineffective prompt is vague – the model might produce a generic response or latch onto random points. The effective prompt sets the stage (a user survey, topics identified) and asks for a structured summary. It even gently provides the categories (ease of use, pricing, support) to focus on, which likely came from you noticing those in the data – this ensures the AI doesn't digress to less important points. Also, by asking for a suggested improvement per topic, it forces actionable insight, not just repetition of feedback.

**Example 4: Creating a stakeholder update**

- Ineffective prompt: "Update to stakeholders about project status."
- Effective prompt: "Compose a status update for the executive stakeholders about Project Falcon (our new payment feature). Start with a one-line overall status (e.g., On track, At risk, etc.), then in 2 short paragraphs cover: Progress (what's completed recently) and Next Steps (what's coming, any asks). Keep it concise and factual, as this will be an email to VPs."

*Why the effective prompt works:* The ineffective one doesn't specify what the status is, what details to include, or even who the stakeholders are (though implied executives, it's not stated). The effective prompt clearly defines the audience (executives, VPs – meaning it should be high-level), the content structure (progress vs. next steps), and even the desired opener (one-line status). This reduces the chance the AI writes a novel about irrelevant details or uses the wrong tone. The result should be an email-ready status update that you can send with minimal edits.

**Example 5: Prioritization rationale**

- Ineffective prompt: "Which feature is more important?"
- Effective prompt: "We have two proposed features: (A) Real-time collaboration, (B) Advanced analytics dashboard. Provide a brief comparison of these two in terms of user value and implementation effort. Assume real-time collaboration impacts user engagement significantly but is complex to build, while analytics provides moderate value and is easier. Then recommend which to prioritize and explain why, considering a startup context."

*Why the effective prompt works:* The ineffective question is just too bare – important in what sense? The AI would be guessing, maybe it even asks back "Feature A or B in what way?". The effective prompt paints the scenario with given assumptions (so the AI doesn't hallucinate facts), asks for a specific angle of comparison (value vs. effort), and sets a context (a startup, which implies maybe speed is crucial). It then explicitly asks for a recommendation with reasoning. In other words, we gave the AI the criteria to consider and the context for judgment, rather than expecting it to pull criteria out of thin air.

**Example 6: Effective vs. ineffective tone**

- Ineffective prompt (for tone): "Explain the new security policy." (The AI might respond with a very formal, maybe jargon-heavy explanation.)
- Effective prompt (for tone): "Explain the new security policy to the team in simple terms, and make it sound encouraging and not overly strict. For example, use phrases like 'looking out for each other's data safety' rather than 'enforcing rules'. Keep it to one paragraph."

*Why the effective prompt works:* Here the ineffective prompt didn't mention audience or tone, so the AI might default to a dry explanation ("The security policy is as follows... All employees must..."). The effective prompt clearly says: this is for "the team" (implying internal staff, likely non-experts), "simple terms" (no heavy jargon), and even gives a stylistic cue (encouraging, not strict, providing a phrase to emulate). It also bounds length. This demonstrates how instructing on tone and style can transform the result.

**Example 7: Technical info for different audiences**

- Ineffective prompt: "Describe how our encryption works."
- Effective prompt (Scenario 1 – user audience): "Describe how our app's encryption works in layman's terms for a FAQ page. Keep it to 2-3 sentences, focusing on the benefit (protecting user data) rather than technical jargon."
- Effective prompt (Scenario 2 – developer audience): "As a block of technical documentation, describe how our app's encryption works. Include mention of the algorithm (AES-256), key management, and any security protocols, assuming the reader is a software engineer. Aim for 5-6 sentences with technical detail."

*Why the effective prompt works:* The ineffective prompt doesn't specify the audience, so you might get a middle-of-the-road explanation. By tailoring two different effective prompts, you see how the output would diverge appropriately. The first one ensures any user reading the FAQ understands the gist, while the second ensures a developer gets the nitty-gritty. This reinforces the practice of stating the audience and depth needed.

**Example 8: Summarizing vs. elaborating**

- Ineffective prompt: "Tell me about the Q3 sales results."
- Effective prompt (Summary): "Summarize the Q3 sales results of our product in one paragraph, highlighting whether we met targets, and note any key factors (like a major client win or a shortfall in a region). Assume revenue was $5M vs $4M target, and mention that."
- Effective prompt (Detailed report): "Create a detailed summary of the Q3 sales results for our product. Cover: overall revenue vs target (we achieved $5M vs $4M target – above target), key drivers of success (mention the major client win and increased upsells), and any areas of concern (perhaps note slower growth in EU market). Use 4-5 bullet points, and maintain a neutral, factual tone for a management report."

*Why the effective prompt works:* The ineffective one is vague; the AI might give a generic response or ask for clarification. The two effective versions show how you adjust for different depths. In both cases, we provided the crucial data (the AI wouldn't know actual results) and guided it on what analysis to mention. Essentially, the effective prompt did the thinking of "what do I want to see" and articulated that, whereas the ineffective one just punted the question to the AI with no info.

These examples illustrate a few patterns:

- Providing context and specifics turns a generic prompt into a targeted one.
- Specifying format (bullets, paragraph, list, etc.) yields cleaner, easier-to-use outputs.
- Tailoring the prompt with audience and tone prevents misfires in style.
- Breaking down requests or focusing them leads to more depth where you need it, rather than shallow multi-answers.
- Including actual data or assumptions in the prompt stops the AI from guessing (which it might do incorrectly).

By comparing ineffective vs. effective versions, you can viscerally see how a little more upfront clarity in the prompt produces a much better result, often requiring minimal editing. Ineffective prompts often lead to either too generic or off-target outputs, which then cost you time to fix or render the whole exercise moot. Effective prompts, on the other hand, truly harness the AI as a helpful partner that delivers something close to what you'd want if you were doing it yourself, just faster.

As a final tip: whenever you find yourself dissatisfied with an AI's response, consider rewriting your prompt in the style of these effective examples. Usually, the fault (if we can call it that) lies not in the AI's capabilities but in the question it was asked. The good news is, you control that question. Now you have the knowledge to make your questions (prompts) as clear and powerful as possible.
