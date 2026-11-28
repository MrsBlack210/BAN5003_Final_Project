# AI Session Log – Mikayla Esqueda

**Team:** Quant Labs  
**Course:** BAN 5003  
**Project:** Olist Freight Costs Between States  
**Role:** Communications Lead  
**Date:** November 28, 2026  
**AI Tool:** ChatGPT (GPT-6.2)

## 1. Purpose of AI Use

I used ChatGPT to help me understand the Stage 2 assignment requirements, identify my assigned coding section, review the formatting of Step 8, and navigate GitHub. I also used ChatGPT to develop a structured prompt, draft a business recommendation based on our regression results, and proofread my edited recommendation.

I briefly experimented with Claude for rewording, but its response was not used in the final recommendation documented below.

## 2. Coding Assistance

My assigned contribution was Step 8, which translates the regression results into plain-language statements.

The original code came from Brandon's project walkthrough. ChatGPT helped me review the code, remove the unnecessary step() function call, and correct the indentation while keeping the original calculations and variable names.

I inserted the code into finalProject.py, created my individual branch (mikayla-step8), committed my changes, and submitted a pull request for Brandon to review.

## 3. Structured AI Prompt

**Role:** Act as a business analytics consultant for Olist's logistics management team.

**Context:** Our team analyzed 86,825 single-item delivered orders to determine how package weight, volume, and destination state affect freight costs.

Our team's reported regression results are:

- Each additional kilogram adds approximately R$1.66.
- Each additional liter adds approximately R$0.19.
- Rondônia costs approximately R$27.51 more than São Paulo for a comparable package.
- Rondônia, Acre, Paraíba, and Roraima add approximately R$26–R$28 in freight costs.
- The model explains approximately 54% of freight cost variation.
- Acre and Roraima have small sample sizes, making their estimates less certain.

**Task:** Draft a business recommendation identifying which states Olist should prioritize when negotiating discounted shipping rates.

**Constraints:** Use only the provided results. Do not invent statistics, potential savings, or causal relationships. Acknowledge the limitations of the analysis. Refuse to make claims that cannot be supported by the provided data.

**Output format:** One concise, professional business recommendation paragraph written in simple business language.

## 4. Original AI Response

Olist should prioritize Rondônia and Paraíba when negotiating discounted shipping rates, while further evaluating Acre and Roraima due to their smaller sample sizes. These four states have estimated freight costs approximately R$26–R$28 higher than São Paulo for comparable packages. Rondônia is a strong starting point, with an estimated additional freight cost of R$27.51. Package weight and volume should also be considered during negotiations. Although the model explains approximately 54% of freight cost variation, other factors may influence shipping costs. Additional analysis is needed to determine potential savings before implementing discounted shipping rates.

## 5. My Edited Response Before Proofreading

olist should start negotiating discounted shipping rates for Rondonia and paraiba, and take a closer look at acre and romaima before commitingbsince we dont have much data on them. all 4 states cost roughly R$26 to R$28 more to ship to than Sao paulo for a similar package. rondonia is a good place to begin, at about R$27.51 extra. weight and volume matter too, so we should bring them up in the next convo. our model explains about 54% of the cost differences, which mean other things we did not measure are also driving shipping costs up. b4 we lock in any discounts we need more analysis to figure out how much we could actually save.

## 6. Final Recommendation After Proofreading

Olist should start negotiating discounted shipping rates for Rondônia and Paraíba and take a closer look at Acre and Roraima before committing, since we don't have much data on them. All four states cost roughly R$26 to R$28 more to ship to than São Paulo for a similar package. Rondônia is a good place to begin, at about R$27.51 extra. Weight and volume also matter, so they should be considered during negotiations. Our model explains about 54% of the variation in freight costs, which means other factors we did not measure may also influence shipping costs. Before finalizing any discounts, we need further analysis to determine how much Olist could actually save.

## 7. Human Contribution and Edits

I revised the original AI response to make the recommendation more direct and easier to understand. I kept the original numerical findings and emphasized the need for further analysis before making final business decisions.

ChatGPT assisted with correcting spelling, grammar, and wording that suggested an unsupported causal relationship.

For the coding portion, I reviewed the provided Step 8 code, inserted it into the project script, created my branch, committed my changes, and requested a review through GitHub.

## 8. Verification and Limitations

The numerical findings in the recommendation were compared with the results reported in our team's README. ChatGPT was used to communicate the analytical findings, not to generate regression estimates or calculate potential savings.

I reviewed the placement and formatting of my Step 8 code using the GitHub preview before committing my changes. Full execution testing and verification against the completed Python script are still pending.

This document records the structured recommendation prompt, AI response, personal edits, and a summary of my coding assistance. It is not a complete transcript of every AI interaction.
