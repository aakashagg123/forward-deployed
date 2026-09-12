# 4. Prompt templates and frameworks for reusable prompts

In this section, we'll step back and look at the structure of effective prompts – essentially, creating templates that you can reuse across different scenarios. Developing a few go-to prompt frameworks can save you time (no need to reinvent the wheel each time) and ensure consistency in how you interact with AI tools.

## 4.1 Anatomy of an effective prompt

Most powerful prompts share common elements. Here are key "ingredients" of an effective prompt, which you can formulate as a template:

1. **Role or persona assignment:** Set the context by telling the AI who to "be" or from what perspective to respond. This helps tune the style and assumed knowledge. For example: "You are a senior product manager at a fintech startup…" or "Act as a user researcher with 10 years of experience…". By doing this, you instantly shape the AI's tone and expertise. It's similar to how you'd frame a conversation: you'd ask a question differently to an engineer vs. a designer. With AI, you can have it play the specific role you need for the task.
2. **Task definition (clear objective):** State exactly what you want the AI to do. This should be as concise and specific as possible. If it's to generate something, say "Draft a...", "Create a list of...", "Explain...". If it's to analyze, say "Identify X in the following...", "Compare X and Y in terms of Z...". Avoid vague verbs like "help" or "discuss" on their own – clarify help with what or discuss which aspect. For instance, "Generate a list of 5 unique onboarding ideas for a productivity app" is clear about the expected output (a list of 5 ideas). A good practice is to imagine the desired outcome and essentially write that in the prompt (e.g. "I want a list of 5 things, so I literally ask for 5 things").
3. **Relevant details and context:** Provide any information the AI needs to do the task well. This could include background info, data, or constraints. Think of this as feeding the AI the "ingredients" or facts it can use. For example, if asking to write a user story, mention the product or feature so it has context. If analyzing feedback, include a few samples or a summary of what the product is. If you have specific data (like "our conversion rate is X, and industry benchmark is Y"), include that. The AI can only draw from what it knows (its training) plus what you give it in the prompt. So if it's something specific to your company or product, you need to include those details. As one expert put it, "lack of attention to audience requirements and purpose" is a common mistake – in other words, if you don't tell the AI who the audience is or why you need something, it might produce a generic output. Always ask: what does the AI need to know to do this well? – and then provide that in the prompt.
4. **Constraints or style guidelines:** If you have preferences for the format or style of the output, spell them out. Want the answer in bullet points? Say so. Need it in a tabular format? Specify columns. Have a length limit? Mention "in 200 words" or "brief" etc. For tone, you can say "in a casual tone" or "in a formal tone suitable for a press release," etc. The more explicitly you articulate these, the more the output will match your expectation. For example, "Provide the answer as three bullet points" or "Use an encouraging and motivational tone in the response" are easy additions that shape the result. AI models don't take offense at being bossed around – they actually perform better with precise instructions, as shown in OpenAI's own guidelines (e.g., saying how to format the output yields more reliably structured results).
5. **Examples (if needed):** As discussed earlier, giving an example can clarify what you want. This is especially useful if the task is complex or the format is unusual. For example, "Here is an example of the output format I want: [Example]" and then "Now produce the output for this new input: [New input]." This few-shot technique can dramatically improve accuracy for certain tasks (like following a format or extracting specific info). If you have a template or previous good output, you can include a snippet as a guide. However, keep in mind the prompt length – don't overload with too many examples if not necessary.
6. **Prompt primer or next step:** An advanced but nifty trick: sometimes end your prompt with an implicit expectation. For example, instead of ending with a question or nothing, you could end with something like "Answer:" or "Solution:" as a cue. This is called an output primer – by giving the first word or just signaling that the answer should start now, it nudges the AI to format the answer in a certain way. For instance, if I write: "Q: [some question]. A:", the model sees the "A:" and will likely continue in an answer format. Or if I say "The following is a summary of the above text:" at the end of the prompt, it primes the AI to produce a summary. It's a subtle way to guide the style of completion, and can improve reliability.

Putting it all together, a prompt template might look like this:

> "You are a [ROLE] who [ADDITIONAL CONTEXT]. [TASK STATEMENT]. [RELEVANT DETAILS]. [FORMAT/STYLE constraints]."

