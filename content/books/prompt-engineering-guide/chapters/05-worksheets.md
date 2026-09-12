# 5. Worksheets and templates for daily workflow integration

Reading about prompt engineering is great, but to truly benefit, you need to practice and make it a habit in your day-to-day work. In this section, we provide some printable worksheets and templates that you can use to plan and evaluate your prompts. These resources are designed to help you systematically approach prompt writing until it becomes second nature. Feel free to print or adapt them to your needs.

## 5.1 Prompt planning worksheet

Often, the key to a good prompt is a bit of planning. Before you rush to ask the AI, take a minute to jot down what you're really looking for. The prompt planning worksheet guides you through the thought process:

**Prompt planning worksheet** – *Use this template to craft effective prompts for any task.*

- **Task/problem:** (What are you trying to accomplish with AI assistance?)
  Example: "Summarize user feedback from our latest survey" or "Brainstorm new onboarding ideas".
- **Goal/desired outcome:** (What does a successful output look like?)
  Example: "I want the top 3 themes users mentioned, in a few bullet points, with maybe a quote each."
  This clarifies your expectations: analysis vs. list vs. narrative, etc.
- **Key context/details to provide:** (What information does the AI need to know?)
  Example: "We surveyed 100 users about our mobile app. They used open-ended responses about what they like or dislike. Also, our app is a task management tool."
- **Preferred format/style:** (Any instructions on how you want the answer?)
  Example: "Bullet points preferred; keep each point short. Casual tone is fine."
  If format is very important (like it needs to be JSON or a table), note that clearly.
- **Draft prompt:** (Now write a first draft of the prompt incorporating the above.)
  Combine role, task, context, style in a single prompt. For example:
  "You are a customer insights analyst. I will provide feedback from users of our task management app. Summarize the top three themes from this feedback and give one user quote example for each theme. Feedback: [paste or describe feedback]."
  This is your first attempt. It's fine if it's rough – you'll refine it next.
- **Review and refine:** (Check your prompt draft against best practices.)
  – Did you specify a role or perspective? (If not, consider adding "As a ...")
  – Is the request clear and specific? (If you see any ambiguous words like "it" or "help", clarify them.)
  – Did you include necessary context? (Imagine you're an outsider, would the prompt make sense?)
  – Did you mention the desired format/style if important?
  Adjust the wording if needed. This might be as simple as adding "List each theme as a bullet" or clarifying what the feedback is about.
- **Final prompt:** (Write the final version that you'll actually use.)
  Sometimes reading it aloud helps ensure it's clear and not overly long. You want it detailed but not convoluted.
- **Results & next steps:** (After running the prompt, note what happened and any adjustments.)
  Example: "Result was pretty good, but the second theme wasn't accurate – maybe I need to provide more context about that. Next time, I'll mention that half the users are new customers, since that might matter."
  This encourages iterative improvement. If the prompt didn't work perfectly, don't fret – note what to change and try again. Over time, these notes will teach you patterns of what works.

You can use this worksheet mentally in a quick minute or literally write it out for complex prompts. It enforces a habit of being intentional with your prompts rather than typing the first thing that comes to mind. Many prompt failures come from skipping those steps – like forgetting to specify what format you wanted and then getting a long paragraph when you actually needed a list.

## 5.2 Daily workflow integration tips

To truly integrate prompt engineering into your daily workflow, consider the following tips (almost like a checklist you can print and pin up):

- **Morning planning with AI:** At the start of your day or week, glance at your to-do list and identify tasks that involve writing, analysis, or idea generation. Ask yourself: "Could an AI prompt help me with this?" For example, if you need to draft a presentation, plan to use a prompt to outline it. If you need to analyze some data or research a topic, plan a prompt to get a summary. By proactively earmarking tasks for AI assistance, you're more likely to actually use it rather than forget.
- **Use a prompt log:** Keep a simple log (could be in a notebook or a document) of prompts you use and how effective they were. This could be as straightforward as two columns: Prompt and Outcome/notes. Over time, you'll build your own reference of what worked in your context. If something was especially useful (like a prompt that perfectly drafted an email), highlight it or reuse it. If a prompt failed, note why and avoid that pattern. This log also serves as evidence of your productivity gains which can be great to share with your team (e.g., "Using ChatGPT, I drafted our release notes in 10 minutes – here's how.").
- **Incorporate prompting in meetings:** Encourage a team culture of using AI for quick answers. For instance, in a planning meeting, someone might wonder "how do other apps do X feature?" Instead of putting it on a research backlog, you could live-prompt an AI (if allowed) for a quick overview. Or after a heated discussion, you might say "Let's ask an AI to summarize these two viewpoints and see if we missed something." Obviously, use this judiciously, but making it a normal tool at hand (just like one might quickly Google something during a meeting) reinforces its presence in daily work.
- **Worksheet for team brainstorms:** If you're running a brainstorming workshop with your team, bring prompt engineering into it. Have a section in the workshop where the team crafts a prompt together to see what an AI suggests. For example, "We've generated our own ideas, now let's see what an AI comes up with. How should we ask the question?" This not only could yield extra ideas, but it trains your team in prompt thinking as well.
- **Prompt templates cheat-sheet:** Create a one-pager (cheat-sheet) of commonly useful prompt formats (similar to the ones in Chapter 4) and keep it near your desk. When you're tired or unsure how to ask, glance at it for inspiration. This cheat-sheet can list structures like "As a [role] do X with Y in Z format." and some examples. Over time you'll internalize them, but the sheet is a great training wheel.
- **Time-box experimentation:** Initially, you might need to try a prompt a few ways to get what you need. That's fine – but time-box it so you don't go down a rabbit hole. For example, "I'll spend 10 minutes with ChatGPT to get a draft of this doc. If it's not useful by then, I'll write it myself." Often, you'll get something good within 1-3 attempts. If not, move on (or ask a colleague for help, which might be quicker in some cases). This keeps your workflow efficient. The good news is, as you practice, your first attempt success rate will go up.

## 5.3 From worksheets to habits

Using a worksheet or template might feel formal at first, but the aim is to train your brain in this new skill. Much like a beginner PM might use a checklist for writing user stories until it becomes natural, you'll use these prompt planning aids until you instinctively include all the needed details in your prompts.

One day you'll realize you don't need to write out a prompt draft on paper – you can jump straight into ChatGPT and phrase it well on the fly. When that day comes, still keep the worksheets around for mentoring others or for particularly high-stakes prompts where a bit of planning helps.

Also, consider sharing the practice with your team. Perhaps have a "Prompt of the week" that you circulate among fellow PMs or product ops folks – where someone shares a cool prompt they used and what it achieved. This creates collective learning. Some organizations even create an internal "prompt book" or repository for different roles (PM, design, engineering, support) to use. As a PM, you can lead by example by championing such knowledge sharing.

In summary, integrating prompt engineering into daily workflow is about making it a *reflex* to think "How can AI assist me here?" and having the tools (in your mind or on paper) to quickly formulate a query that yields value. The worksheets and templates provided are your training gear – use them often, and soon you'll be prompt-engineering on the fly, much to the envy (and eventually curiosity) of those still doing everything the old manual way!