For example: "You are an experienced UX researcher helping a product manager. Summarize the user feedback below into three key insights and one suggested action per insight. User feedback: [feedback here]. Provide the output in a numbered list. Insight 1: ..., Action: ..."

Notice how that template includes role, task, context (the feedback), and even starts to prime the format ("Insight 1: ..., Action: ..."). This structure can be adapted for many tasks – just slot in the specifics of your scenario.

**Reusable frameworks:** Beyond this generic template, it's useful to have some go-to frameworks you can invoke in prompts. These are especially helpful for analytical tasks. We already saw one: SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) which you can plug into prompts to get a structured strategic analysis. Some other frameworks handy for PMs:

- **MoSCoW prioritization:** Use Must-have, Should-have, Could-have, Won't-have categories for features. E.g., "Using MoSCoW, categorize these feature requests..."
- **Jobs To Be Done (JTBD):** Focus on what job the user is hiring the product for. E.g., "Apply JTBD thinking: what core job is the user trying to accomplish when using our app, and how does each feature help with that?"
- **CARE/STAR for problem-solving:** CARE = Context, Action, Result, Example (or STAR: Situation, Task, Action, Result). You can prompt the AI to answer in that format. E.g., "Using the CARE framework, analyze our recent incident: provide Context of what happened, Actions taken, Results observed, and Examples or evidence to illustrate."
- **RICE scoring:** (Reach, Impact, Confidence, Effort) for prioritization. E.g., "Assess these 3 initiatives with a RICE analysis. Provide scores or rationale for each factor." This requires some data to be meaningful, but the AI can outline how to think about each factor if you supply estimates.

By explicitly naming a framework in the prompt, you guide the AI to organize its response according to that structure. Research has shown this yields more relevant and actionable outputs compared to unguided prompts. For instance, telling the AI to use SWOT might result in a more comprehensive answer than just asking "what do you think about X product vs Y product?" because SWOT forces it to cover multiple angles.

Let's see a quick example of a prompt template using a framework in a PM scenario: Suppose you want to prioritize features. You might prompt:

"You are a product manager helping to prioritize features. I have Feature A, B, C. Evaluate them using the RICE framework (Reach, Impact, Confidence, Effort) and suggest which one should be top priority. Assume: Feature A – reach 10k users, high impact, medium confidence, 3 weeks effort; Feature B – reach 50k, medium impact, low confidence, 6 weeks effort; Feature C – reach 20k, high impact, high confidence, 4 weeks effort. Provide a brief RICE analysis and your recommendation."

The AI would then presumably output a structured analysis, something like:

- Feature A: Reach 10k (score X), Impact high (score Y), Confidence medium, Effort 3 weeks. (It might give a combined score or at least a reasoning).
- Feature B: Reach 50k, Impact medium, Confidence low (riskier), Effort 6 weeks (high effort).
- Feature C: Reach 20k, Impact high, Confidence high, Effort 4 weeks.
- Recommendation: Perhaps Feature C first (because strong impact and confidence outweigh moderate reach), etc.

This is a lot quicker than you manually writing out the pros and cons, and it uses a familiar framework that stakeholders understand.

## 4.2 Specific prompt examples and templates

Let's compile some prompt templates that you can practically reuse. These are inspired by real prompts product managers have found useful. You can consider them "fill-in-the-blank" starters:

- **Idea generation / brainstorming template:**
  "You are a creative [role, e.g., 'growth hacker' or 'innovative PM'] brainstorming ideas for [problem or goal]. Generate [number] ideas for [what], considering [any constraints or context]."

  Example: "You are a creative product manager brainstorming growth ideas for a mobile banking app aimed at Gen Z. Generate 5 ideas to increase daily engagement, considering that we have a limited marketing budget."
  (This would yield a list of ideas, each maybe a sentence or two.)
- **User story / requirement template:**
  "You are a [role] writing a user story for [feature]. Write an agile user story and acceptance criteria for [feature description or goal]. The user story should follow the format: As a ..., I want ..., so that ..."

  Example: "You are a business analyst. Write a user story and 3 acceptance criteria for a feature that allows users to schedule posts on a social media app."
  (Output might be: As a user, I want to schedule a post to publish at a later time, so I can maintain activity even when I'm offline. Acceptance Criteria: 1) User can set date/time... etc.)
- **Email / announcement template:**
  "You are a communications specialist. Draft a [tone: friendly/professional] email to [audience] about [subject]. Include [key points]. Keep it [length]."

  Example: "You are a communications specialist. Draft a professional email to all company employees announcing the launch of our new internal project management tool next Monday. Include why we built it, the go-live date, and a link to the user guide. Keep it under 200 words."
  (The result will be a nicely structured announcement email.)
- **Problem analysis (Five Whys or RCA) template:**
  "You are a problem-solving expert. Analyze [problem description] and suggest possible root causes using a Five Whys approach."

  Example: "You are a problem-solving expert. Analyze why our website's sign-up conversion dropped 30% last week. Use the Five Whys technique to drill down to a potential root cause."
  (This will simulate an analysis: e.g. "Conversion dropped – Why? Fewer visitors clicking sign-up – Why? Landing page load time increased – Why? Recent code change – Why? The new analytics script is slowing it – Why? It's not optimized. Root cause: unoptimized script causing slow load and drop-offs.")
- **Framework-driven analysis template:** (Combining frameworks explicitly)
  "Using the [Framework Name] framework, analyze [situation or question]. [If needed, define what to cover]."

  Example: "Using the SWOT framework, analyze our product's position in the online learning market, focusing on one point each for strengths, weaknesses, opportunities, and threats based on current industry trends."
  (Output will clearly label Strengths, Weaknesses, etc., with relevant points.)
- **Comparison template:**
  "Compare [two or more items] with respect to [criteria]. Provide the output in a structured format (e.g., a table or list)."

  Example: "Compare Feature X and Feature Y of our product in terms of user adoption, customer satisfaction, and technical complexity. Summarize in a bullet list."
  (This yields something like: Feature X – adoption high, satisfaction medium, complexity low; Feature Y – adoption medium, satisfaction high, complexity high, etc.)
- **Plan or strategy template:**
  "You are a strategic planner. Outline a [plan/strategy] to achieve [goal] considering [constraints]. Include steps or phases."

  Example: "You are a strategic planner. Outline a go-to-market strategy to achieve 10,000 users in the first 3 months for a new productivity app, considering we have a limited ad budget and need to leverage viral features."
  (The output might be phased: Pre-launch (do X), Launch (do Y), Post-launch (do Z) with tactics like referral incentives, partnerships, social media campaigns, etc.)
- **Q&A or FAQ generation template:**
  "Generate a FAQ section for [product/feature] covering [topics]. Provide questions and brief answers."

  Example: "Generate a short FAQ for our new passwordless login feature, covering what it is, how to use it, and what to do if it doesn't work."
  (It will list Q: What is passwordless login? A: ...; Q: How do I set it up? A: ... etc.)

These templates illustrate how you can structure prompts for different needs. You'll notice they all explicitly state the role/perspective, the task, and details. Feel free to customize these to your style – you can also create a "cheat sheet" of your favorite prompt structures.

In fact, many practitioners have distilled prompt engineering into a set of best practices like the above. For example, one guide emphasizes: Role and context, clear instructions, and desired format as the triad of a good prompt – which aligns with what we've laid out. They even show how a vague prompt ("Write a blog post about microservices") becomes far more effective when adding those elements ("As a senior software architect... write a post about microservices architecture patterns"). We can apply the same principle to product management topics.

**Tip:** You might worry "do I have to include all these things every time?" Not always. If something is obvious from context or past conversation with the AI, you can omit it. For example, in a ChatGPT session, if you've already set the context that you're talking about your fintech app, you don't need to repeat that in every prompt. But when in doubt, more clarity is better than less.

Also, note that multiple instructions can be given in one prompt; the AI can handle that, especially if you format them clearly (using bullets or newlines for separate instructions). Just ensure they don't conflict.

The ultimate goal with templates is to make prompt writing second nature – eventually, you might not even need to think formally about role or constraints; you'll naturally phrase your requests to AI in a way that hits these points. Until then, you have these frameworks to fall back on and even print out as a reference.
